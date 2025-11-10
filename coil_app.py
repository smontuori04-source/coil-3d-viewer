import streamlit as st
import numpy as np
import plotly.graph_objects as go

# =====================
# 🔧 Grundkonfiguration
# =====================
st.set_page_config(page_title="3D Coil Viewer", layout="wide")

st.sidebar.title("Parameter")

# Eingabefelder
rid = st.sidebar.radio("RID (Innenradius, mm)", [150, 300, 400, 500], index=2)
rad = st.sidebar.slider("RAD (Außenradius, mm)", rid + 10, 1600, 800, step=10)
width = st.sidebar.slider("Breite (mm)", 8, 600, 300)
thickness = st.sidebar.slider("Dicke (mm)", 0.1, 5.0, 1.0, step=0.1)

material = st.sidebar.selectbox("Material", ["Kupfer", "Edelstahl", "Aluminium"])
view = st.sidebar.radio("Ansicht", ["Isometrisch", "Vorne", "Oben", "Seite"], index=0)

# =====================
# 🎨 Farben / Materialien
# =====================
material_colors = {
    "Kupfer": "#b87333",
    "Edelstahl": "#c0c0c0",
    "Aluminium": "#d9d9d9"
}
color = material_colors[material]

# =====================
# 🧮 Geometrie berechnen
# =====================
theta = np.linspace(0, 2 * np.pi, 200)
z = np.linspace(-width / 2, width / 2, 50)
theta, z = np.meshgrid(theta, z)

x_outer = rad * np.cos(theta)
y_outer = rad * np.sin(theta)
x_inner = rid * np.cos(theta)
y_inner = rid * np.sin(theta)

# =====================
# 🌀 Coil-Flächen erzeugen
# =====================
surfaces = []

# Außenmantel
surfaces.append(go.Surface(
    x=x_outer, y=y_outer, z=z,
    colorscale=[[0, color], [1, "white"]],
    showscale=False,
    lighting=dict(ambient=0.6, diffuse=0.9, specular=0.4),
))

# Innenmantel
surfaces.append(go.Surface(
    x=x_inner, y=y_inner, z=z,
    colorscale=[[0, color], [1, "white"]],
    showscale=False,
    lighting=dict(ambient=0.5, diffuse=0.7, specular=0.4),
))

# Stirnflächen
theta_top, r_top = np.meshgrid(np.linspace(0, 2 * np.pi, 200),
                               np.linspace(rid, rad, 50))
x_top = r_top * np.cos(theta_top)
y_top = r_top * np.sin(theta_top)
z_top = np.ones_like(x_top) * (width / 2)
z_bottom = -z_top

for z_surf in [z_top, z_bottom]:
    surfaces.append(go.Surface(
        x=x_top, y=y_top, z=z_surf,
        colorscale=[[0, color], [1, "white"]],
        showscale=False
    ))

# =====================
# 📷 Kamerapositionen
# =====================
camera_views = {
    "Isometrisch": dict(eye=dict(x=2, y=2, z=1.3)),
    "Vorne": dict(eye=dict(x=0, y=0, z=3)),
    "Oben": dict(eye=dict(x=0, y=3, z=0)),
    "Seite": dict(eye=dict(x=3, y=0, z=0)),
}

# =====================
# 📊 Plot erstellen
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
    title=dict(text=f"{material}-Coil", x=0.5, font=dict(size=22, color="white")),
    margin=dict(l=0, r=0, t=40, b=0),
    scene_camera=camera_views[view],
    dragmode="orbit"
)

# =====================
# 🖥️ Darstellung (Vollbild)
# =====================
st.markdown(
    """
    <style>
        div[data-testid="stPlotlyChart"] {
            height: 90vh !important;
            width: 100% !important;
        }
        .block-container {
            padding: 0rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.plotly_chart(fig, use_container_width=True, height=900)
