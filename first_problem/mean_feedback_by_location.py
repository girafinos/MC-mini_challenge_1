import csv
from collections import defaultdict

def mean_columns_by_location(csv_path):

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        rows = list(reader)
        
        result = {}
        
        for column_name in fieldnames:
            if column_name == "time":
                continue
            totals = defaultdict(float)
            counts = defaultdict(int)
            for row in rows:
                location = row.get('location')
                value = row.get(column_name)
                if location is None or value is None:
                    continue

                location = location.strip()
                try:
                    column_value = float(value)
                except ValueError:
                    continue

                totals[location] += column_value
                counts[location] += 1
            
            result[column_name] = {
                loc: totals[loc] / counts[loc]
                for loc in totals
                if counts[loc] > 0
            }
            
        return result


if __name__ == '__main__':
    csv_file = 'mc1-reports-data.csv'
    result = mean_columns_by_location(csv_file)

    for key, value in result.items():
        print(f'Mean {key} by location:')
        for location, mean_column in sorted(value.items(), key=lambda item: int(item[0])):
            print(f'Location {location}: {mean_column:.4f}')
        print()