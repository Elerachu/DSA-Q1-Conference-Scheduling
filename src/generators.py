# Creates test session data for timing experiments with no CSV needed,
# these functions return session dicts directly, in the same format
# load_sessions() produces (a list of {"id", "start", "end"} dicts).

import random

# A fixed seed, so every experiment in this project is reproducible.
#
# Python seeds `random` from the operating system's entropy pool, so without
# this each run draws DIFFERENT durations. That does not change the room
# counts (they are fixed by the family design) but it does change how many
# rooms the list baseline has to scan, and therefore changes list_ops. That
# made the committed operation counts impossible to reproduce. Seeding means
# re-running measure.py gives the same instance every time.
DEFAULT_SEED = 20260927


def _rng(seed=None):
    """
    Returns a random generator seeded from DEFAULT_SEED unless a seed is
    passed explicitly.

    A private generator is used rather than the module-level `random` on
    purpose: it means the seed travels with this one call, so a test or a
    re-run gets the same instance no matter what any other code has done to
    the global `random` state beforehand, and no global state is left behind
    for the next caller.
    """
    return random.Random(DEFAULT_SEED if seed is None else seed)


def generate_high_overlap(n, day_length=1440, seed=None):
    """
    Family 1: room count grows with n.

    Every session starts at time 0 and has a random, long-ish duration.
    Since they all start at the exact same instant, they ALL overlap each
    other at time 0, the peak overlap (and therefore the room count)
    is always exactly n, no matter how big n gets.
    """
    sessions = []
    rng = _rng(seed)

    for i in range(n):
        start = 0
        # A seeded duration; so sessions don't all end at the exact same
        # time either keeping things realistic, doesn't change the overlap
        # count.
        duration = rng.randint(30, day_length)
        end = start + duration

        sessions.append({
            "id": f"H{i}",   # "H" for "high overlap" plus a number
            "start": start,
            "end": end,
        })

    return sessions


def generate_fixed_rooms(n, num_rooms, min_duration=30, max_duration=90, seed=None):
    """
    Family 2: room count stays FIXED at num_rooms, however large n gets.

    Sessions are split into num_rooms separate "tracks". Within one track,
    sessions run back-to-back with no overlap at all; each new session on
    that track starts exactly when the previous one on that track ends.
    Since only num_rooms tracks exist, at most num_rooms sessions can ever
    be happening at the same moment regardless of how many sessions total
    are generated.
    """
    sessions = []
    rng = _rng(seed)

    # One "current end time" tracked per track/room.
    track_end_times = [0] * num_rooms

    for i in range(n):
        # Session 0 goes to track 0, session 1 to track 1, etc.
        # and wraps back around (the % operator does the wrapping).
        track = i % num_rooms

        start = track_end_times[track]
        duration = rng.randint(min_duration, max_duration)
        end = start + duration

        sessions.append({
            "id": f"F{i}",   # "F" for "fixed rooms", plus a number
            "start": start,
            "end": end,
        })

        # This track is now busy until `end` and the next session placed on this track will start from here.
        track_end_times[track] = end

    return sessions


if __name__ == "__main__":
    from lower_bound import compute_lower_bound
    from heap_scheduler import schedule_rooms_heap

    for n in [10, 100, 1000]:
        high_overlap_sessions = generate_high_overlap(n)
        sorted_sessions = sorted(high_overlap_sessions, key=lambda s: s["start"])
        room_count, _ = schedule_rooms_heap(sorted_sessions)
        bound = compute_lower_bound(high_overlap_sessions)
        print(f"[high overlap] n={n}: rooms={room_count}, lower_bound={bound}")

    print()

    for n in [10, 100, 1000]:
        fixed_sessions = generate_fixed_rooms(n, num_rooms=5)
        sorted_sessions = sorted(fixed_sessions, key=lambda s: s["start"])
        room_count, _ = schedule_rooms_heap(sorted_sessions)
        bound = compute_lower_bound(fixed_sessions)
        print(f"[fixed rooms] n={n}: rooms={room_count}, lower_bound={bound}")