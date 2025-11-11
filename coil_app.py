import math
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Coil – Berechnung & Zuschnitte", layout="wide")

# --- Sidebar: Eingabeparameter ---
st.sidebar.title("Coil Parameter")
RID   = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD   = st.sidebar.slider("Außenradius (mm)", 600, 1600, 800, step=10)
WIDTH = st.sidebar.slider("Breite (mm)", 8, 600, 300, step=1)
MATERIAL = st.sidebar.selectbox("Material", ["Stahl", "Kupfer", "Aluminium"], index=0)

# Dichte in g/mm³
density_map = {
    "Stahl": 0.00785,
    "Kupfer": 0.00896,
    "Aluminium": 0.00270
}

rho = density_map[MATERIAL]

st.title("🌀 Coil-Berechnung und Zuschnittplanung")
st.caption("Basierend auf Material, Geometrie und gewünschten Zuschnittbreiten")

# --- Coil Berechnung ---
volume_mm3 = math.pi * (RAD**2 - RID**2) * WIDTH
weight_g = volume_mm3 * rho
weight_kg = weight_g / 1000
kg_per_mm = weight_kg / WIDTH

col1, col2, col3 = st.columns(3)
col1.metric("Gesamtgewicht", f"{weight_kg:,.0f} kg")
col2.metric("Gewicht pro mm", f"{kg_per_mm:,.2f} kg/mm")
col3.metric("Volumen", f"{volume_mm3/1e9:,.2f} dm³")

# --- Zuschnitt-Eingabe ---
st.subheader("✂️ Zuschnittbreiten eingeben")
cuts_input = st.text_input("Trenne mehrere Zuschnitte mit Komma (,)", "100, 200, 250")

try:
    cuts = [float(x.strip()) for x in cuts_input.split(",") if x.strip()]
    sum_cuts = sum(cuts)
    cut_weights = [kg_per_mm * c for c in cuts]
    total_cut_weight = sum(cut_weights)
    rest_width = WIDTH - sum_cuts
    rest_weight = kg_per_mm * rest_width if rest_width > 0 else 0

    df = pd.DataFrame({
        "Zuschnitt": [f"{i+1}" for i in range(len(cuts))] + (["Rest"] if rest_width > 0 else []),
        "Breite (mm)": cuts + ([rest_width] if rest_width > 0 else []),
        "Gewicht (kg)": [round(w, 2) for w in cut_weights] + ([round(rest_weight, 2)] if rest_width > 0 else []),
    })
    st.dataframe(df, hide_index=True, use_container_width=True)
except Exception as e:
    st.error(f"Fehler bei der Eingabe: {e}")

# --- 3D Visualisierung (nur Coil) ---
threejs_html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<style>
  html, body {{
    margin: 0;
    overflow: hidden;
    background: transparent;
    width: 100%;
    height: 100%;
  }}
  canvas {{
    display:block;
    width:100%;
    height:100%;
    background: transparent;
  }}
</style>
</head>
<body>
<script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>

<script>
// ===== Szene/Kamera/Renderer =====
const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(55, window.innerWidth/window.innerHeight, 1, 20000);
const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
renderer.setClearColor(0x000000, 0);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// ===== Licht =====
const key = new THREE.DirectionalLight(0xffffff, 1.15);
key.position.set(2000, 2200, 1600);
scene.add(key);

const fill = new THREE.DirectionalLight(0xfff0e0, 0.45);
fill.position.set(-1600, 800, -1000);
scene.add(fill);

scene.add(new THREE.HemisphereLight(0xffffff, 0xdde8ff, 0.4));
scene.add(new THREE.AmbientLight(0xffffff, 0.25));

// ===== Coil (vertikal stehend) =====
const RID   = {RID};
const RAD   = {RAD};
const WIDTH = {WIDTH};
const shape = new THREE.Shape();
shape.absarc(0, 0, RAD, 0, Math.PI*2, false);
const hole  = new THREE.Path();
hole.absarc(0, 0, RID, 0, Math.PI*2, true);
shape.holes.push(hole);

const geom = new THREE.ExtrudeGeometry(shape, {{ depth: WIDTH, bevelEnabled: false, curveSegments: 128 }});
geom.rotateZ(Math.PI/2);
geom.translate(0, RAD, 0);
geom.computeVertexNormals();

const mat = new THREE.MeshPhongMaterial({{
  color: 0x999999,
  shininess: 120,
  reflectivity: 0.8,
  specular: 0xffffff
}});
const coil = new THREE.Mesh(geom, mat);
scene.add(coil);

// ===== Kamera-Ausrichtung =====
(function frameCoil(){{
  const box = new THREE.Box3().setFromObject(coil);
  const size = new THREE.Vector3(); box.getSize(size);
  const center = new THREE.Vector3(); box.getCenter(center);

  const fov = camera.fov * Math.PI/180;
  const maxDim = Math.max(size.x, size.y, size.z);
  let dist = (maxDim/2) / Math.tan(fov/2);
  dist *= 2.0;

  camera.position.set(center.x + dist, center.y + dist*0.35, center.z + dist);
  camera.lookAt(center);
}})();

// ===== Rotation =====
function animate(){{
  requestAnimationFrame(animate);
  coil.rotation.y += 0.01;
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

st.subheader("3D-Ansicht des Hauptcoils")
components.html(threejs_html, height=600)
