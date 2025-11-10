import streamlit as st
import numpy as np
import plotly.graph_objects as go

# -------------------------------------------------------------------
# ⚙️ GRUNDEINSTELLUNG
# -------------------------------------------------------------------
st.set_page_config(page_title="3D Coil Viewer", layout="wide")

# -------------------------------------------------------------------
# 🎚️ SIDEBAR-PARAMETER
# -------------------------------------------------------------------
st.sidebar.title("Parameter")

RID = st.sidebar.radio("RID (Innenradius, mm):", [150, 300, 400, 500], index=2)
RAD = st.sidebar.slider("RAD (Außenradius, mm):", min_value=RID + 10, max_value=1600, value=800, step=10)
WIDTH = st.sidebar.slider("Breite (mm):", min_value=8, max_value=600, value=300)
THICK = st.sidebar.slider("Dicke (Bandstärke, mm):", min_value=0.1, max_value=5.0, value=1.0, step=0.1)

MATERIAL = st.sidebar.selectbox("Material:", ["Stahl", "Kupfer", "Aluminium", "Zink"], index=1)
VIEW = st.sidebar.radio("Ansicht:", ["Isometrisch", "Vorne", "Oben", "Seite"], index=0)

# -------------------------------------------------------------------
# 🎨 MATERIALFARBEN
# -------------------------------------------------------------------
MATERIAL_COLORS = {
    "Stahl": "#888888",
    "Kupfer": "#b87333",
    "Aluminium": "#d9d9d9",
    "Zink": "#a0a0a0"
}
color = MATERIAL_COLORS[MATERIAL]

# -------------------------------------------------------------------
# 🧮 GEOMETRIE DES COILS
# -------------------------------------------------------------------
theta = np.linspace(0, 2*np.pi, 180)
z = np.linspace(-WIDTH/2, WIDTH/2, 80)
theta, z = np.meshgrid(theta, z)

x_outer = RAD * np.cos(theta)
y_outer = RAD * np.sin(theta)
x_inner = RID * np.cos(theta)
y_inner = RID * np.sin(theta)

surfaces = []

# Außenmantel
surfaces.append(go.Surface(
    x=x_outer, y=y_outer, z=z,
    colorscale=[[0, color], [1, "#e0e0e0"]],
    showscale=False,
    lighting=dict(ambient=0.6, diffuse=0.8, specular=0.5, roughness=0.3),
))

# Innenmantel
surfaces.append(go.Surface(
    x=x_inner, y=y_inner, z=z,
    colorscale=[[0, color], [1, "#f5f5f5"]],
    showscale=False,
))

# Stirnflächen
theta2, r2 = np.meshgrid(np.linspace(0, 2*np.pi, 180),
                         np.linspace(RID, RAD, 80))
x = r2 * np.cos(theta2)
y = r2 * np.sin(theta2)
for zval in [WIDTH/2, -WIDTH/2]:
    surfaces.append(go.Surface(
        x=x, y=y, z=np.ones_like(x)*zval,
        colorscale=[[0, color], [1, "#dddddd"]],
        showscale=False,
    ))

# -------------------------------------------------------------------
# 🎥 KAMERA UND ANSICHT
# -------------------------------------------------------------------
Rmax = RAD * 1.4

views = {
    "Isometrisch": dict(eye=dict(x=2.5, y=2.5, z=1.5)),
    "Vorne": dict(eye=dict(x=0, y=0, z=3)),
    "Oben": dict(eye=dict(x=0, y=3, z=0)),
    "Seite": dict(eye=dict(x=3, y=0, z=0)),
}
camera = dict(center=dict(x=0, y=0, z=0), **views[VIEW])

fig = go.Figure(data=surfaces)
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False, range=[-Rmax, Rmax]),
        yaxis=dict(visible=False, range=[-Rmax, Rmax]),
        zaxis=dict(visible=False, range=[-Rmax, Rmax]),
        aspectmode="cube",
        bgcolor="#ffffff"
    ),
    paper_bgcolor="#ffffff",
    margin=dict(l=0, r=0, t=0, b=0),
    scene_camera=camera,
    dragmode="orbit"
)

# -------------------------------------------------------------------
# 🎨 CSS für Vollbild + dunkles Sidebar-Design
# -------------------------------------------------------------------
st.markdown("""
    <style>
        /* --- Sidebar fixieren + dunkles Design --- */
        section[data-testid="stSidebar"] {
            position: fixed !important;
            top: 0;
            left: 0;
            height: 100vh !important;
            width: 320px !important;
            background-color: #1e2328 !important;  /* dunkles Blaugrau */
            border-right: 1px solid #2f343a !important;
            padding: 18px !important;
            color: #f2f2f2 !important;
            z-index: 10;
        }

        /* --- Sidebar-Text und Titel --- */
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p {
            color: #f2f2f2 !important;
        }

        /* --- Slider (rot wie vorher) --- */
        input[type="range"]::-webkit-slider-thumb {
            background: #e53935 !important;
        }
        input[type="range"]::-moz-range-thumb {
            background: #e53935 !important;
        }
        input[type="range"]::-webkit-slider-runnable-track {
            background: #4b4f56 !important;
        }

        /* --- Checkbox + RadioButtons --- */
        input[type="checkbox"], input[type="radio"] {
            accent-color: #e53935 !important;
        }

        /* --- Hauptanzeige rechts: echtes Vollbild --- */
        div[data-testid="stAppViewContainer"] > div:nth-child(1) {
            margin-left: 320px !important; /* Platz für Sidebar */
            height: 100vh !important;
            width: calc(100vw - 320px) !important;
            background: #ffffff !important;
        }

        /* --- 3D-Plot selbst --- */
        div[data-testid="stPlotlyChart"] {
            position: absolute !important;
            top: 0;
            bottom: 0;
            left: 320px;
            right: 0;
            height: 100vh !important;
            width: calc(100vw - 320px) !important;
            margin: 0 !important;
            padding: 0 !important;
            background: #ffffff !important;
        }

        /* --- Button-Styling (Blaugrau) --- */
        button[kind="primary"] {
            background-color: #2f343a !important;
            color: #f2f2f2 !important;
            border: 1px solid #3a4046 !important;
            border-radius: 4px !important;
        }
        button[kind="primary"]:hover {
            background-color: #40464e !important;
        }

        /* --- Allgemeine Abstände anpassen --- */
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
        }
    </style>
""", unsafe_allow_html=True)


# -------------------------------------------------------------------
# 🧾 ANZEIGE
# -------------------------------------------------------------------
st.plotly_chart(fig, use_container_width=True, height=1080)
