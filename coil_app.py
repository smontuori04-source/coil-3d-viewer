import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Coil – Reset (Minimal)", layout="wide")

# --- einfache Parameter (mm) ---
st.sidebar.title("Coil Parameter")
RID   = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD   = st.sidebar.slider("Außenradius (mm)", 600, 1600, 800, step=10)
WIDTH = st.sidebar.slider("Breite (mm)", 8, 600, 300, step=1)

st.title("🌀 3D-Coil – Minimaler Reset (sicher sichtbar)")
st.caption("Nur Coil + Licht. Keine Wände, keine Controls. Sanfte Rotation für Sichtbarkeits-Check.")

threejs_html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<style>
  html, body {{
    margin: 0;
    overflow: hidden;
    background: #484852; /* neutral hellgrau – nicht reinweiß */
    width: 100%;
    height: 100%;
  }}
  canvas {{ display:block; width:100%; height:100%; }}
</style>
</head>
<body>
<!-- Nur der stabile, nicht-modulare Build -->
<script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>

<script>
// ===== Szene/Kamera/Renderer =====
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x484852);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth/window.innerHeight, 1, 20000);
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

// ===== Licht =====
const key = new THREE.DirectionalLight(0xffffff, 1.15);
key.position.set(2000, 2200, 1600);
key.castShadow = true;
scene.add(key);

const fill = new THREE.DirectionalLight(0xfff0e0, 0.45);
fill.position.set(-1600, 800, -1000);
scene.add(fill);

scene.add(new THREE.HemisphereLight(0xffffff, 0xdde8ff, 0.4));
scene.add(new THREE.AmbientLight(0xffffff, 0.25));

// ===== dezente Schattenfläche =====
const floor = new THREE.Mesh(new THREE.PlaneGeometry(20000, 20000), new THREE.ShadowMaterial({{opacity:0.15}}));
floor.rotation.x = -Math.PI/2;
floor.receiveShadow = true;
scene.add(floor);

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
geom.rotateZ(Math.PI/2);   // aufrecht
geom.translate(0, RAD, 0); // auf "Boden" stellen
geom.computeVertexNormals();

const mat = new THREE.MeshPhongMaterial({{
  color: 0x9a9a9a,
  shininess: 120,
  reflectivity: 0.8,
  specular: 0xffffff
}});
const coil = new THREE.Mesh(geom, mat);
coil.castShadow = coil.receiveShadow = true;
scene.add(coil);

// ===== Kamera automatisch passend setzen =====
(function frameCoil(){{
  const box = new THREE.Box3().setFromObject(coil);
  const size = new THREE.Vector3(); box.getSize(size);
  const center = new THREE.Vector3(); box.getCenter(center);

  const fov = camera.fov * Math.PI/180;
  const maxDim = Math.max(size.x, size.y, size.z);
  let dist = (maxDim/2) / Math.tan(fov/2);
  dist *= 2.0; // Luft

  camera.position.set(center.x + dist, center.y + dist*0.35, center.z + dist);
  camera.lookAt(center);
}})();

// ===== sanfte Rotation zur Sichtprüfung =====
function animate(){{
  requestAnimationFrame(animate);
  coil.rotation.y += 0.00005; // langsam
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
