# My automated tests for the scheduling algorithms. 
# Run this file directly to check: 
# - self-check instance
# - boundary case
# - a tie case
# and that heap and list versions always agree on room count.

import sys
import os

# The test file lives in tests/ but the code lives in src/. This line
# adds src/ to Python's search path so I can import from it even
# though this file isn't inside that folder.
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from session_loader import load_sessions
from heap_scheduler import schedule_rooms_heap
from list_scheduler import schedule_rooms_list
from lower_bound import compute_lower_bound


def test_selfcheck_room_count():
    """The official self-check instance must give exactly 3 rooms."""
    sessions = load_sessions("data/Q1_sessions_selfcheck.csv")
    sorted_sessions = sorted(sessions, key=lambda s: s["start"])

    room_count, _ = schedule_rooms_heap(sorted_sessions)

    # assert checks a condition and CRASHES with an error if it's False.
    # This is exactly what I want in a test: fail loudly if wrong.
    assert room_count == 3, f"Expected 3 rooms, got {room_count}"
    print("PASS: self-check gives 3 rooms")


def test_boundary_case():
    """
    A session ending exactly when another starts must NOT be treated
    as overlapping. Session A: 09:00-10:00, Session B: 10:00-11:00.
    These should fit in ONE room, not two.
    """
    sessions = [
        {"id": "A", "start": 540, "end": 600},   # 09:00-10:00
        {"id": "B", "start": 600, "end": 660},   # 10:00-11:00
    ]
    sorted_sessions = sorted(sessions, key=lambda s: s["start"])

    room_count, assignment = schedule_rooms_heap(sorted_sessions)

    assert room_count == 1, f"Expected 1 room, got {room_count}"
    assert assignment["A"] == assignment["B"], "Boundary sessions should share a room"
    print("PASS: boundary case (touching times) shares one room")


def test_overlap_case():
    """
    Sessions that genuinely overlap (B starts BEFORE A ends) must NOT
    share a room. Session A: 09:00-10:01, Session B: 10:00-11:00.
    """
    sessions = [
        {"id": "A", "start": 540, "end": 601},   # 09:00-10:01
        {"id": "B", "start": 600, "end": 660},   # 10:00-11:00
    ]
    sorted_sessions = sorted(sessions, key=lambda s: s["start"])

    room_count, assignment = schedule_rooms_heap(sorted_sessions)

    assert room_count == 2, f"Expected 2 rooms, got {room_count}"
    assert assignment["A"] != assignment["B"], "Overlapping sessions must NOT share a room"
    print("PASS: genuine overlap uses two separate rooms")


def test_heap_and_list_agree_on_selfcheck():
    """
    Both algorithms must give the SAME room COUNT (not necessarily the
    same room labels; see the earlier discussion on first-fit vs
    earliest-fit behaviour).
    """
    sessions = load_sessions("data/Q1_sessions_selfcheck.csv")
    sorted_sessions = sorted(sessions, key=lambda s: s["start"])

    heap_count, _ = schedule_rooms_heap(sorted_sessions)
    list_count, _ = schedule_rooms_list(sorted_sessions)

    assert heap_count == list_count, (
        f"Heap gave {heap_count} rooms, list gave {list_count}; they must match"
    )
    print("PASS: heap and list agree on room count")


def test_matches_lower_bound():
    """The greedy room count must equal the independently-computed lower bound."""
    sessions = load_sessions("data/Q1_sessions_selfcheck.csv")
    sorted_sessions = sorted(sessions, key=lambda s: s["start"])

    room_count, _ = schedule_rooms_heap(sorted_sessions)
    lower_bound = compute_lower_bound(sessions)

    assert room_count == lower_bound, (
        f"Room count {room_count} does not match lower bound {lower_bound}"
    )
    print("PASS: greedy room count matches the lower bound (optimal)")


if __name__ == "__main__":
    # Run every test function in order. If any assert fails, Python will
    # crash with an AssertionError and print exactly which check failed
    # and why.
    test_selfcheck_room_count()
    test_boundary_case()
    test_overlap_case()
    test_heap_and_list_agree_on_selfcheck()
    test_matches_lower_bound()

    print("\nAll tests passed!")