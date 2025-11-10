import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="3D Coil im Raum (Smooth)", layout="wide")

st.sidebar.title("Coil Parameter")
RID = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD = st.sidebar.slider("Außenradius (mm)", 600, 1600, 800, step=10)
WIDTH = st.sidebar.slider("Breite (mm)", 8, 600, 300, step=1)
THK = st.sidebar.slider("Dicke (mm)", 0.1, 5.0, 1.0, step=0.1)
MATERIAL = st.sidebar.selectbox("Material", ["Stahl", "Kupfer", "Aluminium"], index=1)

color_map = {
    "Stahl": "0x888888",
    "Kupfer": "0xb87333",
    "Aluminium": "0xaaaaaa"
}

st.title("🏭 Glatter Coil im fixen Raum")
st.caption("Fixe Kamera, glatte Oberfläche, Coil bleibt zentriert.")

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
// --- Szene & Kamera ---
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf7f7f7);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 1, 10000);
camera.position.set(1200, 800, 1200);
camera.lookAt(0, 200, 0);

// --- Renderer ---
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

// --- Licht ---
const light = new THREE.DirectionalLight(0xffffff, 1.1);
light.position.set(1000, 1500, 1000);
light.castShadow = true;
scene.add(light);
scene.add(new THREE.AmbientLight(0xffffff, 0.5));

// --- Raum ---
const floorGeo = new THREE.PlaneGeometry(4000, 4000);
const floorMat = new THREE.MeshPhongMaterial({{ color: 0xdddddd }});
const floor = new THREE.Mesh(floorGeo, floorMat);
floor.rotation.x = -Math.PI / 2;
floor.receiveShadow = true;
scene.add(floor);

function makeWall(x, z, rot) {{
  const wallGeo = new THREE.PlaneGeometry(4000, 2000, 1, 1);
  const wallMat = new THREE.MeshPhongMaterial({{ color: 0xeaeaea }});
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
const segments = 256; // ⬅️ höhere Auflösung für glatte Rundung

const outerShape = new THREE.Shape();
outerShape.absarc(0, 0, RAD, 0, Math.PI * 2, false, segments);

const innerHole = new THREE.Path();
innerHole.absarc(0, 0, RID, 0, Math.PI * 2, true, segments);
outerShape.holes.push(innerHole);

const extrudeSettings = {{ depth: WIDTH, bevelEnabled: false, curveSegments: 128 }};
const geometry = new THREE.ExtrudeGeometry(outerShape, extrudeSettings);
geometry.rotateX(-Math.PI / 2);
geometry.translate(0, WIDTH / 2, 0);
geometry.computeVertexNormals();

// --- Material ---
const material = new THREE.MeshPhongMaterial({{
  color: {color_map[MATERIAL]},
  shininess: 100,
  reflectivity: 0.6,
  specular: 0xffffff
}});
const coil = new THREE.Mesh(geometry, material);
coil.castShadow = true;
coil.receiveShadow = true;
scene.add(coil);

// --- Render ---
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
