import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="3D Coil – Python + Three.js", layout="wide")

# ---------------------- Sidebar ----------------------
st.sidebar.title("Coil Parameter")

RID = st.sidebar.slider("Innenradius (mm)", 150, 500, 300, step=10)
RAD = st.sidebar.slider("Außenradius (mm)", 600, 1600, 800, step=10)
WIDTH = st.sidebar.slider("Breite (mm)", 8, 600, 300, step=1)
THK = st.sidebar.slider("Dicke (mm)", 0.1, 5.0, 1.0, step=0.1)
DENSITY = st.sidebar.selectbox(
    "Materialdichte",
    [("Stahl", 7.85), ("Kupfer", 8.96), ("Aluminium", 2.70)],
    index=0
)

material, rho = DENSITY
coil_volume = math.pi * (RAD**2 - RID**2) * WIDTH  # mm³
coil_weight = coil_volume * rho / 1e6              # g → kg
coil_length = 2 * math.pi * (RAD + RID) / 2        # mm (mittlere Länge)

st.sidebar.markdown(f"""
**Material:** {material}  
**Volumen:** {coil_volume:,.0f} mm³  
**Gewicht:** {coil_weight:,.2f} kg  
**Mittlere Länge:** {coil_length:,.0f} mm
""")

# ---------------------- Three.js Szene ----------------------
threejs_html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<style>
  html, body {{
    margin: 0;
    overflow: hidden;
    background: #ffffff;
    width: 100%;
    height: 100%;
  }}
  canvas {{
    display: block;
    width: 100vw;
    height: 100vh;
  }}
</style>
</head>
<body>
<script type="module">
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.module.js';
import {{ OrbitControls }} from 'https://cdn.jsdelivr.net/npm/three@0.157.0/examples/jsm/controls/OrbitControls.js';

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffffff);

// ---------- Kamera ----------
const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 1, 10000);
const camDist = {RAD} * 2.5;
camera.position.set(camDist, camDist * 0.5, camDist);
camera.lookAt(0, 0, 0);

// ---------- Renderer ----------
const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

// ---------- Licht ----------
const light = new THREE.DirectionalLight(0xffffff, 1.0);
light.position.set(1000, 1500, 1000);
scene.add(light);
scene.add(new THREE.AmbientLight(0xffffff, 0.6));

// ---------- Coil ----------
const RID = {RID}, RAD = {RAD}, WIDTH = {WIDTH};
const shape = new THREE.Shape();
shape.absarc(0, 0, RAD, 0, Math.PI * 2, false);
const hole = new THREE.Path();
hole.absarc(0, 0, RID, 0, Math.PI * 2, true);
shape.holes.push(hole);

const extrudeSettings = {{ steps: 1, depth: WIDTH, bevelEnabled: false }};
const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
geometry.rotateX(-Math.PI / 2);
geometry.translate(0, WIDTH / 2, 0);

const material = new THREE.MeshStandardMaterial({{
  color: 0xb87333,
  metalness: 0.8,
  roughness: 0.25
}});

const coil = new THREE.Mesh(geometry, material);
scene.add(coil);

// ---------- Boden ----------
const floorGeo = new THREE.CircleGeometry(RAD * 2, 64);
const floorMat = new THREE.MeshStandardMaterial({{ color: 0xeeeeee }});
const floor = new THREE.Mesh(floorGeo, floorMat);
floor.rotation.x = -Math.PI / 2;
scene.add(floor);

// ---------- Steuerung ----------
const controls = new OrbitControls(camera, renderer.domElement);
controls.enablePan = false;
controls.target.set(0, WIDTH / 2, 0);
controls.update();

// ---------- Renderloop ----------
function animate() {{
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}}
animate();

window.addEventListener('resize', () => {{
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}});
</script>
</body>
</html>
"""

# ---------------------- Darstellung ----------------------
components.html(threejs_html, height=900)
