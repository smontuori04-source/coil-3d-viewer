import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Coil auf Palette – Clean", layout="wide")

# ---- Sidebar (mm) ----
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

# Palettenmaß: EU 1200x800 oder Einweg 1200x1200 – hier 1200x1200 (wie gewünscht)
PAL_W, PAL_D, PAL_H = 1200, 1200, 144  # Breite, Tiefe, Höhe in mm

st.title("🛠️ Coil auf Palette (ohne Raum)")
st.caption("Nur Boden + Palette + Coil. Hintergrund dunkel – kein weiß. Y-Drehung & Auto-Zoom aktiv.")

threejs_html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8" />
<style>
  html, body {{
    margin: 0;
    overflow: hidden;
    background: #484852; /* KEIN WEISS */
    width: 100%;
    height: 100%;
  }}
  canvas {{ display:block; width:100%; height:100%; }}
</style>
</head>
<body>
<!-- THREE core + OrbitControls (nicht-modular, stabil für Streamlit) -->
<script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.157.0/examples/js/controls/OrbitControls.js"></script>

<script>
// ===== Szene / Kamera / Renderer =====
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x484852); // KEIN WEISS

const camera   = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 1, 60000);
const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// ===== Licht (hell, aber neutral) =====
const sun = new THREE.DirectionalLight(0xffffff, 1.05);
sun.position.set(2500, 3000, 2200);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
scene.add(sun);

const fill = new THREE.DirectionalLight(0xfff0e0, 0.45);
fill.position.set(-1600, 800, -1200);
scene.add(fill);

scene.add(new THREE.HemisphereLight(0xffffff, 0xdfe8ff, 0.35));
scene.add(new THREE.AmbientLight(0xffffff, 0.22));

// ===== Boden (dunkel, dezent), plus Schattenebene =====
const groundColor = new THREE.MeshPhongMaterial({{ color: 0x3a3a40, shininess: 10 }});
const groundPlane = new THREE.Mesh(new THREE.PlaneGeometry(20000, 20000), groundColor);
groundPlane.rotation.x = -Math.PI / 2;
groundPlane.receiveShadow = true;
scene.add(groundPlane);

const shadowMat = new THREE.ShadowMaterial({{ opacity: 0.18 }});
const shadowPlane = new THREE.Mesh(new THREE.PlaneGeometry(20000, 20000), shadowMat);
shadowPlane.rotation.x = -Math.PI / 2;
shadowPlane.receiveShadow = true;
scene.add(shadowPlane);

// ===== Palette (massives Deck) =====
const PAL_W = {PAL_W}, PAL_D = {PAL_D}, PAL_H = {PAL_H};
const palMat = new THREE.MeshPhongMaterial({{ color: 0xc69c6d }});
const pallet = new THREE.Mesh(new THREE.BoxGeometry(PAL_W, PAL_H, PAL_D), palMat);
pallet.position.set(0, PAL_H/2, 0);
pallet.castShadow = pallet.receiveShadow = true;
scene.add(pallet);

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

const extrude = new THREE.ExtrudeGeometry(shape, {{ depth: WIDTH, bevelEnabled: false, curveSegments: 128 }});
extrude.rotateZ(Math.PI/2);              // aufrecht
extrude.translate(0, PAL_H + RAD, 0);    // auf Palette stellen
extrude.computeVertexNormals();

const coilMat = new THREE.MeshPhongMaterial({{
  color: {color_map[MATERIAL]},
  shininess: 120,
  reflectivity: 0.8,
  specular: 0xffffff
}});
const coil = new THREE.Mesh(extrude, coilMat);
coil.castShadow = coil.receiveShadow = true;
scene.add(coil);

// ===== OrbitControls: nur Y-Achse, kein Pan =====
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enablePan = false;
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minPolarAngle = Math.PI/2 - 0.04;
controls.maxPolarAngle = Math.PI/2 + 0.04;

// ===== Auto-Framing: Coil + Palette gemeinsam =====
function frameAll() {{
  const group = new THREE.Group();
  group.add(coil.clone());
  group.add(pallet.clone());
  scene.add(group);
  const box = new THREE.Box3().setFromObject(group);
  scene.remove(group);

  const size = new THREE.Vector3(); box.getSize(size);
  const center = new THREE.Vector3(); box.getCenter(center);

  const fov = camera.fov * Math.PI/180;
  const maxDim = Math.max(size.x, size.y, size.z);
  let dist = (maxDim/2) / Math.tan(fov/2);
  dist *= 2.2;  // Luft

  controls.target.copy(center);
  camera.position.set(center.x + dist, center.y + dist*0.35, center.z + dist);
  camera.lookAt(center);

  controls.minDistance = dist*0.6;
  controls.maxDistance = dist*3.0;
  controls.update();

  // Boden & Schatten auf y=0 lassen
  groundPlane.position.y = 0;
  shadowPlane.position.y = 0;
}}
frameAll();

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
