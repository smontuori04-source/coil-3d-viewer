import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="3D Coil Viewer", layout="wide")

st.sidebar.header("Parameter")

# Eingaben
rid = st.sidebar.radio("RID (Innenradius, mm):", [150, 300, 400, 500])
rad = st.sidebar.slider("RAD (Außenradius, mm)", rid + 10, 1600, 800)
width = st.sidebar.slider("Breite (mm)", 8, 600, 300)
metal_type = st.sidebar.selectbox("Material", ["Edelstahl", "Aluminium", "Kupfer"])

# Kamera-Ansichtsauswahl
view = st.sidebar.radio(
    "Ansicht:",
    ["Isometrisch", "Vorne", "Oben", "Seite"],
    index=0
)

# Farben
colors = {
    "Edelstahl": "#C0C0C0",
    "Aluminium": "#D9D9D9",
    "Kupfer": "#B87333"
}
color = colors[metal_type]

# Coil-Geometrie
theta_steps = 200
height_steps = 60
theta = np.linspace(0, 2 * np.pi, theta_steps)
z = np.linspace(-width / 2, width / 2, height_steps)
theta, z = np.meshgrid(theta, z)

x_outer = rad * np.cos(theta)
y_outer = rad * np.sin(theta)
x_inner = rid * np.cos(theta)
y_inner = rid * np.sin(theta)

# Flächen vorbereiten
surfaces = []

# Außenmantel
surfaces.append(go.Surface(
    x=x_outer, y=y_outer, z=z,
    colorscale=[[0, color], [1, "white"]],
    showscale=False,
    lighting=dict(ambient=0.5, diffuse=0.8, specular=0.4, roughness=0.3),
    lightposition=dict(x=2000, y=2000, z=1000)
))

# Innenmantel
surfaces.append(go.Surface(
    x=x_inner, y=y_inner, z=z,
    colorscale=[[0, color], [1, "white"]],
    showscale=False,
    lighting=dict(ambient=0.4, diffuse=0.6, specular=0.3, roughness=0.5),
    lightposition=dict(x=-1000, y=-2000, z=500)
))

# Oben / Unten
theta_top = np.linspace(0, 2 * np.pi, theta_steps)
r_top = np.linspace(rid, rad, height_steps)
theta_top, r_top = np.meshgrid(theta_top, r_top)
x_top = r_top * np.cos(theta_top)
y_top = r_top * np.sin(theta_top)
z_top = np.ones_like(x_top) * (width / 2)
z_bottom = np.ones_like(x_top) * (-width / 2)

for z_surf in [z_top, z_bottom]:
    surfaces.append(go.Surface(
        x=x_top, y=y_top, z=z_surf,
        colorscale=[[0, color], [1, "white"]],
        showscale=False, opacity=1.0
    ))

# Plot erstellen
fig = go.Figure(data=surfaces)

# Layout fixieren
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode="manual",
        aspectratio=dict(x=1, y=1, z=0.6),
        bgcolor="white"
    ),
    title=dict(text=f"{metal_type}-Coil", x=0.5, font=dict(size=22)),
    margin=dict(l=0, r=0, t=40, b=0)
)

# 📷 Kamera-Positionen je nach Auswahl
camera_views = {
    "Isometrisch": dict(eye=dict(x=2.6, y=2.6, z=1.2)),
    "Vorne": dict(eye=dict(x=0.01, y=0.01, z=2.5)),
    "Oben": dict(eye=dict(x=0.01, y=3.5, z=0.01)),
    "Seite": dict(eye=dict(x=3.5, y=0.01, z=0.01))
}

fig.update_layout(scene_camera=camera_views[view])

# Anzeigen
st.plotly_chart(fig, use_container_width=True, height=950)
