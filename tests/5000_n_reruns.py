# This runs the fixed-rooms family at n=5000 several times to get a median
# ratio across separate runs, not just the median of 5 taken within one run
# which measure.py already does.
#
# The point of this file is to check the ratio is STABLE. The families are
# generated from a fixed seed now, so every repeat below rebuilds exactly the
# same instance and the ratio should barely move. If it does, something has
# broken reproducibility.

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from generators import generate_fixed_rooms
from heap_scheduler import schedule_rooms_heap
from list_scheduler import schedule_rooms_list
from measure import warm_up, measure_median

num_repeats = 5
ratios = []

for repeat in range(num_repeats):
    sessions = generate_fixed_rooms(5000, num_rooms=5)
    sorted_sessions = sorted(sessions, key=lambda s: s["start"])

    # warm_up takes the GENERATOR FUNCTION, not the sessions, so it can build
    # its own small fixed-size throwaway input. Passing sorted_sessions here
    # would try to call the list and fail with
    # "TypeError: 'list' object is not callable".
    warm_up(schedule_rooms_heap, generate_fixed_rooms, num_rooms=5)
    warm_up(schedule_rooms_list, generate_fixed_rooms, num_rooms=5)

    heap_time, _ = measure_median(schedule_rooms_heap, sorted_sessions)
    list_time, _ = measure_median(schedule_rooms_list, sorted_sessions)

    ratio = list_time / heap_time
    ratios.append(ratio)

    print(f"Run {repeat + 1}: heap={heap_time*1000:.3f} ms, "
          f"list={list_time*1000:.3f} ms, ratio={ratio:.3f}")

import statistics
print(f"\nMedian ratio across {num_repeats} runs: {statistics.median(ratios):.3f}")