import streamlit as st
import streamlit.components.v1 as components

RID, RAD, WIDTH = 300, 800, 300
# Beispiel: Zuschnittberechnung in Python
length = 2 * 3.1416 * ((RID + RAD) / 2)

st.write(f"Zuschnittlänge: {length:.2f} mm")

# Übergib Python-Werte an Three.js Szene
threejs_html = f"""
<script type="module">
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.module.js';
import {{ OrbitControls }} from 'https://cdn.jsdelivr.net/npm/three@0.157.0/examples/jsm/controls/OrbitControls.js';

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffffff);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth/window.innerHeight, 1, 10000);
camera.position.set(1500, 800, 1500);
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const light = new THREE.DirectionalLight(0xffffff, 1.0);
light.position.set(1000,1500,1000);
scene.add(light);
scene.add(new THREE.AmbientLight(0xffffff,0.6));

// Coil
const RID = {RID}, RAD = {RAD}, WIDTH = {WIDTH};
const shape = new THREE.Shape();
shape.absarc(0,0,RAD,0,Math.PI*2,false);
const hole = new THREE.Path();
hole.absarc(0,0,RID,0,Math.PI*2,true);
shape.holes.push(hole);

const extrudeSettings = {{ steps: 1, depth: WIDTH, bevelEnabled: false }};
const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
geometry.rotateX(-Math.PI/2);
geometry.translate(0, WIDTH/2, 0);
const material = new THREE.MeshStandardMaterial({{ color:0xb87333, metalness:0.8, roughness:0.25 }});
const coil = new THREE.Mesh(geometry, material);
scene.add(coil);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enablePan = false;

function animate() {{
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}}
animate();
</script>
"""

components.html(threejs_html, height=600)
