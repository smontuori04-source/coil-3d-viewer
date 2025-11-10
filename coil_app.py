import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Coil – Sichtbarkeitstest", layout="wide")

st.title("🧪 Sichtbarkeitstest für Three.js-Coil")
st.write("Jetzt sollte der Coil garantiert sichtbar sein (grauer Hintergrund + starkes Licht).")

threejs_html = """
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<style>
  html, body { margin: 0; overflow: hidden; background: #000000; width: 100%; height: 100%; }
  canvas { display: block; width: 100%; height: 100%; }
</style>
</head>
<body>
<script type="module">
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.157.0/examples/jsm/controls/OrbitControls.js';

// Szene
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x202020); // Dunkelgrau

// Kamera
const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 1, 20000);
camera.position.set(2000, 1000, 2000);
camera.lookAt(0, 0, 0);

// Renderer
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

// Licht
const light = new THREE.DirectionalLight(0xffffff, 1.3);
light.position.set(1500, 2000, 1000);
scene.add(light);
scene.add(new THREE.AmbientLight(0xffffff, 0.4));

// Testobjekte (sichtbare Referenzen)
const axes = new THREE.AxesHelper(1000);
scene.add(axes);

// Boden
const grid = new THREE.GridHelper(4000, 40, 0x888888, 0x444444);
scene.add(grid);

// Coil – feste Werte
const RID = 300, RAD = 800, WIDTH = 300;
const shape = new THREE.Shape();
shape.absarc(0, 0, RAD, 0, Math.PI * 2, false);
const hole = new THREE.Path();
hole.absarc(0, 0, RID, 0, Math.PI * 2, true);
shape.holes.push(hole);
const extrudeSettings = { depth: WIDTH, bevelEnabled: false };
const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
geometry.rotateX(-Math.PI / 2);
geometry.translate(0, WIDTH / 2, 0);
const material = new THREE.MeshStandardMaterial({
  color: 0xb7b7b7,
  metalness: 0.8,
  roughness: 0.25
});
const coil = new THREE.Mesh(geometry, material);
scene.add(coil);

// Orbit Controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enablePan = false;
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.target.set(0, WIDTH / 2, 0);
controls.update();

// Animation
function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}
animate();

// Resize
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
"""

components.html(threejs_html, height=800)
