import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="3D Coil – Stabiler Renderer", layout="wide")

st.sidebar.title("Coil Parameter")
RID = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD = st.sidebar.slider("Außenradius (mm)", 600, 1600, 800, step=10)
WIDTH = st.sidebar.slider("Breite (mm)", 8, 600, 300, step=1)
THK = st.sidebar.slider("Dicke (mm)", 0.1, 5.0, 1.0, step=0.1)
DENSITY = st.sidebar.selectbox(
    "Materialdichte",
    [("Stahl", 7.85), ("Kupfer", 8.96), ("Aluminium", 2.70)],
    index=0,
)

material, rho = DENSITY
coil_volume = math.pi * (RAD**2 - RID**2) * WIDTH
coil_weight = coil_volume * rho / 1e6
st.sidebar.markdown(f"**Gewicht:** {coil_weight:,.2f} kg")

st.title("🌀 3D Coil Vorschau")
st.caption("Diese Version nutzt denselben Renderer wie beim roten Würfel (stabil in Streamlit).")

threejs_html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<style>
  html, body {{
    margin: 0;
    overflow: hidden;
    background: #cccccc;
    width: 100%;
    height: 100%;
  }}
  canvas {{ display: block; width: 100%; height: 100%; }}
</style>
</head>
<body>
<div id="container"></div>

<script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>

<script>
// Szene + Kamera
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xcccccc);
const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 1, 20000);
camera.position.set(2000, 1000, 2000);
camera.lookAt(0, 0, 0);

// Renderer
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Licht
const light = new THREE.DirectionalLight(0xffffff, 1.3);
light.position.set(1500, 2000, 1000);
scene.add(light);
scene.add(new THREE.AmbientLight(0xffffff, 0.5));

// Grid
const grid = new THREE.GridHelper(4000, 40, 0x888888, 0x444444);
scene.add(grid);

// ---- Coil ----
const RID = {RID}, RAD = {RAD}, WIDTH = {WIDTH};

// Außenform
const outerShape = new THREE.Shape();
outerShape.absarc(0, 0, RAD, 0, Math.PI * 2, false);

// Innenloch
const innerHole = new THREE.Path();
innerHole.absarc(0, 0, RID, 0, Math.PI * 2, true);
outerShape.holes.push(innerHole);

// Extrusion (Tiefe = Breite)
const extrudeSettings = {{ depth: WIDTH, bevelEnabled: false }};
const geometry = new THREE.ExtrudeGeometry(outerShape, extrudeSettings);
geometry.rotateX(-Math.PI / 2);
geometry.translate(0, WIDTH / 2, 0);

// Material
const material = new THREE.MeshPhongMaterial({{ color: 0xb7b7b7, shininess: 80 }});
const coil = new THREE.Mesh(geometry, material);
scene.add(coil);

// Animation (leichte Rotation)
function animate() {{
  requestAnimationFrame(animate);
  coil.rotation.y += 0.01;
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

components.html(threejs_html, height=700)
