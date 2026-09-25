# The Algorithm: Assign conference sessions to the fewest possible rooms using a min-heap to always check the room that frees up soonest.

import csv        
import heapq        # built-in module for min-heap operations

from time_utilities import time_to_minutes

def load_sessions(filepath):
    """
    Reads a CSV file of sessions and returns a list of dictionaries,
    one per session with start and end converted to minutes.
    """
    sessions = []  # List with one dict per session

    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            start = time_to_minutes(row["start"].strip())
            end = time_to_minutes(row["end"].strip())

            # Guard against malformed data: a session must take positive time. 
            # My optimality proof assumes this is true and if it isn't true, the proof and the algorithm can't be trusted.
            if start >= end:

            # A bad row that slips through could throw off the room count with no clue why
            # So I raise an exception with a clear message instead of silently ignoring it.
                raise ValueError(
                    f"Session {row['session_id']} has start >= end "
                    f"({row['start']} -> {row['end']})"
                )

            sessions.append({
                "id": row["session_id"],
                "start": start,
                "end": end,
            })

    return sessions


def schedule_rooms_heap(sorted_sessions, operation_counter=None):
    room_heap = []
    session_room_assignment = {}
    room_count = 0

    for session in sorted_sessions:
        if room_heap and room_heap[0][0] <= session["start"]:
            finish_time, room_number = heapq.heappop(room_heap)
        else:
            room_count += 1
            room_number = room_count

        heapq.heappush(room_heap, (session["end"], room_number))

        # Count one "push" per session and this is what I can directly observe. 
        if operation_counter is not None:
            operation_counter[0] += 1

        session_room_assignment[session["id"]] = room_number

    return room_count, session_room_assignment


# Only runs when this file is executed directly and not when it is imported.
if __name__ == "__main__":
    import sys  # reads command-line arguments

    # sys.argv is a list of command-line arguments.
    if len(sys.argv) < 2:
        print("Usage: python src/heap_scheduler.py data/Q1_sessions_selfcheck.csv")
    else:
        filepath = sys.argv[1]
        sessions = load_sessions(filepath)

        # Sorting is now a separate step; useful for timing the heap algorithm and list algorithm 
        # separately from the sort they both share.

        sorted_sessions = sorted(sessions, key=lambda s: s["start"])

        room_count, session_room_assignment = schedule_rooms_heap(sorted_sessions)

        print(f"Room count: {room_count}")
        print(f"Assigned sessions and corresponding rooms: {session_room_assignment}")