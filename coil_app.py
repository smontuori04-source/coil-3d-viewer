import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="3D Coil mit Licht", layout="wide")

st.sidebar.title("Coil Parameter")
RID = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD = st.sidebar.slider("Außenradius (mm)", 600, 1600, 800, step=10)
WIDTH = st.sidebar.slider("Breite (mm)", 8, 600, 300, step=1)
THK = st.sidebar.slider("Dicke (mm)", 0.1, 5.0, 1.0, step=0.1)
MATERIAL = st.sidebar.selectbox("Material", ["Stahl", "Kupfer", "Aluminium"], index=1)

color_map = {
    "Stahl": "0x999999",
    "Kupfer": "0xb87333",
    "Aluminium": "0xd0d0d0"
}

st.title("💡 3D Coil im beleuchteten Raum")
st.caption("Mit Hauptlicht, Fülllicht und weichen Reflexionen – Coil bleibt fix im Raum.")

threejs_html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<style>
  html, body {{
    margin: 0;
    overflow: hidden;
    background: #dcdcdc;
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
scene.background = new THREE.Color(0xf4f4f4);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 1, 10000);
camera.position.set(1200, 800, 1200);
camera.lookAt(0, 200, 0);

// --- Renderer ---
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// --- Lichtsystem ---
// Hauptlicht (Sonnenlicht)
const sun = new THREE.DirectionalLight(0xffffff, 1.0);
sun.position.set(1000, 1800, 1000);
sun.castShadow = true;
sun.shadow.mapSize.width = 2048;
sun.shadow.mapSize.height = 2048;
sun.shadow.camera.near = 0.5;
sun.shadow.camera.far = 4000;
scene.add(sun);

// Fülllicht (weiches Licht von der Seite)
const fillLight = new THREE.DirectionalLight(0xfff0e0, 0.4);
fillLight.position.set(-1000, 500, -800);
scene.add(fillLight);

// Bodenreflexlicht (leicht bläulich)
const bounce = new THREE.HemisphereLight(0xcfdfff, 0xffffff, 0.3);
scene.add(bounce);

// Umgebungslicht
scene.add(new THREE.AmbientLight(0xffffff, 0.2));

// --- Raum ---
const floorGeo = new THREE.PlaneGeometry(4000, 4000);
const floorMat = new THREE.MeshPhongMaterial({{ color: 0xeeeeee, shininess: 30 }});
const floor = new THREE.Mesh(floorGeo, floorMat);
floor.rotation.x = -Math.PI / 2;
floor.receiveShadow = true;
scene.add(floor);

function makeWall(x, z, rot) {{
  const wallGeo = new THREE.PlaneGeometry(4000, 2000);
  const wallMat = new THREE.MeshPhongMaterial({{ color: 0xededed, shininess: 10 }});
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
const segments = 256;

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

const material = new THREE.MeshPhongMaterial({{
  color: {color_map[MATERIAL]},
  shininess: 120,
  reflectivity: 0.8,
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
