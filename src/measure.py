# Times both scheduler implementations on inputs of growing size, across
# both instance families following the four rules from the brief:
# - warm up first
# - repeat
# - report a median
# - count operations as milliseconds 
# and time only the part that differs not the shared sort.

import time
import statistics

from generators import generate_high_overlap, generate_fixed_rooms
from heap_scheduler import schedule_rooms_heap
from list_scheduler import schedule_rooms_list


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


def warm_up(schedule_function, sorted_sessions, num_warmup_runs=300):
    """
    Runs the scheduler many times on throwaway input BEFORE the real
    timed runs. Java, C#, and JavaScript-style JIT compilers speed up
    after repeated use and Python's interpreter doesn't JIT the same way,
    but warming up still helps stabilise caching effects; I followed
    the brief's instruction.
    """
    for _ in range(num_warmup_runs):
        schedule_function(sorted_sessions, None)


def run_experiment(instance_family_name, generator_function, sizes):
    """
    For one instance family (e.g. "high overlap"), runs both schedulers
    across a list of sizes n, and returns a list of result rows.
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

        # Warm up both algorithms before timing either of them.
        warm_up(schedule_rooms_heap, sorted_sessions)
        warm_up(schedule_rooms_list, sorted_sessions)

        heap_time, heap_ops = measure_median(schedule_rooms_heap, sorted_sessions)
        list_time, list_ops = measure_median(schedule_rooms_list, sorted_sessions)

        results.append({
            "family": instance_family_name,
            "n": n,
            "heap_time": heap_time,
            "heap_ops": heap_ops,
            "list_time": list_time,
            "list_ops": list_ops,
        })

        print(f"[{instance_family_name}] n={n:5d} | "
              f"heap: {heap_time*1000:.3f} ms, {heap_ops} ops | "
              f"list: {list_time*1000:.3f} ms, {list_ops} ops")

    return results


if __name__ == "__main__":
    import csv

    sizes = [10, 50, 100, 500, 1000, 2000]
    fixed_rooms_sizes = [10, 50, 100, 500, 1000, 2000, 5000]

    print("=== High overlap family (room count grows with n) ===")
    high_overlap_results = run_experiment("high overlap", generate_high_overlap, sizes)

    print()
    print("=== Fixed rooms family (room count stays at 5) ===")
    fixed_rooms_results = run_experiment("fixed rooms", generate_fixed_rooms, fixed_rooms_sizes)

    # Save everything to a CSV so the numbers survive after this terminal closes
    all_results = high_overlap_results + fixed_rooms_results

    with open("results/measurements.csv", "w", newline="") as f:
        fieldnames = ["family", "n", "heap_time", "heap_ops", "list_time", "list_ops"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)

    print("\nSaved results to results/measurements.csv")