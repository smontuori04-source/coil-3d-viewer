import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="3D Coil – Lagerraum", layout="wide")

# Coil-Parameter
RID, RAD, WIDTH = 300, 800, 300
COLOR = "#b87333"

# Geometrie
theta = np.linspace(0, 2*np.pi, 200)
z = np.linspace(-WIDTH/2, WIDTH/2, 80)
theta, z = np.meshgrid(theta, z)

x_outer = RAD*np.cos(theta)
y_outer = RAD*np.sin(theta)
x_inner = RID*np.cos(theta)
y_inner = RID*np.sin(theta)

# Coil-Flächen
coil = []
coil.append(go.Surface(
    x=x_outer, y=y_outer, z=z,
    colorscale=[[0, COLOR], [1, "#f0f0f0"]],
    showscale=False,
    lighting=dict(ambient=0.4, diffuse=0.7, specular=0.5, roughness=0.25)
))
coil.append(go.Surface(
    x=x_inner, y=y_inner, z=z,
    colorscale=[[0, COLOR], [1, "#e8e8e8"]],
    showscale=False
))

theta2, r2 = np.meshgrid(np.linspace(0, 2*np.pi, 200),
                         np.linspace(RID, RAD, 80))
x = r2 * np.cos(theta2)
y = r2 * np.sin(theta2)
for zval in [WIDTH/2, -WIDTH/2]:
    coil.append(go.Surface(
        x=x, y=y, z=np.ones_like(x)*zval,
        colorscale=[[0, COLOR], [1, "#dddddd"]],
        showscale=False
    ))

# Coil leicht vom Boden anheben
for s in coil:
    s.update(z=s.z - WIDTH/2 + 50)

# --- Lagerraum erzeugen --------------------------------------------
room = []
room_size = RAD * 3

# Boden
X, Y = np.meshgrid(np.linspace(-room_size, room_size, 2),
                   np.linspace(-room_size, room_size, 2))
Z = np.zeros_like(X)
room.append(go.Surface(
    x=X, y=Y, z=Z,
    colorscale=[[0, "#d9d9d9"], [1, "#c9c9c9"]],
    showscale=False, opacity=1
))

# Rückwand
Y2, Z2 = np.meshgrid(np.linspace(-room_size, room_size, 2),
                     np.linspace(0, room_size, 2))
X2 = np.ones_like(Y2) * (-room_size)
room.append(go.Surface(
    x=X2, y=Y2, z=Z2,
    colorscale=[[0, "#e0e0e0"], [1, "#e0e0e0"]],
    showscale=False, opacity=0.9
))

# Seitenwand
X3, Z3 = np.meshgrid(np.linspace(-room_size, room_size, 2),
                     np.linspace(0, room_size, 2))
Y3 = np.ones_like(X3) * (room_size)
room.append(go.Surface(
    x=X3, y=Y3, z=Z3,
    colorscale=[[0, "#e0e0e0"], [1, "#e0e0e0"]],
    showscale=False, opacity=0.9
))

# --- Zusammenbauen --------------------------------------------------
fig = go.Figure(data=room + coil)
Rmax = room_size
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False, range=[-Rmax, Rmax]),
        yaxis=dict(visible=False, range=[-Rmax, Rmax]),
        zaxis=dict(visible=False, range=[0, Rmax]),
        bgcolor="#ffffff",
        aspectmode="cube"
    ),
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor="#ffffff",
    scene_camera=dict(eye=dict(x=2.5, y=2.5, z=1.2)),
    dragmode="orbit"
)

# --- CSS: Vollbild & Sidebar fixiert --------------------------------
st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            position: fixed !important;
            top: 0;
            left: 0;
            height: 100vh !important;
            width: 320px !important;
            background-color: #1e2328 !important;
            border-right: 1px solid #2f343a !important;
            padding: 18px !important;
            color: #f2f2f2 !important;
            z-index: 10;
        }
        div[data-testid="stAppViewContainer"] > div:nth-child(1) {
            margin-left: 320px !important;
            height: 100vh !important;
            width: calc(100vw - 320px) !important;
            background: #ffffff !important;
        }
        div[data-testid="stPlotlyChart"] {
            position: absolute !important;
            top: 0;
            left: 320px;
            right: 0;
            bottom: 0;
            height: 100vh !important;
            width: calc(100vw - 320px) !important;
            background: #ffffff !important;
        }
        .block-container { padding: 0 !important; margin: 0 !important; }
    </style>
""", unsafe_allow_html=True)

# --- Darstellung ----------------------------------------------------
st.plotly_chart(fig, use_container_width=True, height=1080)
