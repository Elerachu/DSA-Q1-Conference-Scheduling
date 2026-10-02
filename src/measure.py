# Times both scheduler implementations on inputs of growing size, across
# both instance families following the four rules from the brief:
# - warm up first
# - repeat
# - report a median
# - count operations as milliseconds
# and time only the part that differs not the shared sort.
#
# Also measures the SUPPLIED 40-session dataset, and records the greedy room
# count and the independently computed lower bound for every row, so the
# optimality claim (R = M) and the heap/list agreement claim are backed by the
# data in this file rather than only asserted in the report.

import time
import statistics
import csv

from generators import generate_high_overlap, generate_fixed_rooms, DEFAULT_SEED
from heap_scheduler import schedule_rooms_heap
from list_scheduler import schedule_rooms_list
from session_loader import load_sessions
from lower_bound import compute_lower_bound


def time_one_run(schedule_function, sorted_sessions):
    """
    Runs one scheduler once, returns (elapsed_seconds, operation_count).
    Only the scheduling step is timed and sorting already happened before
    this function is called, it's never included in the measurement.
    """
    operation_counter = [0]

    start_clock = time.perf_counter()
    schedule_function(sorted_sessions, operation_counter)
    end_clock = time.perf_counter()

    elapsed_seconds = end_clock - start_clock
    return elapsed_seconds, operation_counter[0]


def measure_median(schedule_function, sorted_sessions, num_runs=5):
    """
    Runs the scheduler num_runs times and returns the MEDIAN time and
    operation count, not the mean; a median ignores one-off garbage
    collection pauses that would otherwise skew an average.
    """
    times = []
    operation_counts = []

    for _ in range(num_runs):
        elapsed, ops = time_one_run(schedule_function, sorted_sessions)
        times.append(elapsed)
        operation_counts.append(ops)

    median_time = statistics.median(times)
    median_ops = statistics.median(operation_counts)
    return median_time, median_ops


def warm_up(schedule_function, generator_function, num_warmup_runs=300, **gen_kwargs):
    """
    Runs the scheduler many times on a small, fixed-size throwaway input
    BEFORE the real timed runs. CPython has no JIT compiler, so this
    doesn't recompile hot loops the way Java, C# or JavaScript runtimes
    do; it still guards against other first-use costs (module/attribute
    lookups settling, CPU frequency scaling). Crucially, the throwaway
    input here is always small (n=50) regardless of the n being measured,
    since warming up on the actual large input being timed would make the
    warm-up itself take as long as or longer than the measurement.
    """
    warmup_sessions = generator_function(50, **gen_kwargs)
    warmup_sorted = sorted(warmup_sessions, key=lambda s: s["start"])
    for _ in range(num_warmup_runs):
        schedule_function(warmup_sorted, None)


def optimality_check(sessions):
    """
    Returns (heap_rooms, list_rooms, lower_bound) for one instance.

    This is deliberately NOT timed. The point is to record, for every row of
    results/measurements.csv, that the greedy room count equals the greedy
    room count from the other algorithm AND equals the independently computed
    maximum overlap. If any of these ever disagreed, the row would show it.
    """
    sorted_sessions = sorted(sessions, key=lambda s: s["start"])
    heap_rooms, _ = schedule_rooms_heap(sorted_sessions)
    list_rooms, _ = schedule_rooms_list(sorted_sessions)
    return heap_rooms, list_rooms, compute_lower_bound(sessions)


def run_experiment(instance_family_name, generator_function, sizes):
    """
    For one instance family e.g. "high overlap" runs both schedulers
    across a list of sizes n and returns a list of result rows.
    """
    results = []

    for n in sizes:
        # Build the raw sessions once, then sort ONCE
        # This sorted list is reused for both algorithms; the sort itself is never
        # counted inside either algorithm's timed measurement.
        if instance_family_name == "high overlap":
            sessions = generator_function(n)
        else:
            sessions = generator_function(n, num_rooms=5)

        sorted_sessions = sorted(sessions, key=lambda s: s["start"])

        # Warm up both algorithms before timing either of them, always on
        # a small fixed-size input, never on the n being measured.
        if instance_family_name == "high overlap":
            warm_up(schedule_rooms_heap, generator_function)
            warm_up(schedule_rooms_list, generator_function)
        else:
            warm_up(schedule_rooms_heap, generator_function, num_rooms=5)
            warm_up(schedule_rooms_list, generator_function, num_rooms=5)

        heap_time, heap_ops = measure_median(schedule_rooms_heap, sorted_sessions)
        list_time, list_ops = measure_median(schedule_rooms_list, sorted_sessions)

        heap_rooms, list_rooms, lower_bound = optimality_check(sessions)

        results.append({
            "family": instance_family_name,
            "n": n,
            "heap_time": heap_time,
            "heap_ops": heap_ops,
            "list_time": list_time,
            "list_ops": list_ops,
            "heap_rooms": heap_rooms,
            "list_rooms": list_rooms,
            "lower_bound": lower_bound,
            "seed": DEFAULT_SEED,
        })

        agreement = "OK" if heap_rooms == list_rooms == lower_bound else "MISMATCH!"
        print(f"[{instance_family_name}] n={n:5d} | "
              f"heap: {heap_time*1000:.3f} ms, {heap_ops} ops | "
              f"list: {list_time*1000:.3f} ms, {list_ops} ops | "
              f"rooms={heap_rooms}/{list_rooms}, lower_bound={lower_bound} [{agreement}]")

    return results


def measure_supplied_data(csv_path="data/Q1_sessions_main.csv"):
    """
    Measures both schedulers on the SUPPLIED dataset, which is the instance
    the marker will actually run, rather than only on generated inputs.

    The same warm-up, repeat and median rules are applied so these timings are
    directly comparable with the generated families.
    """
    sessions = load_sessions(csv_path)
    sorted_sessions = sorted(sessions, key=lambda s: s["start"])
    n = len(sessions)

    # Warm up on a small generated throwaway input, same as the other
    # families, so the supplied-data timings aren't the first calls the
    # interpreter ever sees.
    warm_up(schedule_rooms_heap, generate_high_overlap)
    warm_up(schedule_rooms_list, generate_high_overlap)

    heap_time, heap_ops = measure_median(schedule_rooms_heap, sorted_sessions)
    list_time, list_ops = measure_median(schedule_rooms_list, sorted_sessions)

    heap_rooms, list_rooms, lower_bound = optimality_check(sessions)

    agreement = "OK" if heap_rooms == list_rooms == lower_bound else "MISMATCH!"
    print(f"[supplied data] {csv_path} n={n:5d} | "
          f"heap: {heap_time*1000:.3f} ms, {heap_ops} ops | "
          f"list: {list_time*1000:.3f} ms, {list_ops} ops | "
          f"rooms={heap_rooms}/{list_rooms}, lower_bound={lower_bound} [{agreement}]")

    return {
        "family": "supplied data",
        "n": n,
        "heap_time": heap_time,
        "heap_ops": heap_ops,
        "list_time": list_time,
        "list_ops": list_ops,
        "heap_rooms": heap_rooms,
        "list_rooms": list_rooms,
        "lower_bound": lower_bound,
        "seed": "n/a (supplied data, not generated)",
    }


if __name__ == "__main__":
    sizes = [10, 50, 100, 500, 1000, 2000, 5000]
    fixed_rooms_sizes = [10, 50, 100, 500, 1000, 2000, 5000]

    print(f"Generated families use fixed seed {DEFAULT_SEED}, so this run is "
          f"reproducible.")
    print()

    print("=== Supplied data ===")
    supplied_results = measure_supplied_data()

    print()
    print("=== High overlap family (room count grows with n) ===")
    high_overlap_results = run_experiment("high overlap", generate_high_overlap, sizes)

    print()
    print("=== Fixed rooms family (room count stays at 5) ===")
    fixed_rooms_results = run_experiment("fixed rooms", generate_fixed_rooms, fixed_rooms_sizes)

    # Save everything to a CSV so the numbers survive after this terminal closes.
    # plot_results.py only plots the two generated family names, so the
    # "supplied data" row is ignored by the plots and doesn't disturb them.
    all_results = [supplied_results] + high_overlap_results + fixed_rooms_results

    with open("results/measurements.csv", "w", newline="") as f:
        fieldnames = ["family", "n", "heap_time", "heap_ops", "list_time", "list_ops",
                      "heap_rooms", "list_rooms", "lower_bound", "seed"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)

    print("\nSaved results to results/measurements.csv")