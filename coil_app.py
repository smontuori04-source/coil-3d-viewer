import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Coil im Raum mit Regal, Kartons & Männchen", layout="wide")

# ---- Sidebar-Parameter (mm) ----
st.sidebar.title("Coil Parameter")
RID = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD = st.sidebar.slider("Außenradius (mm)", 600, 1600, 800, step=10)
WIDTH = st.sidebar.slider("Breite (mm)", 8, 600, 300, step=1)
MATERIAL = st.sidebar.selectbox("Material", ["Stahl", "Kupfer", "Aluminium"], index=0)

color_map = {
    "Stahl": "0x9a9a9a",
    "Kupfer": "0xb87333",
    "Aluminium": "0xcfcfcf",
}

st.title("🏭 Coil im Raum – mit Regal, Kartons & 1,80 m Männchen")
st.caption("Maus: drehen (nur um Y-Achse) · Mausrad: zoomen · Kamera passt sich an Coil + Männchen an.")

threejs_html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8" />
<style>
  html, body {{
    margin: 0;
    overflow: hidden;
    background: #0d0d0d; /* dunkler, neutraler Hintergrund */
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
// ===== Szene & Renderer =====
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0d0d0d);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth/window.innerHeight, 1, 60000);
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// ===== Licht (hell, aber neutral) =====
const sun = new THREE.DirectionalLight(0xffffff, 1.1);
sun.position.set(3200, 3600, 2600);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
scene.add(sun);

scene.add(new THREE.DirectionalLight(0xfff2e0, 0.45)).position.set(-2500, 1200, -1800);
scene.add(new THREE.HemisphereLight(0xffffff, 0xdde6ff, 0.4));
scene.add(new THREE.AmbientLight(0xffffff, 0.25));

// ===== Raum (Box innen) + Boden =====
const roomSize = 6000;                // mm – großer, heller Raum
const roomGeo  = new THREE.BoxGeometry(roomSize, roomSize*0.6, roomSize);
const roomMat  = new THREE.MeshPhongMaterial({{color:0x202225, side:THREE.BackSide}}); // dunkle Halle
const room     = new THREE.Mesh(roomGeo, roomMat);
room.position.y = roomSize*0.3;       // Boden auf y=0
scene.add(room);

const floorGeo = new THREE.PlaneGeometry(roomSize, roomSize);
const floorMat = new THREE.MeshPhongMaterial({{color:0x1b1d20, shininess:25}});
const floor    = new THREE.Mesh(floorGeo, floorMat);
floor.rotation.x = -Math.PI/2;
floor.receiveShadow = true;
scene.add(floor);

// ===== Hilfsfunktionen für Deko =====
function addShelf(x, z) {{
  const g = new THREE.Group();
  const uprMat = new THREE.MeshPhongMaterial({{color:0xaeb3b8}});
  const beamMat= new THREE.MeshPhongMaterial({{color:0xc9cdd1}});
  const upr1 = new THREE.Mesh(new THREE.BoxGeometry(40,1000,40), uprMat);
  const upr2 = upr1.clone();
  upr1.position.set(-300,500,0); upr2.position.set(300,500,0);
  const board = new THREE.Mesh(new THREE.BoxGeometry(700,30,400), beamMat);
  const b2 = board.clone(), b3 = board.clone();
  board.position.set(0,300,0); b2.position.set(0,600,0); b3.position.set(0,900,0);
  g.add(upr1,upr2,board,b2,b3);
  g.position.set(x,0,z);
  g.traverse(o=>{{o.castShadow=o.receiveShadow=true;}});
  scene.add(g);
}}

function addBox(x,y,z, w,h,d, c) {{
  const m = new THREE.MeshPhongMaterial({{color:c}});
  const b = new THREE.Mesh(new THREE.BoxGeometry(w,h,d), m);
  b.position.set(x,y,z);
  b.castShadow = b.receiveShadow = true;
  scene.add(b);
}}

function addBarrel(x,z,c) {{
  const m = new THREE.MeshPhongMaterial({{color:c, shininess:60}});
  const b = new THREE.Mesh(new THREE.CylinderGeometry(250,250,700,48), m);
  b.position.set(x,350,z);
  b.castShadow = b.receiveShadow = true;
  scene.add(b);
}}

// Platzierung Regale/Kartons/Fässer
addShelf(-2000,-1200);
addShelf( 1800, -800);

addBox(-2050,  45, -900, 400,90,300, 0x8d805f);
addBox(-1850,  45, -900, 400,90,300, 0x947b55);
addBox(-1950, 135, -900, 400,90,300, 0x9b875f);

addBarrel(-400,  950, 0x3a6ea5);
addBarrel( -50, 1050, 0x8a2d2d);
addBarrel( 250,  950, 0x2d8a51);

// ===== Coil (vertikal) =====
const RID   = {RID};
const RAD   = {RAD};
const WIDTH = {WIDTH};
const segments = 256;

const shape = new THREE.Shape();
shape.absarc(0,0,RAD,0,Math.PI*2,false,segments);
const hole  = new THREE.Path();
hole.absarc(0,0,RID,0,Math.PI*2,true,segments);
shape.holes.push(hole);

const extrude = new THREE.ExtrudeGeometry(shape, {{depth:WIDTH, bevelEnabled:false, curveSegments:128}});
extrude.rotateZ(Math.PI/2);      // aufrecht stellen
extrude.translate(0,RAD,0);      // auf den Boden stellen (Unterkante ~0)
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

// ===== Männchen (1.800 mm) =====
const guy = new THREE.Group();
const H = 1800; // mm
const skin = new THREE.MeshPhongMaterial({{color:0xd8b39b}});
const cloth= new THREE.MeshPhongMaterial({{color:0x6b7a8f}});
const head = new THREE.Mesh(new THREE.SphereGeometry(90,24,18), skin);
const body = new THREE.Mesh(new THREE.CapsuleGeometry(180, 500, 8, 16), cloth);
const legL = new THREE.Mesh(new THREE.CylinderGeometry(75,75,700,16), cloth);
const legR = legL.clone();
head.position.y = H - 90;
body.position.y = H - 90 - 350;
legL.position.set(-90, 350, 0);
legR.position.set( 90, 350, 0);
guy.add(head, body, legL, legR);

// neben den Coil (links davon), mit etwas Abstand:
const gap = 200; // mm Abstand
guy.position.set(-(RAD + gap), 0, 0);
guy.traverse(o=>{{o.castShadow = o.receiveShadow = true;}});
scene.add(guy);

// ===== OrbitControls (nur Y-Achse) =====
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enablePan = false;
controls.minPolarAngle = Math.PI/2 - 0.04;
controls.maxPolarAngle = Math.PI/2 + 0.04;
controls.enableDamping = true;
controls.dampingFactor = 0.06;

// ===== Kamera: Auto-Framing für Coil + Männchen =====
function frameObjects() {{
  const group = new THREE.Group();
  group.add(coil.clone());
  group.add(guy.clone());
  scene.add(group);
  const box = new THREE.Box3().setFromObject(group);
  scene.remove(group);

  const size = new THREE.Vector3(); box.getSize(size);
  const center = new THREE.Vector3(); box.getCenter(center);

  const fov = camera.fov * Math.PI/180;
  const maxDim = Math.max(size.x, size.y, size.z);
  let dist = (maxDim/2) / Math.tan(fov/2);
  dist *= 2.0; // etwas Luft
  const targetY = center.y;
  controls.target.set(center.x, targetY, center.z);
  camera.position.set(center.x + dist, targetY + dist*0.35, center.z + dist);
  camera.lookAt(controls.target);

  controls.minDistance = dist*0.6;
  controls.maxDistance = dist*3.0;
  controls.update();
}}
frameObjects();

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
