import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 🔧 Grundlayout (volle Seite, dunkler Hintergrund)
st.set_page_config(page_title="3D Coil Minimal", layout="wide")

# Coil-Parameter (fest)
RID = 300   # mm Innenradius
RAD = 800   # mm Außenradius
WIDTH = 300 # mm Spulenbreite
COLOR = "#b87333"  # Kupferfarbe

# =====================
# 🧮 Geometrie berechnen
# =====================
theta = np.linspace(0, 2 * np.pi, 200)
z = np.linspace(-WIDTH / 2, WIDTH / 2, 80)
theta, z = np.meshgrid(theta, z)

x_outer = RAD * np.cos(theta)
y_outer = RAD * np.sin(theta)
x_inner = RID * np.cos(theta)
y_inner = RID * np.sin(theta)

# =====================
# 🌀 Coil-Flächen erzeugen
# =====================
surfaces = []

# Außenmantel
surfaces.append(go.Surface(
    x=x_outer, y=y_outer, z=z,
    colorscale=[[0, COLOR], [1, "white"]],
    showscale=False,
    lighting=dict(ambient=0.6, diffuse=0.8, specular=0.4)
))

# Innenmantel
surfaces.append(go.Surface(
    x=x_inner, y=y_inner, z=z,
    colorscale=[[0, COLOR], [1, "white"]],
    showscale=False
))

# Stirnseiten (oben & unten)
theta_top, r_top = np.meshgrid(np.linspace(0, 2 * np.pi, 200),
                               np.linspace(RID, RAD, 80))
x_top = r_top * np.cos(theta_top)
y_top = r_top * np.sin(theta_top)
z_top = np.ones_like(x_top) * (WIDTH / 2)
z_bottom = -z_top

for z_surf in [z_top, z_bottom]:
    surfaces.append(go.Surface(
        x=x_top, y=y_top, z=z_surf,
        colorscale=[[0, COLOR], [1, "white"]],
        showscale=False
    ))

# =====================
# 📷 Kamera & Layout
# =====================
fig = go.Figure(data=surfaces)
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode="manual",
        aspectratio=dict(x=1, y=1, z=0.6),
        bgcolor="#0f1117"
    ),
    paper_bgcolor="#0f1117",
    margin=dict(l=0, r=0, t=0, b=0),
    scene_camera=dict(eye=dict(x=2, y=2, z=1.3)),
    dragmode="orbit"
)

# =====================
# 🖥️ Darstellung (Fullscreen)
# =====================
st.markdown(
    """
    <style>
        div[data-testid="stPlotlyChart"] {
            height: 95vh !important;
            width: 100% !important;
        }
        .block-container {
            padding: 0rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.plotly_chart(fig, use_container_width=True, height=950)
