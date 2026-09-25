# Q1: Rooms for a Multi-Track Event

DSA final project (COMS-RW-20515) — greedy room scheduling using a min-heap,
compared against a list-scan baseline.

## How to run

1. Install dependencies:
   pip install -r requirements.txt

2. Run the self-check (must report 3 rooms):
   python tests/test_selfcheck.py

3. Run on the main dataset:
   python src/scheduler_heap.py data/Q1_sessions_main.csv

## Files

- src/time_utils.py      — converts "HH:MM" strings to minutes
- src/scheduler_heap.py  — min-heap greedy algorithm, O(n log n)
- src/scheduler_list.py  — list-scan baseline, O(n x r)
- src/lower_bound.py     — independent max-overlap check for optimality
- src/generators.py      — generates test instances of varying size
- src/measure.py         — timing and operation-count comparison

## Data

- data/Q1_sessions_main.csv       — 40 supplied sessions
- data/Q1_sessions_selfcheck.csv  — 8 sessions, must resolve to 3 rooms