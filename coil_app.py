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
z = np.linspace(0, width, len(theta))

# 3D-Plot
fig = go.Figure(data=[go.Scatter3d(
    x=x, y=y, z=z,
    mode='lines',
    line=dict(color='silver', width=4)
)])

fig.update_layout(
    scene=dict(
        xaxis_title='X (mm)',
        yaxis_title='Y (mm)',
        zaxis_title='Z (mm)',
        aspectmode='data',
        bgcolor='white'
    ),
    title="3D Coil Visualisierung"
)

st.plotly_chart(fig, use_container_width=True)
