import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Coil – Sichtbar & Clean", layout="wide")

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

st.title("🌀 Coil – einfache 3D-Ansicht")
st.caption("Nur Coil – heller Hintergrund, keine Palette, kein Raum. Sichtbarkeit garantiert.")

threejs_html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<style>
  html, body {{
    margin: 0;
    overflow: hidden;
    background: #ffffff; /* Weißer Hintergrund */
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
// ===== Szene =====
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffffff);

// ===== Kamera =====
const camera = new THREE.PerspectiveCamera(55, window.innerWidth/window.innerHeight, 1, 10000);
camera.position.set(2000, 1000, 2000);
camera.lookAt(0,0,0);

// ===== Renderer =====
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// ===== Licht =====
const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
dirLight.position.set(1500, 2000, 1500);
scene.add(dirLight);
scene.add(new THREE.AmbientLight(0xffffff, 0.5));

// ===== Coil =====
const RID = {RID};
const RAD = {RAD};
const WIDTH = {WIDTH};

const shape = new THREE.Shape();
shape.absarc(0, 0, RAD, 0, Math.PI * 2, false);
const hole = new THREE.Path();
hole.absarc(0, 0, RID, 0, Math.PI * 2, true);
shape.holes.push(hole);

const extrude = new THREE.ExtrudeGeometry(shape, {{
  depth: WIDTH,
  bevelEnabled: false,
  curveSegments: 128
}});
extrude.rotateZ(Math.PI / 2);
extrude.translate(0, RAD, 0);

const material = new THREE.MeshPhongMaterial({{
  color: {color_map[MATERIAL]},
  shininess: 120,
  reflectivity: 0.8,
  specular: 0xffffff
}});

const coil = new THREE.Mesh(extrude, material);
scene.add(coil);

// ===== Steuerung =====
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.enablePan = false;

// ===== Render-Loop =====
function animate() {{
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}}
animate();

// ===== Resize =====
window.addEventListener('resize', () => {{
  camera.aspect = window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}});
</script>
</body>
</html>
"""

components.html(threejs_html, height=760)
