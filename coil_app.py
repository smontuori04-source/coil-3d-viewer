import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Coil auf Palette", layout="wide")

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

st.title("🪵 Coil auf Palette – einfach & sichtbar")

threejs_html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8" />
<style>
  html, body {{
    margin: 0;
    overflow: hidden;
    background: #f4f4f4; /* heller neutraler Hintergrund */
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
// === Szene & Kamera ===
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf4f4f4);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 1, 100000);
const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// === Licht ===
const key = new THREE.DirectionalLight(0xffffff, 1.1);
key.position.set(2000, 2000, 1800);
scene.add(key);
scene.add(new THREE.AmbientLight(0xffffff, 0.4));

// === Palette (1200x800x144 mm) ===
const PAL_W = 1200, PAL_D = 800, PAL_H = 144;
const palMat = new THREE.MeshPhongMaterial({{ color: 0xc69c6d }});
const pallet = new THREE.Mesh(new THREE.BoxGeometry(PAL_W, PAL_H, PAL_D), palMat);
pallet.position.y = PAL_H / 2;
scene.add(pallet);

// === Coil (vertikal stehend) ===
const RID = {RID}, RAD = {RAD}, WIDTH = {WIDTH};
const shape = new THREE.Shape();
shape.absarc(0, 0, RAD, 0, Math.PI * 2, false);
const hole = new THREE.Path();
hole.absarc(0, 0, RID, 0, Math.PI * 2, true);
shape.holes.push(hole);

const geom = new THREE.ExtrudeGeometry(shape, {{ depth: WIDTH, bevelEnabled: false, curveSegments: 128 }});
geom.rotateZ(Math.PI / 2);
geom.translate(0, PAL_H + RAD, 0);
geom.computeVertexNormals();

const mat = new THREE.MeshPhongMaterial({{
  color: {color_map[MATERIAL]},
  shininess: 120,
  reflectivity: 0.8,
  specular: 0xffffff
}});
const coil = new THREE.Mesh(geom, mat);
scene.add(coil);

// === Kamera-Setup ===
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.enablePan = false;

function frameAll() {{
  const group = new THREE.Group();
  group.add(coil.clone());
  group.add(pallet.clone());
  scene.add(group);
  const box = new THREE.Box3().setFromObject(group);
  scene.remove(group);

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
frameAll();

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
