# Tests for the room-type extension.
#
# The point of these tests is NOT only that the typed greedy works. It is to
# demonstrate that the report's optimality result R = M depends on all rooms
# being interchangeable, and that the assumption fails as soon as rooms have
# types.

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from session_loader import load_sessions
from heap_scheduler import schedule_rooms_heap
from lower_bound import compute_lower_bound, compute_typed_lower_bound
from typed_scheduler import schedule_rooms_typed, optimality_report

# Two room types whose peaks happen at DIFFERENT times.
#   09:00-10:00  two seminars at once  -> needs 2 seminar rooms
#   11:00-12:00  three labs at once    -> needs 3 lab rooms
COUNTEREXAMPLE = [
    {"id": "S1", "start": 540, "end": 600, "room_type": "seminar"},
    {"id": "S2", "start": 540, "end": 600, "room_type": "seminar"},
    {"id": "L1", "start": 660, "end": 720, "room_type": "lab"},
    {"id": "L2", "start": 660, "end": 720, "room_type": "lab"},
    {"id": "L3", "start": 660, "end": 720, "room_type": "lab"},
]


def test_typed_lower_bound_separates_peaks():
    """
    The typed lower bound must add up the per-type peaks (2 + 3 = 5) rather
    than take the single biggest one (3).
    """
    assert compute_typed_lower_bound(COUNTEREXAMPLE) == 5, \
        f"Expected typed lower bound 5, got {compute_typed_lower_bound(COUNTEREXAMPLE)}"
    print("PASS: typed lower bound adds per-type peaks (2 + 3 = 5)")


def test_overall_peak_overlap_undercounts():
    """
    Overall peak overlap is only 3, because the three labs at 11:00 are the
    busiest single instant. It is a valid lower bound but a weak one.
    """
    assert compute_lower_bound(COUNTEREXAMPLE) == 3, \
        f"Expected overall peak overlap 3, got {compute_lower_bound(COUNTEREXAMPLE)}"
    print("PASS: overall peak overlap is 3, strictly below the typed bound of 5")


def test_R_equals_M_breaks_with_types():
    """
    The report proves R = M. On this instance greedy needs 5 rooms while the
    overall peak overlap M is only 3, so R = M is FALSE. This is the
    assumption in the proof failing, not a bug in the algorithm.
    """
    report = optimality_report(COUNTEREXAMPLE)

    assert report["greedy_rooms"] == 5, \
        f"Expected 5 rooms, got {report['greedy_rooms']}"
    assert report["greedy_rooms"] != report["peak_overlap"], \
        "R = M was expected to FAIL on this instance"

    print(f"PASS: R = M breaks on typed input (R={report['greedy_rooms']}, "
          f"M={report['peak_overlap']})")


def test_typed_greedy_still_optimal_against_typed_bound():
    """
    The important result: adding room types does NOT make the problem harder.
    R = M still holds, as long as M is the right M, namely the typed one.
    """
    report = optimality_report(COUNTEREXAMPLE)

    assert report["greedy_rooms"] == report["typed_lower_bound"], \
        f"Greedy used {report['greedy_rooms']} rooms but the typed lower bound is " \
        f"{report['typed_lower_bound']}"

    print("PASS: typed greedy is still optimal, against the typed lower bound")


def test_untyped_instances_are_unaffected():
    """
    Adding the extension must not change anything when rooms are
    interchangeable. On the supplied 40 sessions, and on the self-check
    instance, typed and untyped must agree.
    """
    for path, expected in [("data/Q1_sessions_main.csv", 10),
                           ("data/Q1_sessions_selfcheck.csv", 3)]:
        sessions = load_sessions(path)
        sorted_sessions = sorted(sessions, key=lambda s: s["start"])

        untyped_rooms, _ = schedule_rooms_heap(sorted_sessions)
        typed_rooms, _, _ = schedule_rooms_typed(sorted_sessions)

        assert untyped_rooms == typed_rooms == expected, (
            f"{path}: untyped={untyped_rooms}, typed={typed_rooms}, expected={expected}"
        )
        assert compute_typed_lower_bound(sessions) == compute_lower_bound(sessions), (
            f"{path}: the two lower bounds should agree when rooms are interchangeable"
        )

    print("PASS: untyped instances give identical results under both schedulers")


def test_typed_greedy_never_reuses_a_wrong_type_room():
    """
    A lab-only session must never be placed in a room opened for a seminar,
    even when that seminar room happens to be free at the time.
    """
    sessions = [
        # Seminar room opened at 09:00, free from 10:00 onwards.
        {"id": "S1", "start": 540, "end": 600, "room_type": "seminar"},
        # Lab session at 11:00. The seminar room is free then, but is the
        # wrong type, so a new lab room must be opened.
        {"id": "L1", "start": 660, "end": 720, "room_type": "lab"},
    ]

    sorted_sessions = sorted(sessions, key=lambda s: s["start"])
    room_count, assignment, rooms_by_type = schedule_rooms_typed(sorted_sessions)

    assert room_count == 2, f"Expected 2 rooms, got {room_count}"
    assert assignment["S1"] != assignment["L1"], \
        "A lab session was placed in a seminar room"
    assert rooms_by_type == {"seminar": 1, "lab": 1}, rooms_by_type

    print("PASS: typed greedy never reuses a room of the wrong type")


if __name__ == "__main__":
    test_typed_lower_bound_separates_peaks()
    test_overall_peak_overlap_undercounts()
    test_R_equals_M_breaks_with_types()
    test_typed_greedy_still_optimal_against_typed_bound()
    test_untyped_instances_are_unaffected()
    test_typed_greedy_never_reuses_a_wrong_type_room()

    print("\nAll typed-scheduler tests passed!")