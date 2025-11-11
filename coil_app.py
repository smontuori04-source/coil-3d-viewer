import math
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Coil – Zuschnitt & Gewicht", layout="wide")

# ==============================
# 📥 Eingaben (linke Sidebar)
# ==============================
st.sidebar.title("🌀 Coil Parameter")

RID   = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD   = st.sidebar.slider("Außenradius (mm)", 600, 1600, 800, step=10)
WIDTH = st.sidebar.slider("Breite (mm)", 8, 600, 300, step=1)
THK   = st.sidebar.slider("Bandstärke (mm)", 0.1, 5.0, 1.0, step=0.1)
MATERIAL = st.sidebar.selectbox("Material", ["Stahl", "Kupfer", "Aluminium"], index=0)

# Dichten in g/cm³ → g/mm³
rho_g_cm3 = {"Stahl": 7.85, "Kupfer": 8.96, "Aluminium": 2.70}
rho_g_mm3 = rho_g_cm3[MATERIAL] / 1000.0

# Gewicht & Länge berechnen
volume_mm3 = math.pi * (RAD**2 - RID**2) * WIDTH
weight_g = volume_mm3 * rho_g_mm3
weight_kg = weight_g / 1000.0
kg_per_mm = weight_kg / WIDTH
length_mm = math.pi * (RAD**2 - RID**2) / THK
length_m = length_mm / 1000.0

# Formatierung mit Leerzeichen statt Komma
def fmt(x):
    return f"{x:,.0f}".replace(",", " ")

def fmt2(x):
    return f"{x:,.2f}".replace(",", " ")

# Anzeige der Kennwerte
st.sidebar.markdown("### 📊 Berechnete Werte")
c1, c2, c3 = st.sidebar.columns(3)
c1.metric("Gesamtgewicht", f"{fmt(weight_kg)} kg")
c2.metric("Gewicht/mm", f"{fmt2(kg_per_mm)} kg/mm")
c3.metric("Länge", f"{fmt2(length_m)} m")

st.sidebar.markdown("---")
st.sidebar.subheader("✂️ Zuschnittbreiten (mm)")
cuts_input = st.sidebar.text_input("Kommagetrennt (z. B. 100, 200, 250)", "100, 200, 250")

# Zuschnittberechnung
cuts = []
try:
    cuts = [float(x.strip()) for x in cuts_input.split(",") if x.strip()]
    sum_cuts = sum(cuts)
    cut_weights = [kg_per_mm * c for c in cuts]
    rest_width = WIDTH - sum_cuts
    rest_weight = kg_per_mm * rest_width if rest_width > 0 else 0.0

    df = pd.DataFrame({
        "Zuschnitt": [f"{i+1}" for i in range(len(cuts))] + (["Rest"] if rest_width > 0 else []),
        "Breite (mm)": cuts + ([rest_width] if rest_width > 0 else []),
        "Gewicht (kg)": [round(w, 2) for w in cut_weights] + ([round(rest_weight, 2)] if rest_width > 0 else []),
    })
    st.sidebar.dataframe(df, hide_index=True, use_container_width=True)
except Exception as e:
    st.sidebar.error(f"Eingabefehler: {e}")

# ==============================
# 📐 Layout (Spalten)
# ==============================
col_left, col_right = st.columns([0.6, 0.4])

with col_left:
    st.title("🧮 Coil-Berechnung & Ergebnisse")
    st.write("Links oben findest du alle Parameter und Berechnungen.")

with col_right:
    st.title("🧲 3D-Coils (liegend)")

    # ---------- MASTERCOIL ----------
    st.markdown("### 🧩 Mastercoil")
    master_html = f"""
    <html><body style="margin:0;background:#0E1117;">
    <script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
    <script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, 1, 1, 20000);
    const renderer = new THREE.WebGLRenderer({{antialias:true, alpha:true}});
    renderer.setClearColor(0x0E1117, 1);
    renderer.setSize(window.innerWidth, 350);
    document.body.appendChild(renderer.domElement);

    const key = new THREE.DirectionalLight(0xffffff, 1);
    key.position.set(600, 1000, 800);
    scene.add(key);
    const fill = new THREE.DirectionalLight(0xffeedd, 0.35);
    fill.position.set(-400, 300, -200);
    scene.add(fill);
    scene.add(new THREE.AmbientLight(0xffffff, 0.3));

    const RID = {RID}, RAD = {RAD}, WIDTH = {WIDTH};
    const shape = new THREE.Shape();
    shape.absarc(0, 0, RAD, 0, Math.PI * 2, false);
    const hole = new THREE.Path();
    hole.absarc(0, 0, RID, 0, Math.PI * 2, true);
    shape.holes.push(hole);

    const geom = new THREE.ExtrudeGeometry(shape, {{depth: WIDTH, bevelEnabled: false, curveSegments: 128}});
    geom.rotateX(Math.PI/2);   // liegend
    geom.translate(0, WIDTH/2, 0);

    const mat = new THREE.MeshStandardMaterial({{color: 0x999999, metalness: 0.9, roughness: 0.25}});
    const coil = new THREE.Mesh(geom, mat);
    scene.add(coil);

    // Kamera automatisch passend setzen
    const box = new THREE.Box3().setFromObject(coil);
    const size = new THREE.Vector3(); box.getSize(size);
    const center = new THREE.Vector3(); box.getCenter(center);
    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = camera.fov * Math.PI/180;
    let dist = (maxDim/2)/Math.tan(fov/2);
    dist *= 2.0;
    camera.position.set(center.x + dist, center.y + dist*0.5, center.z + dist);
    camera.lookAt(center);

    renderer.render(scene, camera);
    </script></body></html>
    """
    components.html(master_html, height=350)

    # ---------- ZUSCHNITTE ----------
    st.markdown("### ✂️ Coil mit Zuschnitten")
    cuts_js_list = ",".join([str(c) for c in cuts]) if cuts else ""
    cuts_html = f"""
    <html><body style="margin:0;background:#0E1117;">
    <script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
    <script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, 1, 1, 20000);
    const renderer = new THREE.WebGLRenderer({{antialias:true, alpha:true}});
    renderer.setClearColor(0x0E1117, 1);
    renderer.setSize(window.innerWidth, 350);
    document.body.appendChild(renderer.domElement);

    const key = new THREE.DirectionalLight(0xffffff, 1);
    key.position.set(600, 1000, 800);
    scene.add(key);
    const fill = new THREE.DirectionalLight(0xffeedd, 0.35);
    fill.position.set(-400, 300, -200);
    scene.add(fill);
    scene.add(new THREE.AmbientLight(0xffffff, 0.3));

    const RID = {RID}, RAD = {RAD};
    const cuts = [{cuts_js_list}];
    const colors = [0xb87333, 0x999999, 0xd0d0d0, 0x888888, 0xaaaaaa];
    let offset = 0;
    for (let i=0; i<cuts.length; i++) {{
        const shape = new THREE.Shape();
        shape.absarc(0,0,RAD,0,Math.PI*2,false);
        const hole = new THREE.Path();
        hole.absarc(0,0,RID,0,Math.PI*2,true);
        shape.holes.push(hole);

        const geom = new THREE.ExtrudeGeometry(shape, {{depth: cuts[i], bevelEnabled:false, curveSegments:128}});
        geom.rotateX(Math.PI/2);
        geom.translate(offset, cuts[i]/2, 0);
        const mat = new THREE.MeshStandardMaterial({{color: colors[i % colors.length], metalness:0.85, roughness:0.3}});
        const part = new THREE.Mesh(geom, mat);
        scene.add(part);
        offset += cuts[i];
    }}

    // Kamera automatisch positionieren
    const box = new THREE.Box3().setFromObject(scene);
    const size = new THREE.Vector3(); box.getSize(size);
    const center = new THREE.Vector3(); box.getCenter(center);
    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = camera.fov * Math.PI/180;
    let dist = (maxDim/2)/Math.tan(fov/2);
    dist *= 2.0;
    camera.position.set(center.x + dist, center.y + dist*0.5, center.z + dist);
    camera.lookAt(center);

    renderer.render(scene, camera);
    </script></body></html>
    """
    components.html(cuts_html, height=350)
