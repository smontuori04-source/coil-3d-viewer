import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="3D Coil – Streamlit + HTML", layout="wide")

st.sidebar.title("Coil Parameter")

# Feste RID-Auswahl
RID = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD = st.sidebar.slider("Außenradius (mm)", 600, 1600, 800, step=10)
WIDTH = st.sidebar.slider("Breite (mm)", 8, 600, 300, step=1)
THK = st.sidebar.slider("Dicke (mm)", 0.1, 5.0, 1.0, step=0.1)
DENSITY = st.sidebar.selectbox(
    "Materialdichte",
    [("Stahl", 7.85), ("Kupfer", 8.96), ("Aluminium", 2.70)],
    index=0
)

# --- Berechnungen in Python ---
material, rho = DENSITY
coil_volume = math.pi * (RAD**2 - RID**2) * WIDTH  # mm³
coil_weight = coil_volume * rho / 1e6              # g → kg
coil_length = 2 * math.pi * ((RAD + RID) / 2)      # mm (mittlere Länge)

st.sidebar.markdown(f"""
**Material:** {material}  
**Volumen:** {coil_volume:,.0f} mm³  
**Gewicht:** {coil_weight:,.2f} kg  
**Mittlere Länge:** {coil_length:,.0f} mm
""")

# --- HTML-Code aus CoilV1.1.html integriert ---
threejs_html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8" />
<style>
  html,body{{margin:0;height:100%;background:#fff;overflow:hidden;}}
  canvas{{display:block;width:100vw;height:100vh;}}
</style>
</head>
<body>
<script type="module">
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.module.js';
import {{ OrbitControls }} from 'https://cdn.jsdelivr.net/npm/three@0.157.0/examples/jsm/controls/OrbitControls.js';

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffffff);

// Kamera & Renderer
const camera = new THREE.PerspectiveCamera(55, window.innerWidth/window.innerHeight, 1, 20000);
const camDist = {RAD} * 2.3;
camera.position.set(camDist, camDist * 0.6, camDist);
camera.lookAt(0, 0, 0);

const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Licht
const dirLight = new THREE.DirectionalLight(0xffffff, 1.1);
dirLight.position.set(1000, 1500, 1000);
scene.add(dirLight);
scene.add(new THREE.AmbientLight(0xffffff, 0.8));

// Grid (Bodenlinie)
const grid = new THREE.GridHelper({RAD * 3}, 40, 0x999999, 0xcccccc);
scene.add(grid);

// Coil
const RID = {RID}, RAD = {RAD}, WIDTH = {WIDTH};
const shape = new THREE.Shape();
shape.absarc(0, 0, RAD, 0, Math.PI * 2, false);
const hole = new THREE.Path();
hole.absarc(0, 0, RID, 0, Math.PI * 2, true);
shape.holes.push(hole);

const extrudeSettings = {{ depth: WIDTH, bevelEnabled: false, steps: 1 }};
const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
geometry.rotateX(-Math.PI / 2);
geometry.translate(0, WIDTH / 2, 0);

const material = new THREE.MeshStandardMaterial({{
  color: 0xb7b7b7,
  metalness: 0.7,
  roughness: 0.25
}});

const coil = new THREE.Mesh(geometry, material);
scene.add(coil);

// Orbit Controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enablePan = false;
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.target.set(0, WIDTH / 2, 0);
controls.update();

function animate() {{
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}}
animate();

// Fenstergröße anpassen
window.addEventListener('resize', () => {{
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}});
</script>
</body>
</html>
"""

components.html(threejs_html, height=800)
