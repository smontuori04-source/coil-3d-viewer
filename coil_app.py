import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Three.js Sichtbarkeitstest", layout="wide")

st.title("🧩 Sichtbarkeitstest für Three.js")
st.write("Wenn du hier etwas Rotes siehst, funktioniert der Renderer korrekt.")

threejs_html = """
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<style>
  html, body { margin: 0; overflow: hidden; background: #cccccc; width: 100%; height: 100%; }
  canvas { display: block; width: 100%; height: 100%; }
</style>
</head>
<body>
<script type="module">
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.module.js';

// Szene
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xcccccc);

// Kamera
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 1, 5000);
camera.position.set(0, 0, 1000);

// Renderer
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Testobjekt: Roter Würfel
const geometry = new THREE.BoxGeometry(200, 200, 200);
const material = new THREE.MeshBasicMaterial({ color: 0xff0000 });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

// Animation
function animate() {
  requestAnimationFrame(animate);
  cube.rotation.x += 0.01;
  cube.rotation.y += 0.01;
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

components.html(threejs_html, height=600)
