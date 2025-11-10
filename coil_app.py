import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D-Coil – Clean (ohne Raum)", layout="wide")

# ---- Parameter (mm) ----
st.sidebar.title("Coil Parameter")
RID   = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD   = st.sidebar.slider("Außenradius (mm)", 600, 1600, 800, step=10)
WIDTH = st.sidebar.slider("Breite (mm)", 8, 600, 300, step=1)
MATERIAL = st.sidebar.selectbox("Material", ["Stahl", "Kupfer", "Aluminium"], index=0)

color_map = {
    "Stahl": "0x9a9a9a",
    "Kupfer": "0xb87333",
    "Aluminium": "0xcfcfcf",
}

st.title("🌀 3D-Coil – Clean (ohne Raum)")
st.caption("Maus: drehen (nur Y-Achse) · Mausrad: zoomen · Kamera passt sich automatisch an.")

threejs_html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8" />
<style>
  html, body {{
    margin: 0;
    overflow: hidden;
    background: #0d0d0d; /* dunkel, aber nicht tiefschwarz */
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
// ===== Szene, Kamera, Renderer =====
const scene   = new THREE.Scene();
scene.background = new THREE.Color(0x0d0d0d);

const camera  = new THREE.PerspectiveCamera(55, window.innerWidth/window.innerHeight, 1, 60000);
const renderer= new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// ===== Licht (neutral & sichtbar) =====
const key = new THREE.DirectionalLight(0xffffff, 1.2);
key.position.set(2000, 2200, 1600);
key.castShadow = true;
scene.add(key);

const fill = new THREE.DirectionalLight(0xfff0e0, 0.5);
fill.position.set(-1600, 800, -1200);
scene.add(fill);

const hemi = new THREE.HemisphereLight(0xffffff, 0xcfe0ff, 0.45);
scene.add(hemi);

const amb  = new THREE.AmbientLight(0xffffff, 0.25);
scene.add(amb);

// ===== (Optional) Boden für Schatten – extrem dezent =====
const groundMat = new THREE.ShadowMaterial({{ opacity: 0.15 }});
const ground    = new THREE.Mesh(new THREE.PlaneGeometry(20000, 20000), groundMat);
ground.rotation.x = -Math.PI/2;
ground.position.y = 0;
ground.receiveShadow = true;
scene.add(ground);

// ===== Coil (vertikal stehend) =====
const RID   = {RID};
const RAD   = {RAD};
const WIDTH = {WIDTH};
const segments = 256;

const shape = new THREE.Shape();
shape.absarc(0, 0, RAD, 0, Math.PI*2, false, segments);
const hole  = new THREE.Path();
hole.absarc(0, 0, RID, 0, Math.PI*2, true, segments);
shape.holes.push(hole);

const geom = new THREE.ExtrudeGeometry(shape, {{ depth: WIDTH, bevelEnabled: false, curveSegments: 128 }});
// aufrecht stellen + auf den Boden setzen
geom.rotateZ(Math.PI/2);
geom.translate(0, RAD, 0);
geom.computeVertexNormals();

const mat = new THREE.MeshPhongMaterial({{
  color: {color_map[MATERIAL]},
  shininess: 130,
  reflectivity: 0.85,
  specular: 0xffffff
}});
const coil = new THREE.Mesh(geom, mat);
coil.castShadow = coil.receiveShadow = true;
scene.add(coil);

// ===== OrbitControls: nur Y-Achse, kein Pan =====
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enablePan = false;
controls.enableDamping = true;
controls.dampingFactor = 0.06;
// Blick waagerecht einklemmen:
controls.minPolarAngle = Math.PI/2 - 0.04;
controls.maxPolarAngle = Math.PI/2 + 0.04;

// ===== Auto-Framing (passt Zoom/Distanz an) =====
function frameCoil() {{
  // Bounding Box des Coils
  const box = new THREE.Box3().setFromObject(coil);
  const size = new THREE.Vector3(); box.getSize(size);
  const center = new THREE.Vector3(); box.getCenter(center);

  const fov = camera.fov * Math.PI/180;
  const maxDim = Math.max(size.x, size.y, size.z);
  let dist = (maxDim/2) / Math.tan(fov/2);
  dist *= 2.1; // etwas Luft

  const targetY = center.y;
  controls.target.set(center.x, targetY, center.z);
  camera.position.set(center.x + dist, targetY + dist*0.35, center.z + dist);
  camera.lookAt(controls.target);

  controls.minDistance = dist*0.6;
  controls.maxDistance = dist*3.0;
  controls.update();
}}
frameCoil();

// ===== Render-Loop =====
function animate() {{
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}}
animate();

// ===== Resize =====
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
