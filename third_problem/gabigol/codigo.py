import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ==============================
# CONFIGURAÇÕES
# ==============================

ARQUIVO = "/mc1-reports-data.csv"
PASTA_SAIDA = "graficos"

os.makedirs(PASTA_SAIDA, exist_ok=True)

# ==============================
# LEITURA DOS DADOS
# ==============================

df = pd.read_csv(ARQUIVO)

# Converter tempo
df['time'] = pd.to_datetime(df['time'])

# Ordenar
df = df.sort_values('time')

# ==============================
# AGRUPAMENTO TEMPORAL
# ==============================

df_agg = df.resample('1H', on='time').mean()
df_std = df.resample('1H', on='time').std()

# ==============================
# 1. SÉRIE TEMPORAL (INFRAESTRUTURA)
# ==============================

plt.figure(figsize=(12,6))
colunas = ['sewer_and_water','power','roads_and_bridges','medical','buildings']

for col in colunas:
    if col in df_agg.columns:
        plt.plot(df_agg.index, df_agg[col], label=col)

plt.title("Infrastructure Conditions Over Time")
plt.legend()
plt.tight_layout()
plt.savefig(f"{PASTA_SAIDA}/1_infrastructure_timeseries.png")
plt.close()

# ==============================
# 2. SHAKE INTENSITY
# ==============================

if 'shake_intensity' in df_agg.columns:
    plt.figure(figsize=(10,4))
    plt.plot(df_agg.index, df_agg['shake_intensity'])
    plt.title("Shake Intensity Over Time")
    plt.tight_layout()
    plt.savefig(f"{PASTA_SAIDA}/2_shake_intensity.png")
    plt.close()

# ==============================
# 3. INCERTEZA (MÉDIA + DESVIO)
# ==============================

if 'power' in df_agg.columns:
    plt.figure(figsize=(10,5))
    
    media = df_agg['power']
    std = df_std['power']

    plt.plot(df_agg.index, media, label='mean')
    plt.fill_between(df_agg.index, media - std, media + std, alpha=0.3)

    plt.title("Uncertainty in Power Over Time")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{PASTA_SAIDA}/3_uncertainty_power.png")
    plt.close()

# ==============================
# 4. BOXPLOT POR PERÍODO
# ==============================

df['periodo'] = pd.cut(df['time'], bins=3, labels=['early','mid','late'])

if 'power' in df.columns:
    plt.figure(figsize=(8,5))
    sns.boxplot(x='periodo', y='power', data=df)
    plt.title("Power Distribution by Period")
    plt.tight_layout()
    plt.savefig(f"{PASTA_SAIDA}/4_boxplot_power.png")
    plt.close()

# ==============================
# 5. HEATMAP
# ==============================

plt.figure(figsize=(12,6))
sns.heatmap(df_agg.T, cmap='coolwarm')
plt.title("Heatmap of Variables Over Time")
plt.tight_layout()
plt.savefig(f"{PASTA_SAIDA}/5_heatmap.png")
plt.close()

# ==============================
# 6. DADOS FALTANTES (INCERTEZA)
# ==============================

df_missing = df.isna().astype(int)
df_missing['time'] = df['time']

df_missing_agg = df_missing.resample('1H', on='time').mean()

plt.figure(figsize=(12,6))
df_missing_agg.plot(ax=plt.gca())
plt.title("Missing Data Over Time")
plt.tight_layout()
plt.savefig(f"{PASTA_SAIDA}/6_missing_data.png")
plt.close()

# ==============================
# FINAL
# ==============================

print(f"Gráficos salvos na pasta: {PASTA_SAIDA}")