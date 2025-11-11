import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Palette – Minimal", layout="wide")

st.title("🪵 EU-Palette 1200 × 800 mm (ohne Coil)")
st.caption("Nur Palette – neutraler Hintergrund, Orbit-Drehung nur um Y-Achse.")

threejs_html = """
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8" />
<style>
  html, body {
    margin: 0;
    overflow: hidden;
    background: #484852;  /* neutral dunkelgrau */
    width: 100%;
    height: 100%;
  }
  canvas { display: block; width: 100%; height: 100%; }
</style>
</head>
<body>
<script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.157.0/examples/js/controls/OrbitControls.js"></script>

<script>
// ===== Grundsetup =====
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x484852);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 1, 60000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// ===== Licht =====
const sun = new THREE.DirectionalLight(0xffffff, 1.1);
sun.position.set(2000, 2500, 2000);
scene.add(sun);
const fill = new THREE.DirectionalLight(0xfff0e0, 0.4);
fill.position.set(-1600, 600, -1200);
scene.add(fill);
scene.add(new THREE.HemisphereLight(0xffffff, 0xdde8ff, 0.35));
scene.add(new THREE.AmbientLight(0xffffff, 0.25));

// ===== Boden (neutral) =====
const floorMat = new THREE.MeshPhongMaterial({ color: 0x3a3a40, shininess: 10 });
const floor = new THREE.Mesh(new THREE.PlaneGeometry(10000, 10000), floorMat);
floor.rotation.x = -Math.PI / 2;
floor.receiveShadow = true;
scene.add(floor);

// ===== Palette 1200×800×144 mm =====
const PAL_W = 1200, PAL_D = 800, PAL_H = 144;
const palMat = new THREE.MeshPhongMaterial({ color: 0xc69c6d }); // Holzfarben
const pallet = new THREE.Mesh(new THREE.BoxGeometry(PAL_W, PAL_H, PAL_D), palMat);
pallet.position.y = PAL_H / 2;
pallet.castShadow = pallet.receiveShadow = true;
scene.add(pallet);

// ===== Orbit-Steuerung (nur Y-Achse) =====
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enablePan = false;
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minPolarAngle = Math.PI/2 - 0.04;
controls.maxPolarAngle = Math.PI/2 + 0.04;

// ===== Auto-Framing =====
function frameObject(obj) {
  const box = new THREE.Box3().setFromObject(obj);
  const size = new THREE.Vector3(); box.getSize(size);
  const center = new THREE.Vector3(); box.getCenter(center);

  const fov = camera.fov * Math.PI / 180;
  const maxDim = Math.max(size.x, size.y, size.z);
  let dist = (maxDim / 2) / Math.tan(fov / 2);
  dist *= 2.2;

  controls.target.copy(center);
  camera.position.set(center.x + dist, center.y + dist * 0.35, center.z + dist);
  camera.lookAt(center);
  controls.minDistance = dist * 0.6;
  controls.maxDistance = dist * 3.0;
  controls.update();
}
frameObject(pallet);

// ===== Render-Loop =====
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();

// ===== Resize =====
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
"""

components.html(threejs_html, height=760)
