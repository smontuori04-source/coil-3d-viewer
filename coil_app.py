import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Coil im neutralen Raum", layout="wide")

st.sidebar.title("Coil Parameter")
RID = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD = st.sidebar.slider("Außenradius (mm)", 600, 1600, 800, step=10)
WIDTH = st.sidebar.slider("Breite (mm)", 8, 600, 300, step=1)
MATERIAL = st.sidebar.selectbox("Material", ["Stahl", "Kupfer", "Aluminium"], index=1)

color_map = {
    "Stahl": "0x999999",
    "Kupfer": "0xb87333",
    "Aluminium": "0xc0c0c0"
}

st.title("🏭 Coil im neutralen Raum (dunkel)")
st.caption("Dunkler Raum, metallischer Coil, keine weißen Wände – Fokus auf das Objekt.")

threejs_html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<style>
  html, body {{
    margin: 0;
    overflow: hidden;
    background: #0d0d0d; /* sehr dunkler Hintergrund */
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
scene.background = new THREE.Color(0x0d0d0d); // Dunkler Hintergrund, kein Weiß

const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 1, 20000);
camera.position.set(1800, 1000, 1800);
camera.lookAt(0, 400, 0);

// --- Renderer ---
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// --- Lichtsystem ---
const mainLight = new THREE.SpotLight(0xffffff, 1.5, 5000, Math.PI / 4, 0.3);
mainLight.position.set(1500, 2000, 1000);
mainLight.target.position.set(0, 300, 0);
mainLight.castShadow = true;
scene.add(mainLight);
scene.add(mainLight.target);

// Weiches Streiflicht von der anderen Seite
const sideLight = new THREE.DirectionalLight(0xaaaaff, 0.4);
sideLight.position.set(-1000, 800, -800);
scene.add(sideLight);

// Fülllicht von vorne – simuliert indirekte Halle-Beleuchtung
const frontLight = new THREE.DirectionalLight(0xffffff, 0.5);
frontLight.position.set(0, 600, 1500);
scene.add(frontLight);

// Sanftes Umgebungslicht für Details
const ambient = new THREE.AmbientLight(0x444444, 0.7);
scene.add(ambient);

// --- Boden ---
const floorGeo = new THREE.PlaneGeometry(4000, 4000);
const floorMat = new THREE.MeshPhongMaterial({{
  color: 0x1a1a1a,
  shininess: 20,
  reflectivity: 0.3
}});
const floor = new THREE.Mesh(floorGeo, floorMat);
floor.rotation.x = -Math.PI / 2;
floor.receiveShadow = true;
scene.add(floor);

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
geometry.rotateZ(Math.PI / 2);
geometry.translate(0, RAD, 0);
geometry.computeVertexNormals();

const material = new THREE.MeshPhongMaterial({{
  color: {color_map[MATERIAL]},
  shininess: 140,
  reflectivity: 1.0,
  specular: 0xffffff
}});
const coil = new THREE.Mesh(geometry, material);
coil.castShadow = true;
coil.receiveShadow = true;
scene.add(coil);

// --- Animation ---
function animate() {{
  requestAnimationFrame(animate);
  coil.rotation.y += 0.01;
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
