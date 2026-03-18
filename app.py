import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

st.title("Pass Map")

# ==========================
# Coordenadas
# ==========================
cords = [

(37.89,65.43),(14.45,62.61),
(32.24,42.16),(31.24,63.61),
(42.05,71.92),(50.86,76.90),
(62.49,60.28),(45.37,42.66),
(46.54,48.15),(69.81,39.67),
(52.69,37.67),(66.82,39.17),
(77.45,54.30),(82.77,45.32),
(35.40,53.46),(39.05,74.41),
(27.09,55.96),(43.38,44.99),
(75.96,50.14),(93.91,73.91),
(34.07,62.28),(23.43,72.91),
(47.53,60.78),(48.86,72.91),
(48.20,51.14),(39.72,71.09),
(45.21,64.77),(35.56,75.08),
(51.52,49.64),(48.36,24.87),
(79.12,58.62),(96.41,59.62),
(53.35,26.87),(70.31,21.38),
(30.74,39.67),(46.54,38.67),
(48.36,40.17),(51.85,45.98),
(28.42,39.50),(22.93,51.97),
(41.22,52.63),(53.85,45.98),
(33.57,47.98),(91.58,70.92),
(85.77,13.57),(86.60,5.26),
(29.25,29.69),(29.75,13.07),
(56.18,39.50),(68.98,52.63),
(92.75,21.22),(107.71,12.24),
(49.36,52.14),(66.48,51.80),
(54.02,67.10),(80.78,56.12),
(73.13,50.14),(78.78,27.70),
(74.30,70.75),(76.62,76.90),
(48.36,30.36),(55.35,35.18),
(55.51,54.46),(66.32,57.29),
(74.46,60.78),(86.26,71.25),
(72.80,47.81),(78.12,18.06),
(45.04,40.83),(51.85,27.20),
(52.19,59.62),(80.28,15.40),
(48.20,61.11),(67.81,50.47),
(54.68,41.99),(53.68,27.20),
(76.29,50.64),(74.13,67.26),
(37.23,58.78),(43.21,75.74)

]

num_passes = 40
coords = cords[:num_passes * 2]

passes_errados = [19,22,29,40]

# ==========================
# DataFrame
# ==========================
passes = []

for i in range(0, len(coords), 2):
    start = coords[i]
    end = coords[i+1]

    numero = int(i/2) + 1

    passes.append({
        "numero": numero,
        "x_start": start[0],
        "y_start": start[1],
        "x_end": end[0],
        "y_end": end[1]
    })

df = pd.DataFrame(passes)

# ==========================
# Métricas
# ==========================
goal_x = 120
goal_y = 40

def distancia_gol(x,y):
    return np.sqrt((goal_x-x)**2 + (goal_y-y)**2)

df["dist_inicio"] = distancia_gol(df.x_start, df.y_start)
df["dist_fim"] = distancia_gol(df.x_end, df.y_end)

df["ganho"] = df["dist_inicio"] - df["dist_fim"]

df["progressivo"] = df["ganho"] >= 10
df["errado"] = df["numero"].isin(passes_errados)

# ==========================
# Plot
# ==========================
pitch = Pitch(
    pitch_type='statsbomb',
    pitch_color='#f5f5f5',
    line_color='#4a4a4a'
)

fig, ax = pitch.draw(figsize=(10,7))

# linha de progressão
ax.axvline(x=80, color='#FFD54F', linewidth=1.5, alpha=0.25)

for _, row in df.iterrows():

    if row["errado"]:
        color = (1, 0, 0, 0.6)
        width = 1.8

    elif row["progressivo"]:
        color = (0.2, 0.3, 1, 0.9)
        width = 2.2

    else:
        color = (0.5, 0.5, 0.5, 0.5)
        width = 1.4

    pitch.arrows(
        row.x_start,
        row.y_start,
        row.x_end,
        row.y_end,
        color=color,
        width=width,
        headwidth=3,
        headlength=3,
        ax=ax
    )

# ==========================
# Render no Streamlit
# ==========================
col1, col2, col3 = st.columns([1,2,1])

# ==========================
# ESTATÍSTICAS
# ==========================

total = len(df)

passes_certos = df["certo"].sum()
passes_errados = df["errado"].sum()
perc_certos = passes_certos / total * 100

prog = df[df["progressivo"]]
prog_total = len(prog)
prog_certos = prog["certo"].sum()
prog_errados = prog["errado"].sum()
perc_prog = prog_total / total * 100

passes_direita = df["direita"].sum()
passes_esquerda = df["esquerda"].sum()

ultimo_terco_certos = df[df["ultimo_terco"] & df["certo"]].shape[0]

pc = df[df["proprio_campo"]]
pc_certos = pc["certo"].sum()
pc_errados = pc["errado"].sum()
pc_perc = pc_certos / len(pc) * 100 if len(pc) > 0 else 0

ca = df[df["campo_adversario"]]
ca_certos = ca["certo"].sum()
ca_errados = ca["errado"].sum()
ca_perc = ca_certos / len(ca) * 100 if len(ca) > 0 else 0


# ==========================
# DASHBOARD
# ==========================

st.subheader("📊 Estatísticas de Passe")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total de passes", total)
col2.metric("Precisão", f"{perc_certos:.1f}%")
col3.metric("Progressivos", prog_total)
col4.metric("% Progressivos", f"{perc_prog:.1f}%")

st.divider()

col5, col6, col7 = st.columns(3)

col5.metric("→ Direita", passes_direita)
col6.metric("← Esquerda", passes_esquerda)
col7.metric("Último terço (certos)", ultimo_terco_certos)

st.divider()

col8, col9 = st.columns(2)

with col8:
    st.markdown("### Próprio campo")
    st.metric("Precisão", f"{pc_perc:.1f}%")
    st.write(f"Certos: {pc_certos} | Errados: {pc_errados}")

with col9:
    st.markdown("### Campo adversário")
    st.metric("Precisão", f"{ca_perc:.1f}%")
    st.write(f"Certos: {ca_certos} | Errados: {ca_errados}")

with col2:
    st.pyplot(fig)
