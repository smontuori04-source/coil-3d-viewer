import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Coil – ohne Wände, mit Auto-Zoom", layout="wide")

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

st.title("🌀 3D-Coil – Freistehend, mit automatischem Zoom")
st.caption("Kein Raum, kein Auto-Drehen. Kamera passt sich automatisch an die Coil-Größe an.")

threejs_html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<style>
  html, body {{
    margin: 0;
    overflow: hidden;
    background: #e6e6e6;
    width: 100%;
    height: 100%;
  }}
  canvas {{ display:block; width:100%; height:100%; }}
</style>
</head>
<body>
<script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.157.0/examples/js/controls/OrbitControls.js"></script>

<script>
// --- Szene, Kamera, Renderer ---
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xe6e6e6);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 1, 20000);
const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

// --- Licht ---
const sun = new THREE.DirectionalLight(0xffffff, 1.0);
sun.position.set(2000, 2500, 2000);
sun.castShadow = true;
scene.add(sun);

const fillLight = new THREE.DirectionalLight(0xfff0e0, 0.5);
fillLight.position.set(-1500, 800, -1000);
scene.add(fillLight);

scene.add(new THREE.HemisphereLight(0xffffff, 0xddeeff, 0.4));
scene.add(new THREE.AmbientLight(0xffffff, 0.3));

// --- Boden (leichter Schatten) ---
const floorMat = new THREE.ShadowMaterial({{ opacity: 0.15 }});
const floor = new THREE.Mesh(new THREE.PlaneGeometry(10000, 10000), floorMat);
floor.rotation.x = -Math.PI / 2;
floor.position.y = 0;
floor.receiveShadow = true;
scene.add(floor);

// --- Coil ---
const RID = {RID}, RAD = {RAD}, WIDTH = {WIDTH};
const segments = 256;

const shape = new THREE.Shape();
shape.absarc(0, 0, RAD, 0, Math.PI * 2, false, segments);
const hole = new THREE.Path();
hole.absarc(0, 0, RID, 0, Math.PI * 2, true, segments);
shape.holes.push(hole);

const extrudeSettings = {{ depth: WIDTH, bevelEnabled: false, curveSegments: 128 }};
const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
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

// --- Kamera & Steuerung ---
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enablePan = false;
controls.enableDamping = true;
controls.dampingFactor = 0.06;

// Drehung nur um Y-Achse
controls.minPolarAngle = Math.PI / 2 - 0.04;
controls.maxPolarAngle = Math.PI / 2 + 0.04;

// --- Automatische Anpassung des Zooms ---
function frameCoil() {{
  const box = new THREE.Box3().setFromObject(coil);
  const size = new THREE.Vector3();
  box.getSize(size);
  const center = new THREE.Vector3();
  box.getCenter(center);

  const fov = camera.fov * Math.PI / 180;
  const maxDim = Math.max(size.x, size.y, size.z);
  let dist = (maxDim / 2) / Math.tan(fov / 2);
  dist *= 2.0; // etwas Luft

  controls.target.copy(center);
  camera.position.set(center.x + dist, center.y + dist * 0.35, center.z + dist);
  camera.lookAt(center);

  controls.minDistance = dist * 0.6;
  controls.maxDistance = dist * 3.0;
  controls.update();
}}

frameCoil();

// --- Animation ---
function animate() {{
  requestAnimationFrame(animate);
  controls.update();
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

components.html(threejs_html, height=760)
