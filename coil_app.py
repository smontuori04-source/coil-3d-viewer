import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Sichtbarkeitstest", layout="wide")

st.title("👀 Sichtbarkeitstest – Kleine Box im 3D-Raum")
st.caption("Kleine Box, stark beleuchtet, Kamera sehr nah. Sollte IMMER sichtbar sein.")

threejs_html = """
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<style>
  html, body {
    margin: 0;
    overflow: hidden;
    background: #202020;
    width: 100%;
    height: 100%;
  }
  canvas { display:block; width:100%; height:100%; }
</style>
</head>
<body>
<script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.157.0/examples/js/controls/OrbitControls.js"></script>

<script>
// --- Szene ---
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x202020);

// --- Kamera ---
const camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 10000);
camera.position.set(3, 2, 3);

// --- Renderer ---
const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// --- Licht ---
const light1 = new THREE.PointLight(0xffffff, 1.5);
light1.position.set(5, 5, 5);
scene.add(light1);
scene.add(new THREE.AmbientLight(0xffffff, 0.3));

// --- Testbox ---
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshPhongMaterial({color: 0x44aa88, shininess: 80});
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

// --- OrbitControls ---
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// --- Renderloop ---
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();

// --- Resize ---
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
