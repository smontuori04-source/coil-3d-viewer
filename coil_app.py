import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="3D Coil Vollbild (Fix)", layout="wide")

# Coil-Parameter
RID = 300
RAD = 800
WIDTH = 300
COLOR = "#b87333"

# Geometrie
theta = np.linspace(0, 2*np.pi, 200)
z = np.linspace(-WIDTH/2, WIDTH/2, 80)
theta, z = np.meshgrid(theta, z)

x_outer = RAD*np.cos(theta)
y_outer = RAD*np.sin(theta)
x_inner = RID*np.cos(theta)
y_inner = RID*np.sin(theta)

surfaces = []

# Außenmantel
surfaces.append(go.Surface(
    x=x_outer, y=y_outer, z=z,
    colorscale=[[0, COLOR], [1, "#f0f0f0"]],
    showscale=False,
    lighting=dict(ambient=0.5, diffuse=0.8, specular=0.5, roughness=0.3),
))

# Innenmantel
surfaces.append(go.Surface(
    x=x_inner, y=y_inner, z=z,
    colorscale=[[0, COLOR], [1, "#f0f0f0"]],
    showscale=False
))

# Stirnseiten
theta_top, r_top = np.meshgrid(np.linspace(0, 2*np.pi, 200),
                               np.linspace(RID, RAD, 80))
x_top = r_top*np.cos(theta_top)
y_top = r_top*np.sin(theta_top)
z_top = np.ones_like(x_top)*(WIDTH/2)
z_bottom = -z_top

for z_surf in [z_top, z_bottom]:
    surfaces.append(go.Surface(
        x=x_top, y=y_top, z=z_surf,
        colorscale=[[0, COLOR], [1, "#fafafa"]],
        showscale=False
    ))

# Vollansicht mit fixierter Kamera
fig = go.Figure(data=surfaces)
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False, range=[-RAD*1.3, RAD*1.3]),
        yaxis=dict(visible=False, range=[-RAD*1.3, RAD*1.3]),
        zaxis=dict(visible=False, range=[-WIDTH, WIDTH]),
        aspectmode="cube",  # füllt Bildschirm gleichmäßig aus
        bgcolor="#ffffff"
    ),
    paper_bgcolor="#ffffff",
    margin=dict(l=0, r=0, t=0, b=0),
    scene_camera=dict(eye=dict(x=2.5, y=2.5, z=1.2)),
    dragmode="orbit"
)

# CSS für echten Vollbildmodus
st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {
            height: 100vh !important;
            margin: 0 !important;
            padding: 0 !important;
            background: white !important;
        }
        div[data-testid="stPlotlyChart"] {
            height: 100vh !important;
            width: 100vw !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .block-container {
            padding: 0rem !important;
            margin: 0 !important;
            background: white !important;
        }
    </style>
""", unsafe_allow_html=True)

st.plotly_chart(fig, use_container_width=True, height=1080)
