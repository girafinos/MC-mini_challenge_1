import csv
import os
import math
from datetime import datetime
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt

# ── Configurações ──────────────────────────────────────────────────────────────
CSV_PATH   = "../mc1-reports-data.csv"
OUTPUT_DIR = "figures"
TIME_FMT   = "%Y-%m-%d %H:%M:%S"
WINDOW_H   = 6   # janela de agrupamento em horas

METRICS = ["sewer_and_water", "power", "roads_and_bridges",
           "medical", "buildings", "shake_intensity"]

LOCATIONS = [str(i) for i in range(1, 20)]

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ── Leitura ────────────────────────────────────────────────────────────────────
records = []
with open(CSV_PATH, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        try:
            t = datetime.strptime(row["time"].strip(), TIME_FMT)
        except ValueError:
            continue
        entry = {"time": t, "location": row.get("location", "").strip()}
        for m in METRICS:
            raw = row.get(m, "").strip()
            entry[m] = float(raw) if raw else None
        records.append(entry)


# ── Agrupamento em janelas de WINDOW_H horas ──────────────────────────────────
def to_bucket(dt):
    return dt.replace(hour=(dt.hour // WINDOW_H) * WINDOW_H,
                      minute=0, second=0, microsecond=0)

# buckets[bucket] = {metric: [valores]}
buckets = defaultdict(lambda: defaultdict(list))
for r in records:
    b = to_bucket(r["time"])
    for m in METRICS:
        if r[m] is not None:
            buckets[b][m].append(r[m])

times = sorted(buckets.keys())

def avg(lst): return sum(lst) / len(lst) if lst else float("nan")
def std(lst):
    if len(lst) < 2: return float("nan")
    m = avg(lst)
    return math.sqrt(sum((v - m)**2 for v in lst) / (len(lst) - 1))


# ── Pico de reportes (momento do terremoto) ───────────────────────────────────
# Identificado diretamente dos dados: maior volume de reportes por janela
count_per_bucket = {b: max(len(buckets[b][m]) for m in METRICS) for b in times}
QUAKE_TIME = max(count_per_bucket, key=count_per_bucket.get)
print(f"Pico de reportes detectado em: {QUAKE_TIME}  ({count_per_bucket[QUAKE_TIME]} reportes)")


# ── Matrizes para os heatmaps (linhas=bairros, colunas=janelas de tempo) ──────
# mean_matrix[m][i][j] = média da métrica m, bairro i, janela j
mean_matrix = {
    m: np.array([
        [avg(buckets[t].get(m, [])) if loc in [r["location"] for r in records
             if to_bucket(r["time"]) == t] else float("nan")
         for t in times]
        for loc in LOCATIONS
    ])
    for m in METRICS
}

# Mais eficiente: agrupar por (bucket, location) de uma vez
loc_buckets = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
for r in records:
    b = to_bucket(r["time"])
    for m in METRICS:
        if r[m] is not None:
            loc_buckets[b][r["location"]][m].append(r[m])

mean_mat = {m: np.full((len(LOCATIONS), len(times)), float("nan")) for m in METRICS}
std_mat  = {m: np.full((len(LOCATIONS), len(times)), float("nan")) for m in METRICS}

for j, t in enumerate(times):
    for i, loc in enumerate(LOCATIONS):
        for m in METRICS:
            vals = loc_buckets[t][loc][m]
            if vals:
                mean_mat[m][i][j] = avg(vals)
                std_mat[m][i][j]  = std(vals)

# Eixo X: labels das janelas
x_labels = [t.strftime("%d/%m\n%Hh") for t in times]
y_labels = [f"Loc {l}" for l in LOCATIONS]


# ── Heatmap (segue o padrão do heatmap_feedback.py) ───────────────────────────
def save_heatmap(title, matriz, filename, x_labels, y_labels, quake_col=None):
    fig, ax = plt.subplots(figsize=(max(14, len(times) * 0.7), 7))

    im = ax.imshow(matriz, aspect="auto", cmap="coolwarm", vmin=0, vmax=10)
    plt.colorbar(im, ax=ax)
    ax.set_title(title)

    # Anotações em cada célula
    for i in range(matriz.shape[0]):
        for j in range(matriz.shape[1]):
            v = matriz[i][j]
            if np.isnan(v):
                continue
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    fontsize=6, color=(74/255, 37/255, 11/255, 1.0))

    # Linha vertical marcando o pico (terremoto)
    if quake_col is not None:
        ax.axvline(quake_col - 0.5, color="red", linewidth=2,
                   linestyle="--", label="Pico de reportes")
        ax.legend(loc="upper right", fontsize=8)

    ax.set_xticks(range(len(x_labels)))
    ax.set_xticklabels(x_labels, fontsize=7, rotation=45, ha="right")
    ax.set_yticks(range(len(y_labels)))
    ax.set_yticklabels(y_labels, fontsize=8)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  -> {filename} salva")

quake_col = times.index(QUAKE_TIME)


# ── Figura 1: Heatmap de média por métrica × bairro × tempo ──────────────────
# Uma figura por métrica (igual ao padrão da Q1 de vocês)
print("Gerando heatmaps de média por métrica...")
for m in METRICS:
    save_heatmap(
        title=f"Média — {m}  (janelas de {WINDOW_H}h)",
        matriz=mean_mat[m],
        filename=f"mean_{m}.png",
        x_labels=x_labels,
        y_labels=y_labels,
        quake_col=quake_col,
    )


# ── Figura 2: Heatmap de desvio padrão (incerteza) por métrica ────────────────
print("Gerando heatmaps de incerteza (std) por métrica...")
for m in METRICS:
    im_std = std_mat[m].copy()
    # std não tem escala 0–10; normalizar visualmente para 0–5
    fig, ax = plt.subplots(figsize=(max(14, len(times) * 0.7), 7))
    im = ax.imshow(im_std, aspect="auto", cmap="coolwarm",
                   vmin=0, vmax=np.nanmax(im_std))
    plt.colorbar(im, ax=ax, label="Desvio Padrão")
    ax.set_title(f"Incerteza (std) — {m}  (janelas de {WINDOW_H}h)")

    for i in range(im_std.shape[0]):
        for j in range(im_std.shape[1]):
            v = im_std[i][j]
            if np.isnan(v): continue
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    fontsize=6, color=(74/255, 37/255, 11/255, 1.0))

    ax.axvline(quake_col - 0.5, color="red", linewidth=2,
               linestyle="--", label="Pico de reportes")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_xticks(range(len(x_labels)))
    ax.set_xticklabels(x_labels, fontsize=7, rotation=45, ha="right")
    ax.set_yticks(range(len(y_labels)))
    ax.set_yticklabels(y_labels, fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f"std_{m}.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  -> std_{m}.png salva")

print("\nConcluído! Figuras em:", OUTPUT_DIR)