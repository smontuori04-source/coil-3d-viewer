import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- Grundeinstellungen ---
st.set_page_config(page_title="3D Coil Viewer", layout="wide")

# --- Sidebar-Layout ---
st.sidebar.header("Parameter")

# Coil-Parameter
rid = st.sidebar.radio("RID (Innenradius, mm):", [150, 300, 400, 500])
rad = st.sidebar.slider("RAD (Außenradius, mm)", rid + 10, 1600, 800)
width = st.sidebar.slider("Breite (mm)", 8, 600, 300)
metal_type = st.sidebar.selectbox("Material", ["Edelstahl", "Aluminium", "Kupfer"])
view = st.sidebar.radio("Ansicht:", ["Isometrisch", "Vorne", "Oben", "Seite"], index=0)

# --- Vollbild-Schalter ---
fullscreen = st.sidebar.checkbox("🖥️ Vollbildmodus aktivieren", value=False)

# --- Farben definieren ---
colors = {
    "Edelstahl": "#C0C0C0",
    "Aluminium": "#D9D9D9",
    "Kupfer": "#B87333"
}
color = colors[metal_type]

# --- Coil-Geometrie ---
theta_steps, height_steps = 200, 60
theta = np.linspace(0, 2 * np.pi, theta_steps)
z = np.linspace(-width / 2, width / 2, height_steps)
theta, z = np.meshgrid(theta, z)

x_outer = rad * np.cos(theta)
y_outer = rad * np.sin(theta)
x_inner = rid * np.cos(theta)
y_inner = rid * np.sin(theta)

# --- Oberflächen ---
surfaces = []

# Außenmantel
surfaces.append(go.Surface(
    x=x_outer, y=y_outer, z=z,
    colorscale=[[0, color], [1, "white"]],
    showscale=False,
    lighting=dict(ambient=0.6, diffuse=0.8, specular=0.5, roughness=0.25),
    lightposition=dict(x=2000, y=2000, z=1000)
))

# Innenmantel
surfaces.append(go.Surface(
    x=x_inner, y=y_inner, z=z,
    colorscale=[[0, color], [1, "white"]],
    showscale=False,
    lighting=dict(ambient=0.5, diffuse=0.7, specular=0.4, roughness=0.3),
    lightposition=dict(x=-1000, y=-2000, z=500)
))

# Oben / Unten
theta_top, r_top = np.meshgrid(np.linspace(0, 2 * np.pi, theta_steps),
                               np.linspace(rid, rad, height_steps))
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

# --- Kamera-Ansichten ---
camera_views = {
    "Isometrisch": dict(eye=dict(x=2.6, y=2.6, z=1.2)),
    "Vorne": dict(eye=dict(x=0.01, y=0.01, z=2.5)),
    "Oben": dict(eye=dict(x=0.01, y=3.5, z=0.01)),
    "Seite": dict(eye=dict(x=3.5, y=0.01, z=0.01))
}

# --- Plot erstellen ---
fig = go.Figure(data=surfaces)
# --- Kamera dynamisch anpassen (zoomt auf den Coil) ---
max_dim = max(rad, width)
zoom = 1.8 * (1000 / max_dim)  # je größer der Coil, desto näher die Kamera

# --- Plot aktualisieren ---
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
    title=dict(text=f"{metal_type}-Coil", x=0.5, font=dict(size=22, color="white")),
    margin=dict(l=0, r=0, t=30, b=0),
    scene_camera=dict(
        eye=dict(x=zoom, y=zoom, z=zoom),
        center=dict(x=0, y=0, z=0)
    ),
    dragmode="orbit"
)

# --- CSS für mehr Anzeigefläche ---
st.markdown(
    f"""
    <style>
        div[data-testid="stPlotlyChart"] {{
            height: {"98vh" if fullscreen else "80vh"} !important;
            width: 100vw !important;
        }}
        .block-container {{
            padding: 0rem !important;
        }}
    </style>
    """, unsafe_allow_html=True
)

# --- Anzeige ---
st.plotly_chart(fig, use_container_width=True, height=(1080 if fullscreen else 800))
