# Reads results/measurements.csv and produces the time-vs-n plots
# the brief asks for saved as image files in results/.

import csv
import matplotlib.pyplot as plt


def load_results(filepath):
    """Reads the CSV back into a list of dicts, converting numbers properly."""
    results = []
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append({
                "family": row["family"],
                "n": int(row["n"]),
                "heap_time": float(row["heap_time"]),
                "heap_ops": int(row["heap_ops"]),
                "list_time": float(row["list_time"]),
                "list_ops": int(row["list_ops"]),
            })
    return results


def plot_family(results, family_name, output_filename):
    """
    Makes one time-vs-n plot for a single family, showing both
    algorithms on the same axes so they're directly comparable.
    """
    # Keep only rows belonging to this family.
    family_rows = [r for r in results if r["family"] == family_name]

    n_values = [r["n"] for r in family_rows]
    # Convert seconds to milliseconds for readability on the plot.
    heap_times_ms = [r["heap_time"] * 1000 for r in family_rows]
    list_times_ms = [r["list_time"] * 1000 for r in family_rows]

    plt.figure()
    plt.plot(n_values, heap_times_ms, marker="o", label="Heap (min-heap)")
    plt.plot(n_values, list_times_ms, marker="o", label="List (baseline)")

    plt.xlabel("Number of sessions (n)")
    plt.ylabel("Time (milliseconds)")
    plt.title(f"Running time vs n — {family_name}")
    plt.legend()
    plt.grid(True)

    plt.savefig(output_filename)
    print(f"Saved {output_filename}")
    plt.close()


if __name__ == "__main__":
    results = load_results("results/measurements.csv")

    plot_family(results, "high overlap", "results/plot_high_overlap.png")
    plot_family(results, "fixed rooms", "results/plot_fixed_rooms.png")