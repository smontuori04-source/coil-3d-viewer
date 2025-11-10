import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Coil im hellen Lagerraum (steuerbar)", layout="wide")

st.sidebar.title("Coil Parameter")
RID = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD = st.sidebar.slider("Außenradius (mm)", 600, 1600, 800, step=10)
WIDTH = st.sidebar.slider("Breite (mm)", 8, 600, 300, step=1)
MATERIAL = st.sidebar.selectbox("Material", ["Stahl", "Kupfer", "Aluminium"], index=1)

color_map = {
    "Stahl": "0x9a9a9a",
    "Kupfer": "0xb87333",
    "Aluminium": "0xcfcfcf"
}

st.title("🏭 Coil im hellen Lagerraum – steuerbar")
st.caption("Heller Raum mit Requisiten. Maus: drehen (nur um Y-Achse) · Mausrad: zoomen · kein Pan. Kamera passt sich an die Coil-Größe an.")

threejs_html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<style>
  html, body {{
    margin: 0;
    overflow: hidden;
    background: #e9ecef;
    width: 100%;
    height: 100%;
  }}
  canvas {{ display: block; width: 100%; height: 100%; }}
</style>
</head>
<body>
<script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.157.0/examples/js/controls/OrbitControls.js"></script>

<script>
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf7f7f7);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 1, 50000);
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const sun = new THREE.DirectionalLight(0xffffff, 1.05);
sun.position.set(3000, 3500, 2500);
sun.castShadow = true;
scene.add(sun);

const fill = new THREE.DirectionalLight(0xfff2e0, 0.5);
fill.position.set(-2500, 1200, -2000);
scene.add(fill);

const hemi = new THREE.HemisphereLight(0xffffff, 0xe0e0ff, 0.45);
scene.add(hemi);

const ambient = new THREE.AmbientLight(0xffffff, 0.25);
scene.add(ambient);

// Raum
const roomSize = 6000;
const roomGeo = new THREE.BoxGeometry(roomSize, roomSize * 0.6, roomSize);
const roomMat = new THREE.MeshPhongMaterial({{ color: 0xf0f0f0, side: THREE.BackSide }});
const room = new THREE.Mesh(roomGeo, roomMat);
room.position.y = (roomSize * 0.6) / 2;
room.receiveShadow = true;
scene.add(room);

const floorGeo = new THREE.PlaneGeometry(roomSize, roomSize);
const floorMat = new THREE.MeshPhongMaterial({{ color: 0xeeeeee, shininess: 30 }});
const floor = new THREE.Mesh(floorGeo, floorMat);
floor.rotation.x = -Math.PI / 2;
floor.receiveShadow = true;
scene.add(floor);

function addShelf(x, z) {{
  const shelf = new THREE.Group();
  const upr = new THREE.Mesh(new THREE.BoxGeometry(40, 1000, 40), new THREE.MeshPhongMaterial({{color:0xc9c9c9}}));
  const upr2 = upr.clone(); upr.position.set(-300, 500, 0); upr2.position.set(300, 500, 0);
  const boardMat = new THREE.MeshPhongMaterial({{color:0xd9d9d9}});
  const board1 = new THREE.Mesh(new THREE.BoxGeometry(700, 30, 400), boardMat); board1.position.set(0, 300, 0);
  const board2 = board1.clone(); board2.position.y = 600;
  const board3 = board1.clone(); board3.position.y = 900;
  shelf.add(upr, upr2, board1, board2, board3);
  shelf.position.set(x, 0, z);
  shelf.castShadow = shelf.receiveShadow = true;
  scene.add(shelf);
}}
addShelf(-1800, -1200);
addShelf(2000, -800);

function addPallet(x, z) {{
  const wood = new THREE.MeshPhongMaterial({{color:0xc69c6d}});
  const deck = new THREE.Mesh(new THREE.BoxGeometry(1200, 60, 800), wood);
  deck.position.set(x, 30, z);
  deck.receiveShadow = deck.castShadow = true;
  scene.add(deck);
}}
addPallet(-800, 900);
addPallet(900, 1100);

function addBarrel(x, z, c) {{
  const body = new THREE.MeshPhongMaterial({{color:c, shininess:60}});
  const cyl = new THREE.Mesh(new THREE.CylinderGeometry(250, 250, 700, 48), body);
  cyl.position.set(x, 350, z);
  cyl.castShadow = cyl.receiveShadow = true;
  scene.add(cyl);
}}
addBarrel(-300, 1000, 0x3a6ea5);
addBarrel(-100, 1000, 0x8a2d2d);
addBarrel(100, 1000, 0x2d8a51);

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

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enablePan = false;
controls.minPolarAngle = Math.PI/2 - 0.05;
controls.maxPolarAngle = Math.PI/2 + 0.05;
controls.enableDamping = true;
controls.dampingFactor = 0.06;

function frameCoil() {{
  const targetY = RAD;
  controls.target.set(0, targetY, 0);
  const fov = camera.fov * Math.PI/180;
  const coilMax = Math.max(RAD*2, WIDTH);
  let dist = coilMax / (2*Math.tan(fov/2));
  dist *= 2.2;
  camera.position.set(dist, targetY + dist*0.35, dist);
  camera.lookAt(0, targetY, 0);
  controls.minDistance = dist*0.6;
  controls.maxDistance = dist*3.2;
  controls.update();
}}
frameCoil();

function animate() {{
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}}
animate();

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
