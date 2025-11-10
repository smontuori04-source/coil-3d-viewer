import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="3D Coil im Raum", layout="wide")

st.sidebar.title("Coil Parameter")
RID = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD = st.sidebar.slider("Außenradius (mm)", 600, 1600, 800, step=10)
WIDTH = st.sidebar.slider("Breite (mm)", 8, 600, 300, step=1)
THK = st.sidebar.slider("Dicke (mm)", 0.1, 5.0, 1.0, step=0.1)
MATERIAL = st.sidebar.selectbox("Material", ["Stahl", "Kupfer", "Aluminium"], index=1)

# Materialfarben
color_map = {
    "Stahl": "0x888888",
    "Kupfer": "0xb87333",
    "Aluminium": "0xaaaaaa"
}

st.title("🏭 Coil im Lagerraum")
st.caption("Fixe Kamera, fester Raum, Coil zentriert – keine automatische Bewegung.")

threejs_html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<style>
  html, body {{
    margin: 0;
    overflow: hidden;
    background: #e0e0e0;
    width: 100%;
    height: 100%;
  }}
  canvas {{ display: block; width: 100%; height: 100%; }}
</style>
</head>
<body>
<script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>

<script>
// --- Szene ---
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf5f5f5);

// --- Kamera ---
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 1, 10000);
camera.position.set(1200, 800, 1200);
camera.lookAt(0, 200, 0);

// --- Renderer ---
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

// --- Licht ---
const light = new THREE.DirectionalLight(0xffffff, 1.2);
light.position.set(1000, 1500, 1000);
light.castShadow = true;
light.shadow.mapSize.width = 2048;
light.shadow.mapSize.height = 2048;
scene.add(light);
scene.add(new THREE.AmbientLight(0xffffff, 0.5));

// --- Raum / Lagerumgebung ---
const floorGeo = new THREE.PlaneGeometry(4000, 4000);
const floorMat = new THREE.MeshPhongMaterial({{ color: 0xdddddd }});
const floor = new THREE.Mesh(floorGeo, floorMat);
floor.rotation.x = -Math.PI / 2;
floor.receiveShadow = true;
scene.add(floor);

// Wände
function makeWall(x, z, rot) {{
  const wallGeo = new THREE.PlaneGeometry(4000, 2000);
  const wallMat = new THREE.MeshPhongMaterial({{ color: 0xe8e8e8 }});
  const wall = new THREE.Mesh(wallGeo, wallMat);
  wall.position.set(x, 1000, z);
  wall.rotation.y = rot;
  wall.receiveShadow = true;
  scene.add(wall);
}}
makeWall(0, -2000, 0);
makeWall(-2000, 0, Math.PI / 2);

// --- Coil ---
const RID = {RID}, RAD = {RAD}, WIDTH = {WIDTH};
const outerShape = new THREE.Shape();
outerShape.absarc(0, 0, RAD, 0, Math.PI * 2, false);
const innerHole = new THREE.Path();
innerHole.absarc(0, 0, RID, 0, Math.PI * 2, true);
outerShape.holes.push(innerHole);
const extrudeSettings = {{ depth: WIDTH, bevelEnabled: false }};
const geometry = new THREE.ExtrudeGeometry(outerShape, extrudeSettings);
geometry.rotateX(-Math.PI / 2);
geometry.translate(0, WIDTH / 2, 0);

const material = new THREE.MeshPhongMaterial({{
  color: {color_map[MATERIAL]},
  shininess: 90,
  reflectivity: 0.5
}});
const coil = new THREE.Mesh(geometry, material);
coil.castShadow = true;
coil.receiveShadow = true;
scene.add(coil);

// --- Render Loop ---
function animate() {{
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}}
animate();

// --- Resize ---
window.addEventListener('resize', () => {{
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}});
</script>
</body>
</html>
"""

components.html(threejs_html, height=750)
