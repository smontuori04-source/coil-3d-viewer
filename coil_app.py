import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="3D Coil Viewer", layout="wide")

st.sidebar.header("Parameter")

# Eingaben
rid = st.sidebar.radio("RID (Innenradius, mm):", [150, 300, 400, 500])
rad = st.sidebar.slider("RAD (Außenradius, mm)", rid + 10, 1600, 800)
width = st.sidebar.slider("Breite (mm)", 8, 600, 300)
thickness = st.sidebar.slider("Dicke (mm)", 0.1, 5.0, 1.0)
metal_type = st.sidebar.selectbox("Material", ["Edelstahl", "Aluminium", "Kupfer"])

# Metallfarbe auswählen
colors = {
    "Edelstahl": "#C0C0C0",
    "Aluminium": "#D9D9D9",
    "Kupfer": "#B87333"
}
color = colors[metal_type]

# Zylinder (Coil) berechnen
theta = np.linspace(0, 2 * np.pi, 100)
z = np.linspace(-width / 2, width / 2, 50)
theta, z = np.meshgrid(theta, z)

# Außen- und Innenmantel
x_outer = rad * np.cos(theta)
y_outer = rad * np.sin(theta)
x_inner = rid * np.cos(theta)
y_inner = rid * np.sin(theta)

# Coil-Wand simulieren
x = np.concatenate([x_outer, x_inner[::-1]])
y = np.concatenate([y_outer, y_inner[::-1]])
z = np.concatenate([z, z[::-1]])

# Farbverlauf (Metall-Reflexion)
intensity = (np.cos(theta) * 0.5 + 0.5)

fig = go.Figure(data=[go.Surface(
    x=x, y=y, z=z,
    surfacecolor=intensity,
    colorscale=[[0, color], [1, "white"]],
    cmin=0, cmax=1,
    showscale=False,
    lighting=dict(ambient=0.5, diffuse=0.9, specular=0.5, roughness=0.3),
    lightposition=dict(x=2000, y=1000, z=1000),
    name="Coil"
)])

# Kamera, Licht & Layout
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode="manual",
        aspectratio=dict(x=1, y=1, z=0.5),
        bgcolor="white"
    ),
    title=dict(text=f"3D {metal_type}-Coil", x=0.5, font=dict(size=22)),
    margin=dict(l=0, r=0, t=60, b=0),
)

# Kamera-Perspektive
fig.update_layout(scene_camera=dict(
    eye=dict(x=1.8, y=1.8, z=1.0)
))

st.plotly_chart(fig, use_container_width=True, height=800)
