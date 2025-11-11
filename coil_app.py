import math
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ==============================
# 📄 Seiten Setup
# ==============================
st.set_page_config(page_title="3D Coil – Zuschnittplanung", layout="wide")

# ==============================
# 🎨 Styling (kein Scrollen, besseres Verhältnis)
# ==============================
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #2C2F35;
        color: #EDEDED;
        overflow: hidden !important; /* Kein Scrollen */
        height: 100vh;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #2C2F35 !important;
        width: 58% !important;
        min-width: 58% !important;
        color: #EDEDED;
        padding-right: 1%;
        overflow-y: auto;
        height: 100vh;
    }

    /* Hauptbereich rechts */
    section.main > div {
        padding: 1rem 2rem 1rem 0rem;
        height: 100vh;
        overflow: hidden;
    }

    /* 3D Box Layout */
    .threejs-box {
        background-color: #0E1117;
        border-radius: 12px;
        box-shadow: 0 0 15px rgba(0,0,0,0.3);
        padding: 10px;
        margin-bottom: 15px;
    }

    h1, h2, h3 {
        color: #EDEDED;
        font-weight: 600;
        letter-spacing: 0.4px;
    }

    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }

    /* Slider schmaler */
    .stSlider {
        padding-bottom: 0px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================
# 🧮 Sidebar – Eingaben
# ==============================
st.sidebar.title("🌀 Coil Berechnung & Zuschnittplanung")

RID = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD = st.sidebar.slider("Außenradius (mm)", 600, 1600, 800, step=10)
WIDTH = st.sidebar.slider("Breite (mm)", 8, 600, 300, step=1)
MATERIAL = st.sidebar.selectbox("Material", ["Stahl", "Kupfer", "Aluminium"], index=0)

# Dichte (g/mm³)
density_map = {"Stahl": 0.00785, "Kupfer": 0.00896, "Aluminium": 0.00270}
rho = density_map[MATERIAL]

# ==============================
# 📏 Berechnung
# ==============================
volume_mm3 = math.pi * (RAD**2 - RID**2) * WIDTH
weight_g = volume_mm3 * rho
weight_kg = weight_g / 1000
kg_per_mm = weight_kg / WIDTH

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Berechnete Werte")
col1, col2 = st.sidebar.columns(2)
col1.metric("Gesamtgewicht", f"{weight_kg:,.0f} kg")
col2.metric("Gewicht/mm", f"{kg_per_mm:,.2f} kg/mm")
st.sidebar.metric("Volumen", f"{volume_mm3/1e9:,.2f} dm³")

# ==============================
# ✂️ Zuschnitt
# ==============================
st.sidebar.markdown("---")
st.sidebar.subheader("✂️ Zuschnittbreiten")
cuts_input = st.sidebar.text_input("Gib Zuschnittbreiten (Komma getrennt) ein:", "100, 200, 250")

try:
    cuts = [float(x.strip()) for x in cuts_input.split(",") if x.strip()]
    sum_cuts = sum(cuts)
    cut_weights = [kg_per_mm * c for c in cuts]
    rest_width = WIDTH - sum_cuts
    rest_weight = kg_per_mm * rest_width if rest_width > 0 else 0

    df = pd.DataFrame({
        "Zuschnitt": [f"{i+1}" for i in range(len(cuts))] + (["Rest"] if rest_width > 0 else []),
        "Breite (mm)": cuts + ([rest_width] if rest_width > 0 else []),
        "Gewicht (kg)": [round(w, 2) for w in cut_weights] + ([round(rest_weight, 2)] if rest_weight > 0 else []),
    })
    st.sidebar.dataframe(df, hide_index=True, use_container_width=True)
except Exception as e:
    st.sidebar.error(f"Fehler in der Eingabe: {e}")

# ==============================
# 🧱 Hauptbereich – keine Scrollbars, feste Höhe
# ==============================
st.title("🧲 3D-Coil Visualisierung")

coil_height = 340  # Fixe Höhe für beide Coils, damit kein Scroll nötig ist

# --- Mastercoil ---
st.markdown('<div class="threejs-box">', unsafe_allow_html=True)
st.markdown("### 🧩 Mastercoil (3D Ansicht)")

threejs_master = f"""
<html><body style="margin:0; background-color:#0E1117;">
<script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
<script>
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(55, 1, 1, 20000);
const renderer = new THREE.WebGLRenderer({{antialias:true, alpha:true}});
renderer.setClearColor(0x0E1117, 1);
renderer.setSize(window.innerWidth, {coil_height});
document.body.appendChild(renderer.domElement);
const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(1,1,1);
scene.add(light);

const shape = new THREE.Shape();
shape.absarc(0,0,{RAD},0,Math.PI*2,false);
const hole = new THREE.Path();
hole.absarc(0,0,{RID},0,Math.PI*2,true);
shape.holes.push(hole);

const geom = new THREE.ExtrudeGeometry(shape,{{depth:{WIDTH},bevelEnabled:false}});
geom.rotateZ(Math.PI/2);
geom.translate(0,{RAD},0);
const mat = new THREE.MeshPhongMaterial({{color:0x999999, shininess:120}});
const coil = new THREE.Mesh(geom,mat);
scene.add(coil);

camera.position.set({RAD*2},{RAD*1.2},{RAD*2});
camera.lookAt(0,{RAD/2},0);
renderer.render(scene,camera);
</script></body></html>
"""
components.html(threejs_master, height=coil_height)
st.markdown('</div>', unsafe_allow_html=True)

# --- Coil mit Zuschnitten ---
st.markdown('<div class="threejs-box">', unsafe_allow_html=True)
st.markdown("### ✂️ Coil mit Zuschnitten (3D Ansicht)")

threejs_cuts = f"""
<html><body style="margin:0; background-color:#0E1117;">
<script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
<script>
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(55, 1, 1, 20000);
const renderer = new THREE.WebGLRenderer({{antialias:true, alpha:true}});
renderer.setClearColor(0x0E1117, 1);
renderer.setSize(window.innerWidth, {coil_height});
document.body.appendChild(renderer.domElement);
const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(1,1,1);
scene.add(light);

const RID = {RID}, RAD = {RAD};
const cuts = [{','.join(map(str, cuts)) if 'cuts' in locals() else ''}];
let offset = 0;
const colors = [0xb87333, 0x999999, 0xd0d0d0, 0x888888, 0xaaaaaa];

for (let i=0; i<cuts.length; i++) {{
    const shape = new THREE.Shape();
    shape.absarc(0,0,RAD,0,Math.PI*2,false);
    const hole = new THREE.Path();
    hole.absarc(0,0,RID,0,Math.PI*2,true);
    shape.holes.push(hole);

    const geom = new THREE.ExtrudeGeometry(shape,{{depth:cuts[i],bevelEnabled:false}});
    geom.rotateZ(Math.PI/2);
    geom.translate(offset, RAD, 0);
    const mat = new THREE.MeshPhongMaterial({{color:colors[i % colors.length], shininess:120}});
    const part = new THREE.Mesh(geom, mat);
    scene.add(part);
    offset += cuts[i];
}}

camera.position.set({RAD*2},{RAD*1.2},{RAD*2});
camera.lookAt(0,{RAD/2},0);
renderer.render(scene,camera);
</script></body></html>
"""
components.html(threejs_cuts, height=coil_height)
st.markdown('</div>', unsafe_allow_html=True)
