import csv
from collections import defaultdict
import numpy as np
from heatmap_feedback import save_heatmap
import matplotlib.pyplot as plt

def mean_columns_by_location(csv_path):

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        rows = list(reader)
        
        result = {}
        
        for column_name in fieldnames:
            if column_name == "time" or column_name == "location":
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

def convert_array_pos_into_matrix_pos(location):
    return (location // 4, location % 4)

if __name__ == '__main__':
    csv_file = 'mc1-reports-data.csv'
    result = mean_columns_by_location(csv_file)

    heat_dict = {}
    for column_name, value in result.items():
        heat_matrix = np.full((5, 4), np.nan)
        print(f'Mean {column_name} by location:')
        for location, mean_column in sorted(value.items(), key=lambda item: int(item[0])):
            print(f'Location {location}: {mean_column:.4f}')
            
            i, j = convert_array_pos_into_matrix_pos(int(location)-1)
            heat_matrix[i][j] = mean_column
        print()
        heat_dict[column_name] = heat_matrix
        
    for column, matrix in heat_dict.items():
        save_heatmap(column, matrix, heat_dict["shake_intensity"])
        plt.clf()