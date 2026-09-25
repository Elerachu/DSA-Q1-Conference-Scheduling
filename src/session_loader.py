# Shared by both schedulers; one place that knows how to read the CSV.

import csv
from time_utilities import time_to_minutes


def load_sessions(filepath):
    """
    Reads a CSV file of sessions and returns a list of dictionaries,
    one per session, with start and end converted to minutes.
    """
    sessions = []

    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            start = time_to_minutes(row["start"].strip())
            end = time_to_minutes(row["end"].strip())

            # A bad row that slips through could throw off the room count with no clue why.
            if start >= end:
                raise ValueError(
                    f"Session {row['session_id']} has start >= end "
                    f"({row['start']} -> {row['end']})"
                )

            sessions.append({
                "id": row["session_id"],
                "start": start,
                "end": end,
            })

    return sessions