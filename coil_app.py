import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Coil – Weißer Raum mit Auto-Zoom", layout="wide")

# ---- Parameter (mm) ----
st.sidebar.title("Coil Parameter")
RID   = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD   = st.sidebar.slider("Außenradius (mm)", 600, 1600, 800, step=10)
WIDTH = st.sidebar.slider("Breite (mm)", 8, 600, 300, step=1)
MATERIAL = st.sidebar.selectbox("Material", ["Stahl", "Kupfer", "Aluminium"], index=1)

color_map = {
    "Stahl": "0x999999",
    "Kupfer": "0xb87333",
    "Aluminium": "0xd0d0d0",
}

st.title("🏭 3D-Coil – Weißer Raum, manuelle Drehung, Auto-Zoom")
st.caption("Wände wieder aktiv (weiß). Drehung per Maus nur um Y-Achse, Zoom passt sich automatisch an.")

threejs_html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<style>
  html, body {{
    margin: 0;
    overflow: hidden;
    background: #ffffff; /* Seite weiß */
    width: 100%;
    height: 100%;
  }}
  canvas {{ display:block; width:100%; height:100%; }}
</style>
</head>
<body>
<!-- THREE core + OrbitControls (nicht modulare Builds für Streamlit) -->
<script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.157.0/examples/js/controls/OrbitControls.js"></script>

<script>
// ===== Grundsetup =====
const SCALE = 1.5; // Raum-/Kamera-Verhältnis wie gewünscht (1.5x)
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffffff); // Raumhintergrund weiß

const camera = new THREE.PerspectiveCamera(55, window.innerWidth/window.innerHeight, 1, 50000*SCALE);
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// ===== Licht (hell, neutral) =====
const sun = new THREE.DirectionalLight(0xffffff, 1.05);
sun.position.set(3000*SCALE, 3500*SCALE, 2500*SCALE);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
scene.add(sun);

const fill = new THREE.DirectionalLight(0xfff2e0, 0.45);
fill.position.set(-2500*SCALE, 1200*SCALE, -2000*SCALE);
scene.add(fill);

const hemi = new THREE.HemisphereLight(0xffffff, 0xdfe8ff, 0.4);
scene.add(hemi);
const ambient = new THREE.AmbientLight(0xffffff, 0.25);
scene.add(ambient);

// ===== Weißer Raum (Box innen) =====
const roomSize = 4000 * SCALE;
const roomGeo  = new THREE.BoxGeometry(roomSize, roomSize*0.6, roomSize);
const roomMat  = new THREE.MeshPhongMaterial({{ color: 0xffffff, side: THREE.BackSide }});
const room     = new THREE.Mesh(roomGeo, roomMat);
room.position.y = roomSize*0.3; // Boden auf y=0
room.receiveShadow = true;
scene.add(room);

// leicht abgesetzter weißer Boden für Schatten
const floorGeo = new THREE.PlaneGeometry(roomSize, roomSize);
const floorMat = new THREE.MeshPhongMaterial({{ color: 0xf2f2f2, shininess: 20 }});
const floor    = new THREE.Mesh(floorGeo, floorMat);
floor.rotation.x = -Math.PI/2;
floor.receiveShadow = true;
scene.add(floor);

// ===== Coil (vertikal), mm-Maße =====
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
geom.rotateZ(Math.PI/2);      // aufrecht stellen
geom.translate(0, RAD, 0);    // auf Boden stellen
geom.computeVertexNormals();

const mat = new THREE.MeshPhongMaterial({{
  color: {color_map[MATERIAL]},
  shininess: 120,
  reflectivity: 0.8,
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
// Blick waagerecht fest (nur um Y drehen)
controls.minPolarAngle = Math.PI/2 - 0.04;
controls.maxPolarAngle = Math.PI/2 + 0.04;

// ===== Auto-Zoom / Framing: immer komplett sichtbar =====
function frameCoil() {{
  // Bounding Box des Coils
  const box = new THREE.Box3().setFromObject(coil);
  const size = new THREE.Vector3(); box.getSize(size);
  const center = new THREE.Vector3(); box.getCenter(center);

  // Distanz aus größter Ausdehnung + FOV berechnen
  const fov = camera.fov * Math.PI/180;
  const maxDim = Math.max(size.x, size.y, size.z);
  let dist = (maxDim/2) / Math.tan(fov/2);
  dist *= 2.2; // etwas Luft

  // Ziel und Kamera setzen
  controls.target.copy(center);
  camera.position.set(center.x + dist, center.y + dist*0.35, center.z + dist);
  camera.lookAt(center);

  // sinnvolle Zoomgrenzen
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
