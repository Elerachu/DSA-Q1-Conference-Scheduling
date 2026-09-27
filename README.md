### Q1: Rooms for a Multi-Track Event

DSA final project COMS-RW-20515. Greedy room scheduling using a min-heap compared against a list-scan baseline.

Python version

Developed and tested on Python 3.13.

Setup

1. Create and activate a virtual environment

   python -m venv venv

   venv\Scripts\Activate.ps1 (Windows PowerShell)

   source venv/bin/activate (macOS or Linux)

2. Install dependencies

   pip install -r requirements.txt

How to run

Run all commands from the project root folder.

Run the automated tests self-check boundary overlap agreement optimality

python tests/selfcheck_test.py

Run the heap scheduler on the main dataset

python src/heap_scheduler.py data/Q1_sessions_main.csv

Run the list scheduler baseline on the main dataset

python src/list_scheduler.py data/Q1_sessions_main.csv

Check optimality against the independent lower bound

python src/lower_bound.py data/Q1_sessions_main.csv

Generate instances and check optimality holds at various sizes

python src/generators.py

Run the full timing and operation count comparison takes 1 to 2 minutes

## Results
Q1: Rooms for a Multi-Track Event

DSA final project COMS-RW-20515. Greedy room scheduling using a min-heap compared against a list-scan baseline.

Python version

Developed and tested on Python 3.13.

Setup

1. Create and activate a virtual environment

   python -m venv venv

   venv\Scripts\Activate.ps1 (Windows PowerShell)

   source venv/bin/activate (macOS or Linux)

2. Install dependencies

   pip install -r requirements.txt

How to run

Run all commands from the project root folder.

Run the automated tests self-check boundary overlap agreement optimality

python tests/selfcheck_test.py

Run the heap scheduler on the main dataset

python src/heap_scheduler.py data/Q1_sessions_main.csv

Run the list scheduler baseline on the main dataset

python src/list_scheduler.py data/Q1_sessions_main.csv

Check optimality against the independent lower bound

python src/lower_bound.py data/Q1_sessions_main.csv

Generate instances and check optimality holds at various sizes

python src/generators.py

Run the full timing and operation count comparison takes 1 to 2 minutes

python src/measure.py

Generate the time vs n plots run measure.py first

Requires matplotlib see requirements.txt

python src/plot_results.py

Files

src/time_utilities.py converts HH:MM strings to minutes

src/session_loader.py shared CSV loading used by both schedulers

src/heap_scheduler.py min-heap greedy algorithm O(n log n)

src/list_scheduler.py list-scan baseline O(n x r)

src/lower_bound.py independent max-overlap check for optimality

src/generators.py generates two families of test instances

src/measure.py timing and operation count comparison

src/plot_results.py produces the time vs n plots

tests/selfcheck_test.py automated tests self-check boundary tie heap-list agreement optimality

Data

data/Q1_sessions_main.csv 40 supplied sessions

data/Q1_sessions_selfcheck.csv 8 sessions must resolve to 3 rooms

Results

results/measurements.csv raw timing and operation count data

results/plot_high_overlap.png time vs n room count grows with n capped at n = 2000 see report limitations

results/plot_fixed_rooms.png time vs n room count stays fixed up to n = 5000
- results/measurements.csv       — raw timing and operation-count data
- results/plot_high_overlap.png  — time vs n, room count grows with n
- results/plot_fixed_rooms.png   — time vs n, room count stays fixed
