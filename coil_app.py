import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Coil Visualisierung", layout="wide")

# Sidebar (Parameter)
st.sidebar.title("🌀 Coil Parameter")
RID = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD = st.sidebar.number_input("Außenradius (mm)", min_value=600, max_value=1600, value=800, step=10)
WIDTH = st.sidebar.number_input("Breite (mm)", min_value=8, max_value=600, value=300, step=1)
THICK = st.sidebar.number_input("Bandstärke (mm)", min_value=0.5, max_value=20.0, value=3.0, step=0.1)
MATERIAL = st.sidebar.selectbox("Material", ["Stahl", "Kupfer", "Aluminium"], index=0)

density = {"Stahl": 7.85, "Kupfer": 8.96, "Aluminium": 2.70}
rho = density[MATERIAL]

# Coilberechnungen
import math
volume_mm3 = math.pi * (RAD**2 - RID**2) * WIDTH
volume_m3 = volume_mm3 * 1e-9
gewicht = rho * volume_m3 * 1000  # kg
gewicht_pro_mm = gewicht / WIDTH
laenge = (math.pi * (RAD + RID)) * (WIDTH / THICK) / 1000

st.sidebar.subheader("📊 Berechnete Werte")
col1, col2, col3 = st.sidebar.columns(3)
col1.metric("Gesamtgewicht", f"{gewicht:,.0f} kg".replace(",", " "))
col2.metric("Gewicht/mm", f"{gewicht_pro_mm:,.2f} kg/mm")
col3.metric("Länge", f"{laenge:,.2f} m")

# Schnittbreiten
st.sidebar.markdown("---")
st.sidebar.subheader("✂️ Zuschnittbreiten (mm)")
cuts_input = st.sidebar.text_input("Kommagetrennt (z. B. 100,200,250)", "100,200,250")
cuts = [float(c.strip()) for c in cuts_input.split(",") if c.strip()]
rest = WIDTH - sum(cuts)
if rest > 0:
    cuts.append(rest)

# 3D Darstellung – mittig, hell, abgerundet
def make_coil_html(title, coil_segments, material_color):
    return f"""
    <div style="
        background:#f5f5f5;
        border-radius:18px;
        padding:10px;
        margin:auto;
        width:90%;
        height:380px;
        box-shadow:0 0 20px rgba(0,0,0,0.1);
    ">
    <h3 style='text-align:center;color:#222;font-family:sans-serif;'>{title}</h3>
    <script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
    <script>
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf5f5f5);
    const camera = new THREE.PerspectiveCamera(55, 1.6, 0.1, 10000);
    const renderer = new THREE.WebGLRenderer({{antialias:true}});
    renderer.setSize(window.innerWidth*0.38, 350);
    document.currentScript.parentElement.appendChild(renderer.domElement);

    const light = new THREE.DirectionalLight(0xffffff, 1.1);
    light.position.set(500,500,500);
    scene.add(light);
    scene.add(new THREE.AmbientLight(0xffffff, 0.5));

    const RID = {RID}, RAD = {RAD}, WIDTH = {WIDTH};
    const segments = 256;

    const shape = new THREE.Shape();
    shape.absarc(0, 0, RAD, 0, Math.PI*2);
    const hole = new THREE.Path();
    hole.absarc(0, 0, RID, 0, Math.PI*2, true);
    shape.holes.push(hole);

    const geom = new THREE.ExtrudeGeometry(shape, {{depth: WIDTH, bevelEnabled:false}});
    geom.rotateX(Math.PI/2);
    geom.translate(0, -WIDTH/2, 0);
    const mat = new THREE.MeshPhongMaterial({{color: {material_color}, shininess: 80}});
    const coil = new THREE.Mesh(geom, mat);
    scene.add(coil);

    camera.position.set(0, RAD*1.2, RAD*2.2);
    camera.lookAt(0, 0, 0);
    renderer.render(scene, camera);
    </script>
    </div>
    """

color_map = {"Stahl": "0x555555", "Kupfer": "0xb87333", "Aluminium": "0xd0d0d0"}

colA, colB = st.columns([0.55, 0.45])
with colB:
    st.markdown("### 🧲 Mastercoil (liegend)")
    components.html(make_coil_html("Mastercoil", 1, color_map[MATERIAL]), height=400)
    st.markdown("### ✂️ Coil mit Zuschnitten (gestapelt)")
    components.html(make_coil_html("Coil mit Zuschnitten", len(cuts), color_map[MATERIAL]), height=400)
