import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Vertikaler Coil mit Rotation", layout="wide")

st.sidebar.title("Coil Parameter")
RID = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD = st.sidebar.slider("Außenradius (mm)", 600, 1600, 800, step=10)
WIDTH = st.sidebar.slider("Breite (mm)", 8, 600, 300, step=1)
MATERIAL = st.sidebar.selectbox("Material", ["Stahl", "Kupfer", "Aluminium"], index=1)

color_map = {
    "Stahl": "0x999999",
    "Kupfer": "0xb87333",
    "Aluminium": "0xd0d0d0"
}

st.title("🌀 Vertikaler, rotierender Coil im Raum")
st.caption("Der Coil steht vertikal (wie eine echte Rolle) und dreht sich sanft um seine Y-Achse.")

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
scene.background = new THREE.Color(0xf5f5f5);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 1, 10000);
camera.position.set(1200, 800, 1200);
camera.lookAt(0, 400, 0);

// --- Renderer ---
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// --- Licht ---
const sun = new THREE.DirectionalLight(0xffffff, 1.0);
sun.position.set(1000, 1500, 1000);
sun.castShadow = true;
scene.add(sun);

const fillLight = new THREE.DirectionalLight(0xfff0e0, 0.4);
fillLight.position.set(-800, 400, -800);
scene.add(fillLight);

const hemi = new THREE.HemisphereLight(0xddeeff, 0xffffff, 0.3);
scene.add(hemi);

scene.add(new THREE.AmbientLight(0xffffff, 0.25));

// --- Boden ---
const floorGeo = new THREE.PlaneGeometry(4000, 4000);
const floorMat = new THREE.MeshPhongMaterial({{ color: 0xeeeeee, shininess: 40 }});
const floor = new THREE.Mesh(floorGeo, floorMat);
floor.rotation.x = -Math.PI / 2;
floor.receiveShadow = true;
scene.add(floor);

// --- Coil (vertikal stehend) ---
const RID = {RID}, RAD = {RAD}, WIDTH = {WIDTH};
const segments = 256;

const outerShape = new THREE.Shape();
outerShape.absarc(0, 0, RAD, 0, Math.PI * 2, false, segments);
const innerHole = new THREE.Path();
innerHole.absarc(0, 0, RID, 0, Math.PI * 2, true, segments);
outerShape.holes.push(innerHole);

const extrudeSettings = {{ depth: WIDTH, bevelEnabled: false, curveSegments: 128 }};
const geometry = new THREE.ExtrudeGeometry(outerShape, extrudeSettings);

// 🔁 Der Coil soll vertikal stehen (wie eine echte Rolle):
geometry.rotateZ(Math.PI / 2); // um 90° kippen
geometry.translate(0, RAD, 0); // leicht anheben, damit er nicht im Boden verschwindet
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

// --- Animation (Rotation um Y-Achse) ---
function animate() {{
  requestAnimationFrame(animate);
  coil.rotation.y += 0.01; // Geschwindigkeit der Rotation
  renderer.render(scene, camera);
}}
animate();

// --- Fenster-Resize ---
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
