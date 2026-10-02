# Q1: Rooms for a Multi-Track Event

DSA final project, COMS-RW-20515. Greedy room scheduling using a min-heap,
compared against a list-scan baseline.

## Python version

Developed and tested on Python 3.13.

## Setup

1. Create and activate a virtual environment

   ```powershell
   python -m venv venv
   venv\Scripts\Activate.ps1        # Windows PowerShell
   ```

   ```bash
   source venv/bin/activate          # macOS or Linux
   ```

2. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

## How to run

Run all commands from the project root folder.

Run the automated tests (self-check, boundary, overlap, heap/list agreement, optimality):

```bash
python tests/selfcheck_test.py
```

Run the heap scheduler on the main dataset:

```bash
python src/heap_scheduler.py data/Q1_sessions_main.csv
```

Run the list scheduler baseline on the main dataset:

```bash
python src/list_scheduler.py data/Q1_sessions_main.csv
```

Check optimality against the independent lower bound:

```bash
python src/lower_bound.py data/Q1_sessions_main.csv
```

Generate instances and check optimality holds at various sizes:

```bash
python src/generators.py
```

Run the full timing and operation count comparison (takes 1 to 2 minutes).
This also measures the supplied 40-session dataset and writes every row to
`results/measurements.csv`:

```bash
python src/measure.py
```

Check that the fixed-rooms ratio is stable across five separate runs:

```bash
python tests/5000_n_reruns.py
```

Run the room-type extension tests:

```bash
python tests/typed_test.py
```

See the counterexample where `R = M` stops holding, on its own:

```bash
python src/typed_scheduler.py
```

Generate the time vs n plots (run `measure.py` first). Requires matplotlib,
see `requirements.txt`:

```bash
python src/plot_results.py
```

## Files

### Source

- `src/time_utilities.py` — converts `HH:MM` strings to minutes.
- `src/session_loader.py` — shared CSV loading, used by both schedulers and
  the lower bound check, so there is exactly one copy of the loading and
  validation rules.
- `src/heap_scheduler.py` — min-heap greedy algorithm, O(n log n).
- `src/list_scheduler.py` — list-scan baseline, O(n x r).
- `src/lower_bound.py` — independent max-overlap check used to confirm
  optimality, plus `compute_typed_lower_bound` for the room-type extension.
- `src/typed_scheduler.py` — room-type extension: one min-heap per room type.
- `src/generators.py` — generates the two families of test instances from a
  fixed seed so results are reproducible.
- `src/measure.py` — timing, operation count and room count comparison.
- `src/plot_results.py` — produces the time vs n plots.

### Tests

- `tests/selfcheck_test.py` — automated tests: self-check, boundary, genuine
  overlap, heap/list agreement, optimality against the lower bound.
- `tests/5000_n_reruns.py` — repeats the fixed-rooms n=5000 measurement five
  times to show the ratio is stable and reproducible.
- `tests/typed_test.py` — room-type extension, including the counterexample
  where the optimality result `R = M` fails.

## Room-type extension

`src/typed_scheduler.py` adds required room types. Each session may carry a
`room_type` key, and the algorithm keeps one min-heap per type, so a room of the
wrong type is never treated as free.

The interesting result is what happens to the optimality proof. The report
proves `R = M`, where `M` is the maximum number of sessions running at any
single instant. That equality depends on all rooms being interchangeable. It
fails as soon as rooms have types:

| Time | Running | Needs |
|---|---|---|
| 09:00–10:00 | 2 seminars | 2 seminar rooms |
| 11:00–12:00 | 3 labs | 3 lab rooms |

The overall peak overlap `M` is 3 (three labs at 11:00), but 5 rooms are
actually needed, because the two seminar rooms are busy at 09:00 and idle at
11:00, so they cannot be reused for the labs. So `R = M` becomes `R = 5` and
`M = 3`.

Overall peak overlap is still a valid lower bound, just a weak one. The bound
that greedy actually attains once rooms have types is the sum over room types
of the peak overlap within that type, which is `2 + 3 = 5` here. Greedy remains
optimal against that bound, and stays O(n log n).

### Data

- `data/Q1_sessions_main.csv` — the 40 supplied sessions.
- `data/Q1_sessions_selfcheck.csv` — 8 sessions that must resolve to 3 rooms.

### Results

- `results/measurements.csv` — raw timing, operation count, room count and
  lower bound data for the supplied dataset and both generated families.
- `results/plot_high_overlap.png` — time vs n where the room count grows with n.
- `results/plot_fixed_rooms.png` — time vs n where the room count stays fixed.

## Reproducibility

`src/generators.py` generates its instances from a fixed seed,
`DEFAULT_SEED = 20260927`, declared at the top of that file. Without a fixed
seed, Python draws durations from the operating system's entropy pool on every
run, which changes how many rooms the list baseline has to scan and therefore
changes the operation counts from run to run.

Each row of `results/measurements.csv` also records `heap_rooms`,
`list_rooms` and `lower_bound`, so the optimality claim (greedy rooms = maximum
overlap) and the claim that both algorithms agree on the room count can be
checked directly against the data rather than taken on trust.

## Notes on the two implementations

Both apply the same greedy rule; they differ only in the data structure used to
find a free room. The heap always picks the earliest-finishing room in
O(log n). The list baseline scans rooms in index order and stops at the first
free one it meets, costing O(r) per session, so it can produce different
room-by-room assignments on the same input even though both agree on the total
number of rooms.

Both use `<=` rather than `<` when testing whether a room is free, so a session
ending at 10:00 and one starting at 10:00 correctly share a room.