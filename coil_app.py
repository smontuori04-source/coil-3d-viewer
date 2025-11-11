import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Testbox", layout="wide")

st.title("📦 3D-Testbox (sichtbarer Quader)")
st.caption("Nur eine Box im Raum – kein Raum, kein Coil. 3D-Ansicht mit Maus drehbar.")

threejs_html = """
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8" />
<style>
  html, body {
    margin: 0;
    overflow: hidden;
    background: #484852; /* neutral dunkel */
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
// === Szene, Kamera, Renderer ===
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x484852);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth/window.innerHeight, 1, 10000);
const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// === Licht ===
const light = new THREE.DirectionalLight(0xffffff, 1.2);
light.position.set(1000, 1000, 800);
scene.add(light);
scene.add(new THREE.AmbientLight(0xffffff, 0.4));

// === 3D-Box ===
const W=1200, H=200, D=800;
const geometry = new THREE.BoxGeometry(W, H, D);
const material = new THREE.MeshPhongMaterial({
  color: 0x888888,
  shininess: 100,
  reflectivity: 0.5
});
const box = new THREE.Mesh(geometry, material);
box.castShadow = true;
box.receiveShadow = true;
scene.add(box);

// === Kamera initial setzen ===
camera.position.set(1800, 900, 1800);
camera.lookAt(0,0,0);

// === OrbitControls ===
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enablePan = false;
controls.enableDamping = true;
controls.dampingFactor = 0.06;

// === Render-Loop ===
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();

// === Resize ===
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
"""

components.html(threejs_html, height=760)
