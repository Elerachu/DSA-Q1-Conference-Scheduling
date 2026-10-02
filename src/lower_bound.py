# Computes the maximum number of sessions overlapping at any single moment.
# This is a LOWER BOUND on the number of rooms needed

from session_loader import load_sessions


def compute_lower_bound(sessions):
    """
    Returns the maximum number of sessions running at the same time,
    computed independently of the greedy scheduling algorithms.
    """
    events = []  # will hold (time, +1 or -1) pairs

    for session in sessions:
        events.append((session["start"], 1))    # a session starting: +1 overlap
        events.append((session["end"], -1))      # a session ending: -1 overlap

    # Sort by time. If a start and an end happen at the SAME time, the end
    # must be processed FIRST (a session ending at 10:00 frees the room for one
    # starting at 10:00, so they never count as overlapping).
    events.sort(key=lambda e: (e[0], e[1]))

    current_overlap = 0
    max_overlap = 0

    for time, change in events:
        current_overlap += change
        max_overlap = max(max_overlap, current_overlap)

    return max_overlap


def compute_typed_lower_bound(sessions):
    """
    The lower bound that stays correct once rooms have TYPES.

    Split the sessions by required room type and find the peak overlap WITHIN
    each type, then add them up. A room of the wrong type is not a free room,
    so the peaks of different types cannot share.

    On an instance where every room is interchangeable this gives the same
    answer as compute_lower_bound. On a typed instance it can be strictly
    larger, and it is the bound greedy actually attains.
    """
    sessions_by_type = {}

    for session in sessions:
        room_type = session.get("room_type", "general")
        sessions_by_type.setdefault(room_type, []).append(session)

    return sum(compute_lower_bound(group) for group in sessions_by_type.values())


if __name__ == "__main__":
    import sys
    from heap_scheduler import schedule_rooms_heap

    if len(sys.argv) < 2:
        print("Usage: python src/lower_bound.py data/Q1_sessions_selfcheck.csv")
    else:
        filepath = sys.argv[1]
        sessions = load_sessions(filepath)
        sorted_sessions = sorted(sessions, key=lambda s: s["start"])

        lower_bound = compute_lower_bound(sessions)
        greedy_room_count, _ = schedule_rooms_heap(sorted_sessions)

        print(f"Lower bound (maximum overlap): {lower_bound}")
        print(f"Greedy room count: {greedy_room_count}")

        if lower_bound == greedy_room_count:
            print("This is a MATCH: greedy is optimal on this instance.")
        else:
            print("This is a MISMATCH: something is wrong.")