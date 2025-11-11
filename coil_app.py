import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Testfläche – Minimal", layout="wide")

st.title("⬛ Flache Testplatte (anstelle der Palette)")
st.caption("Nur eine flache rechteckige Platte – kein Raum, kein Coil, manuelle Drehung.")

threejs_html = """
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8" />
<style>
  html, body {
    margin: 0;
    overflow: hidden;
    background: #484852;  /* neutraler dunkler Hintergrund */
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
// ===== Szene, Kamera, Renderer =====
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
scene.add(new THREE.AmbientLight(0xffffff, 0.3));

// ===== Platte (anstelle Palette) =====
const PLATTE_W = 1200, PLATTE_D = 800, PLATTE_H = 20;
const mat = new THREE.MeshPhongMaterial({ color: 0x777777, shininess: 40 });
const plate = new THREE.Mesh(new THREE.BoxGeometry(PLATTE_W, PLATTE_H, PLATTE_D), mat);
plate.position.y = PLATTE_H / 2;
scene.add(plate);

// ===== Orbit Controls =====
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
frameObject(plate);

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
