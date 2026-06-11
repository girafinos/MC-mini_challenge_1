import csv
from collections import defaultdict

COLUMNS = ["sewer_and_water", "power", "roads_and_bridges", "medical", "buildings",
            "shake_intensity", "location"]

FEEDBACK = "shake_intensity"

def mean_column_by_location(csv_path, feedback=FEEDBACK):
    totals = defaultdict(float)
    counts = defaultdict(int)

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            location = row.get('location')
            column = row.get(feedback)
            if location is None or column is None:
                continue

            location = location.strip()
            try:
                column_value = float(column)
            except ValueError:
                continue

            totals[location] += column_value
            counts[location] += 1

    return {
        loc: totals[loc] / counts[loc]
        for loc in totals
        if counts[loc] > 0
    }


if __name__ == '__main__':
    csv_file = 'mc1-reports-data.csv'
    result = mean_column_by_location(csv_file)

    print(f'Mean {FEEDBACK} by location:')
    for location, mean_power in sorted(result.items(), key=lambda item: item[0]):
        print(f'Location {location}: {mean_power:.4f}')