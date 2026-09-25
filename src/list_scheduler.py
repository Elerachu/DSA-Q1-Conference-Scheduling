# Baseline algorithm: same greedy rule as heap_scheduler.py but tracks
# room finish times in a plain list instead of a min-heap.

from session_loader import load_sessions


def schedule_rooms_list(sorted_sessions, operation_counter=None):
    room_finish_times = []
    session_room_assignment = {}
    room_count = 0

    for session in sorted_sessions:
        free_room_index = None

        for index, finish_time in enumerate(room_finish_times):
            # Count every room checked whether or not it turns out to be free 
            # This is the "scan cost" the O(n x r) bound the brief refers to.
            if operation_counter is not None:
                operation_counter[0] += 1

            if finish_time <= session["start"]:
                free_room_index = index
                break

        if free_room_index is not None:
            room_finish_times[free_room_index] = session["end"]
            room_number = free_room_index + 1
        else:
            room_finish_times.append(session["end"])
            room_count += 1
            room_number = room_count

        session_room_assignment[session["id"]] = room_number

    return room_count, session_room_assignment


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python src/list_scheduler.py data/Q1_sessions_selfcheck.csv")
    else:
        filepath = sys.argv[1]
        sessions = load_sessions(filepath)
        sorted_sessions = sorted(sessions, key=lambda s: s["start"])

        room_count, session_room_assignment = schedule_rooms_list(sorted_sessions)

        print(f"Room count: {room_count}")
        print(f"Assigned sessions and corresponding rooms: {session_room_assignment}")