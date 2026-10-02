# Extension: rooms have TYPES, and a session can only go in a compatible room.
#
# This is the "if you finish early" extension from the question sheet. It also
# shows WHERE the optimality proof in the report stops working: the proof of
# R = M relies on all rooms being interchangeable, and that assumption turns
# out to be load-bearing.
#
# Each session may carry a "room_type" key. Sessions without one are treated as
# type "general".

import heapq

from lower_bound import compute_lower_bound, compute_typed_lower_bound


def schedule_rooms_typed(sorted_sessions, operation_counter=None):
    """
    Same greedy rule as schedule_rooms_heap, but with ONE MIN-HEAP PER ROOM
    TYPE instead of one heap for every room.

    When a session arrives we only look at the heap for its own type. If the
    earliest-finishing room of that type is free we reuse it, otherwise we open
    a new room of that type. Opening a room of a different type never counts as
    a free room, which is the whole point.

    Returns (total_room_count, assignment, rooms_by_type).
    """
    # type -> min-heap of (last session end time in that room, room number)
    heaps_by_type = {}

    session_room_assignment = {}
    rooms_by_type = {}
    room_count = 0

    for session in sorted_sessions:
        room_type = session.get("room_type", "general")

        room_heap = heaps_by_type.setdefault(room_type, [])

        if room_heap and room_heap[0][0] <= session["start"]:
            finish_time, room_number = heapq.heappop(room_heap)
        else:
            room_count += 1
            room_number = room_count
            rooms_by_type[room_type] = rooms_by_type.get(room_type, 0) + 1

        heapq.heappush(room_heap, (session["end"], room_number))

        if operation_counter is not None:
            operation_counter[0] += 1

        session_room_assignment[session["id"]] = room_number

    return room_count, session_room_assignment, rooms_by_type


def optimality_report(sessions):
    """
    Returns a dict comparing the two different lower bounds for a TYPED
    instance:

    - peak_overlap: the maximum number of sessions running at ANY instant,
      ignoring type. This is the lower bound used in the report.
    - typed_lower_bound: the sum over room types of the peak overlap within
      that type. This is the correct lower bound once rooms have types.

    On untyped instances the two are equal. On typed instances the first can be
    strictly smaller, which is exactly why R = M stops holding.
    """
    sorted_sessions = sorted(sessions, key=lambda s: s["start"])

    greedy_rooms, _, _ = schedule_rooms_typed(sorted_sessions)

    return {
        "greedy_rooms": greedy_rooms,
        "peak_overlap": compute_lower_bound(sessions),
        "typed_lower_bound": compute_typed_lower_bound(sessions),
    }


if __name__ == "__main__":
    # The counterexample: two room types whose peaks happen at DIFFERENT times.
    #
    #   09:00-10:00  two seminars at once   -> needs 2 seminar rooms
    #   11:00-12:00  three labs at once     -> needs 3 lab rooms
    #
    # Overall peak overlap is 3 (three labs at 11:00). But 5 rooms are needed,
    # because the two seminar rooms are busy at 09:00 and idle at 11:00, so
    # they cannot be reused for the labs.
    counterexample = [
        {"id": "S1", "start": 540, "end": 600, "room_type": "seminar"},
        {"id": "S2", "start": 540, "end": 600, "room_type": "seminar"},
        {"id": "L1", "start": 660, "end": 720, "room_type": "lab"},
        {"id": "L2", "start": 660, "end": 720, "room_type": "lab"},
        {"id": "L3", "start": 660, "end": 720, "room_type": "lab"},
    ]

    report = optimality_report(counterexample)

    print("Typed instance: 2 seminar rooms needed at 09:00, 3 lab rooms at 11:00")
    print(f"  Greedy (typed) rooms used : {report['greedy_rooms']}")
    print(f"  Overall peak overlap (M)  : {report['peak_overlap']}")
    print(f"  Typed lower bound         : {report['typed_lower_bound']}")
    print()
    if report["greedy_rooms"] == report["typed_lower_bound"]:
        print("MATCH: greedy is still optimal, but against the TYPED lower bound.")
    else:
        print("MISMATCH: something is wrong.")
    if report["greedy_rooms"] != report["peak_overlap"]:
        print("NOTE: greedy rooms != overall peak overlap, so R = M no longer holds.")