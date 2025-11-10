import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Coil im Lagerraum", layout="wide")

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

st.title("🏭 Coil im Lagerraum")
st.caption("Fixe Kamera, Coil steht vertikal und dreht sich um die Y-Achse – mit realistischem Raum.")

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

// 📷 Kamera etwas weiter weg für mehr Raumtiefe
const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 1, 20000);
camera.position.set(2000, 1000, 2000);
camera.lookAt(0, 500, 0);

// --- Renderer ---
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// --- Licht ---
const sun = new THREE.DirectionalLight(0xffffff, 1.0);
sun.position.set(1500, 2000, 1500);
sun.castShadow = true;
scene.add(sun);

const fillLight = new THREE.DirectionalLight(0xfff0e0, 0.4);
fillLight.position.set(-1200, 400, -800);
scene.add(fillLight);

const hemi = new THREE.HemisphereLight(0xddeeff, 0xffffff, 0.3);
scene.add(hemi);
scene.add(new THREE.AmbientLight(0xffffff, 0.25));

// --- Lagerraum (Boden, Wände, Decke) ---
const roomSize = 4000;
const wallMat = new THREE.MeshPhongMaterial({{ color: 0xeeeeee, side: THREE.BackSide }});
const roomGeo = new THREE.BoxGeometry(roomSize, roomSize * 0.6, roomSize);
const room = new THREE.Mesh(roomGeo, wallMat);
room.position.y = roomSize * 0.3; // Boden auf y=0
room.receiveShadow = true;
scene.add(room);

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
geometry.rotateZ(Math.PI / 2);
geometry.translate(0, RAD, 0);
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
  coil.rotation.y += 0.01; // Drehgeschwindigkeit
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
