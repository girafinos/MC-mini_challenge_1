import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from mean_feedback_by_location import mean_columns_by_location

# ── Dados de dano por categoria (média por distrito) ──────────────────────────
# Valores carregados dinamicamente do CSV por local.
COLUMN_MAP = {
    "agua_esgoto": "sewer_and_water",
    "energia": "power",
    "vias_pontes": "roads_and_bridges",
    "saude": "medical",
    "edificios": "buildings",
}


def load_dados_from_csv(csv_path):
    means = mean_columns_by_location(csv_path)
    dados = {}

    for loc in range(1, 20):
        loc_str = str(loc)
        dados[loc] = {
            label: means.get(csv_col, {}).get(loc_str, np.nan)
            for label, csv_col in COLUMN_MAP.items()
        }

    return dados

csv_file = os.path.join(os.path.dirname(__file__), "mc1-reports-data.csv")
dados = load_dados_from_csv(csv_file)

# ── Pontuação composta: média simples das 5 categorias ────────────────────────
compostos = {
    loc: np.mean(list(cats.values()))
    for loc, cats in dados.items()
}

# Ordena do maior para o menor
compostos_ord = sorted(compostos.items(), key=lambda x: x[1], reverse=True)
locais  = [f"Local {loc}" for loc, _ in compostos_ord]
scores  = [score for _, score in compostos_ord]

# ── Cores por nível de prioridade ─────────────────────────────────────────────
def cor_barra(rank):
    if rank < 3:   return "#A32D2D"   # crítico
    if rank < 7:   return "#BA7517"   # alto
    if rank < 12:  return "#185FA5"   # moderado
    return             "#888780"      # menor

cores = [cor_barra(i) for i in range(len(scores))]

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 8))
fig.patch.set_facecolor("#F9F8F6")
ax.set_facecolor("#F9F8F6")

barras = ax.barh(locais, scores, color=cores, height=0.65, zorder=3)

# Rótulos de valor ao final de cada barra
for barra, score in zip(barras, scores):
    ax.text(
        barra.get_width() + 0.08,
        barra.get_y() + barra.get_height() / 2,
        f"{score:.2f}",
        va="center", ha="left",
        fontsize=9.5, color="#444",
    )

# Linha de referência em 5.0
ax.axvline(5.0, color="#BBBBBB", linewidth=1, linestyle="--", zorder=2, label="Média neutra (5,0)")

# Eixos e limites
ax.set_xlim(0, 11)
ax.set_xlabel("Média de dano composto (0–10)", fontsize=11, labelpad=8, color="#444")
ax.set_title(
    "Prioridade de resposta por distrito\n"
    "Pontuação composta = média das 5 categorias de dano",
    fontsize=13, fontweight="bold", color="#222", pad=14
)
ax.invert_yaxis()   # maior pontuação no topo
ax.tick_params(axis="y", labelsize=10, colors="#333")
ax.tick_params(axis="x", labelsize=9,  colors="#666")
ax.set_axisbelow(True)
ax.xaxis.grid(True, color="#DDDDDD", linewidth=0.8)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.spines["bottom"].set_color("#CCCCCC")

# Legenda de cores
legendas = [
    mpatches.Patch(color="#A32D2D", label="Prioridade crítica (top 3)"),
    mpatches.Patch(color="#BA7517", label="Alta prioridade"),
    mpatches.Patch(color="#185FA5", label="Prioridade moderada"),
    mpatches.Patch(color="#888780", label="Prioridade menor"),
]
ax.legend(
    handles=legendas,
    loc="lower right",
    fontsize=9,
    framealpha=0.85,
    edgecolor="#CCCCCC",
)

plt.tight_layout()
plt.savefig("figures/damage_priority_chart.png", dpi=150, bbox_inches="tight")
plt.show()
print("Gráfico salvo em: damage_priority_chart.png")