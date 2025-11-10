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

st.sidebar.write(f"RID = {rid} mm, RAD = {rad} mm, Breite = {width} mm, Dicke = {thickness} mm")

# Coil-Daten berechnen
turns = int((rad - rid) / thickness)
theta = np.linspace(0, 2 * np.pi * turns, 8000)
r = np.linspace(rid, rad, len(theta))
x = r * np.cos(theta)
y = r * np.sin(theta)
z = np.linspace(-width/2, width/2, len(theta))  # mittig

# 3D-Plot
fig = go.Figure(data=[go.Scatter3d(
    x=x, y=y, z=z,
    mode='lines',
    line=dict(color='gray', width=6)
)])

# **Wichtige Änderungen hier:**
fig.update_layout(
    scene=dict(
        xaxis=dict(nticks=10, range=[-rad * 1.2, rad * 1.2]),
        yaxis=dict(nticks=10, range=[-rad * 1.2, rad * 1.2]),
        zaxis=dict(nticks=10, range=[-width * 1.2, width * 1.2]),
        aspectmode='manual',           # feste Skalierung!
        aspectratio=dict(x=1, y=1, z=0.5),  # Z verkürzt = realistischer Coil
        bgcolor='white'
    ),
    title="3D Coil Visualisierung",
    margin=dict(l=0, r=0, t=50, b=0)
)

# Kamera-Startposition: leicht schräg, wie bei 3D-CAD
fig.update_layout(scene_camera=dict(
    eye=dict(x=1.5, y=1.5, z=0.7)
))

st.plotly_chart(fig, use_container_width=True)
