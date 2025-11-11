import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Coil – Nur Coil", layout="wide")

# --- Parameter ---
st.sidebar.title("Coil Parameter")
RID   = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD   = st.sidebar.slider("Außenradius (mm)", 600, 1600, 800, step=10)
WIDTH = st.sidebar.slider("Breite (mm)", 8, 600, 300, step=1)
MATERIAL = st.sidebar.selectbox("Material", ["Stahl", "Kupfer", "Aluminium"], index=0)

color_map = {
    "Stahl": "0x999999",
    "Kupfer": "0xb87333",
    "Aluminium": "0xd0d0d0"
}

st.title("🌀 3D-Coil – Hintergrundfrei, nur das Objekt")

threejs_html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8" />
<style>
  html, body {{
    margin: 0;
    overflow: hidden;
    background: transparent;
    width: 100%;
    height: 100%;
  }}
  canvas {{ display:block; width:100%; height:100%; background: transparent; }}
</style>
</head>
<body>
<script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.157.0/examples/js/controls/OrbitControls.js"></script>

<script>
// === Szene ===
const scene = new THREE.Scene();

// === Kamera ===
const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 1, 100000);
const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(0x000000, 0);
document.body.appendChild(renderer.domElement);

// === Licht ===
const key = new THREE.DirectionalLight(0xffffff, 1.2);
key.position.set(2000, 2000, 1600);
scene.add(key);
scene.add(new THREE.AmbientLight(0xffffff, 0.4));

// === Coil ===
const RID = {RID}, RAD = {RAD}, WIDTH = {WIDTH};
const shape = new THREE.Shape();
shape.absarc(0, 0, RAD, 0, Math.PI * 2, false);
const hole = new THREE.Path();
hole.absarc(0, 0, RID, 0, Math.PI * 2, true);
shape.holes.push(hole);

const geom = new THREE.ExtrudeGeometry(shape, {{ depth: WIDTH, bevelEnabled: false, curveSegments: 128 }});
geom.rotateZ(Math.PI / 2);
geom.translate(0, RAD, 0);
geom.computeVertexNormals();

const mat = new THREE.MeshPhongMaterial({{
  color: {color_map[MATERIAL]},
  shininess: 120,
  reflectivity: 0.8,
  specular: 0xffffff
}});
const coil = new THREE.Mesh(geom, mat);
scene.add(coil);

// === Kamera-Steuerung ===
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.enablePan = false;

// === Kamera-Autoanpassung ===
function frameCoil() {{
  const box = new THREE.Box3().setFromObject(coil);
  const size = new THREE.Vector3(); box.getSize(size);
  const center = new THREE.Vector3(); box.getCenter(center);
  const fov = camera.fov * Math.PI / 180;
  const maxDim = Math.max(size.x, size.y, size.z);
  let dist = (maxDim / 2) / Math.tan(fov / 2);
  dist *= 2.0;

  controls.target.copy(center);
  camera.position.set(center.x + dist, center.y + dist * 0.4, center.z + dist);
  camera.lookAt(center);
  controls.minDistance = dist * 0.5;
  controls.maxDistance = dist * 3.0;
  controls.update();
}}
frameCoil();

// === Render ===
function animate() {{
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}}
animate();

// === Resize ===
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
