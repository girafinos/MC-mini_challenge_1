import csv
from collections import defaultdict
import numpy as np
from heatmap_feedback import save_heatmap
import matplotlib.pyplot as plt

def stats_by_location(csv_path):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        rows = list(reader)

    values = defaultdict(lambda: defaultdict(list))

    for row in rows:
        location = row.get('location')
        if location is None:
            continue
        location = location.strip()
        for column_name in fieldnames:
            if column_name in ("time", "location"):
                continue
            v = row.get(column_name)
            if v is None or v == "":
                continue
            try:
                fv = float(v)
            except ValueError:
                continue
            values[column_name][location].append(fv)

    std_result = {}
    count_result = {}
    cv_result = {}
    mean_result = {}

    for column_name, loc_dict in values.items():
        std_result[column_name] = {}
        count_result[column_name] = {}
        cv_result[column_name] = {}
        mean_result[column_name] = {}
        for loc, vals in loc_dict.items():
            arr = np.array(vals)
            mean = arr.mean()
            std = arr.std()
            std_result[column_name][loc] = std
            count_result[column_name][loc] = len(arr)
            mean_result[column_name][loc] = mean
            cv_result[column_name][loc] = (std / mean) if mean != 0 else np.nan

    return std_result, count_result, cv_result, mean_result


def convert_array_pos_into_matrix_pos(location):
    return (location // 4, location % 4)


def to_matrix(d):
    m = np.full((5, 4), np.nan)
    for loc, val in sorted(d.items(), key=lambda x: int(x[0])):
        i, j = convert_array_pos_into_matrix_pos(int(loc) - 1)
        m[i][j] = val
    return m


if __name__ == '__main__':
    csv_file = 'mc1-reports-data.csv'
    std_result, count_result, cv_result, mean_result = stats_by_location(csv_file)

    columns = ['sewer_and_water', 'power', 'roads_and_bridges', 'medical', 'buildings']

    # ---- Heatmaps de Desvio Padrão (1 por categoria) ----
    for column in columns:
        matrix = to_matrix(std_result[column])
        print(f"--- Std Dev: {column} ---")
        for loc, val in sorted(std_result[column].items(), key=lambda x: int(x[0])):
            print(f"Location {loc}: {val:.4f}")
        print()
        save_heatmap(f"desviopadrao_{column}", matrix)
        plt.clf()

    # ---- Heatmap de Contagem de Relatórios ----
    count_matrix = to_matrix(count_result['sewer_and_water'])
    print("--- Report Count ---")
    for loc, val in sorted(count_result['sewer_and_water'].items(), key=lambda x: int(x[0])):
        print(f"Location {loc}: {val}")
    print()

    plt.imshow(count_matrix, aspect='auto', cmap='viridis')
    plt.title("Número de relatos por região")
    plt.colorbar()
    plt.axis('off')
    for i, row in enumerate(count_matrix):
        for j, value in enumerate(row):
            if np.isnan(value):
                continue
            plt.text(j, i, f"{int(value)}", ha='center', va='center', fontsize=12)
            plt.text(j, i - 0.35, f"Área: {(i*4+j)+1}", ha='center', va='center',
                     fontsize=6, color=(1, 1, 1, 1), fontweight='bold')
    plt.savefig('figures/contagem_de_relatos.png', dpi=300, bbox_inches='tight')
    plt.clf()

    # ---- Heatmap de Contagem de Relatórios - categoria medical ----
    medical_count_matrix = to_matrix(count_result['medical'])
    print("--- Report Count (medical) ---")
    for loc, val in sorted(count_result['medical'].items(), key=lambda x: int(x[0])):
        print(f"Location {loc}: {val}")
    print()

    plt.imshow(medical_count_matrix, aspect='auto', cmap='viridis')
    plt.title("Número de relatos - categoria Medical")
    plt.colorbar()
    plt.axis('off')
    for i, row in enumerate(medical_count_matrix):
        for j, value in enumerate(row):
            if np.isnan(value):
                continue
            plt.text(j, i, f"{int(value)}", ha='center', va='center', fontsize=12)
            plt.text(j, i - 0.35, f"Área: {(i*4+j)+1}", ha='center', va='center',
                     fontsize=6, color=(1, 1, 1, 1), fontweight='bold')
    plt.savefig('figures/contagem_de_relatos_medical.png', dpi=300, bbox_inches='tight')
    plt.clf()

    # ---- Heatmap de Coeficiente de Variação médio (CV = std/mean) ----
    cv_avg = defaultdict(list)
    for column in columns:
        for loc, val in cv_result[column].items():
            if not np.isnan(val):
                cv_avg[loc].append(val)
    cv_avg_mean = {loc: np.mean(vals) for loc, vals in cv_avg.items()}
    cv_matrix = to_matrix(cv_avg_mean)

    print("--- Avg Coefficient of Variation (across 5 categories) ---")
    for loc, val in sorted(cv_avg_mean.items(), key=lambda x: int(x[0])):
        print(f"Location {loc}: {val:.4f}")

    plt.imshow(cv_matrix, aspect='auto', cmap='RdYlGn_r', vmin=0)
    plt.title("Média coeficiente de variação")
    plt.colorbar()
    plt.axis('off')
    for i, row in enumerate(cv_matrix):
        for j, value in enumerate(row):
            if np.isnan(value):
                continue
            plt.text(j, i, f"{value:.3f}", ha='center', va='center', fontsize=12)
            plt.text(j, i - 0.35, f"Área: {(i*4+j)+1}", ha='center', va='center',
                     fontsize=6, color=(1, 1, 1, 1), fontweight='bold')
    plt.savefig('figures/media_cv.png', dpi=300, bbox_inches='tight')
    plt.clf()

    # ---- Std médio entre categorias (score de confiabilidade) ----
    std_avg = defaultdict(list)
    for column in columns:
        for loc, val in std_result[column].items():
            std_avg[loc].append(val)
    std_avg_mean = {loc: np.mean(vals) for loc, vals in std_avg.items()}
    std_matrix = to_matrix(std_avg_mean)

    print()
    print("--- Avg Std Dev (across 5 categories) ---")
    for loc, val in sorted(std_avg_mean.items(), key=lambda x: int(x[0])):
        print(f"Location {loc}: {val:.4f}")

    plt.imshow(std_matrix, aspect='auto', cmap='RdYlGn_r', vmin=0)
    plt.title("Média das 5 categorias por região")
    plt.colorbar()
    plt.axis('off')
    for i, row in enumerate(std_matrix):
        for j, value in enumerate(row):
            if np.isnan(value):
                continue
            plt.text(j, i, f"{value:.3f}", ha='center', va='center', fontsize=12)
            plt.text(j, i - 0.35, f"Área: {(i*4+j)+1}", ha='center', va='center',
                     fontsize=6, color=(0, 0, 0, 1), fontweight='bold')
    plt.savefig('figures/media_desviopadrao.png', dpi=300, bbox_inches='tight')
    plt.clf()