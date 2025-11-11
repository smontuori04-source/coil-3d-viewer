import math
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Coil – Zuschnitt & Gewicht", layout="wide")

# ==============================
# 📥 Eingaben
# ==============================
st.sidebar.title("🌀 Coil Parameter")

RID = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD = st.sidebar.number_input("Außenradius (mm)", 600, 1600, 800, step=10)
WIDTH = st.sidebar.number_input("Breite (mm)", 8, 600, 300, step=1)
THK = st.sidebar.number_input("Bandstärke (mm)", 0.1, 5.0, 1.0, step=0.1)
MATERIAL = st.sidebar.selectbox("Material", ["Stahl", "Kupfer", "Aluminium"], index=0)

# Dichten g/cm³ → g/mm³
rho_g_cm3 = {"Stahl": 7.85, "Kupfer": 8.96, "Aluminium": 2.70}
rho_g_mm3 = rho_g_cm3[MATERIAL] / 1000.0

# Coil-Farbe je Material (Basis)
color_map = {
    "Stahl": "0x999999",
    "Kupfer": "0xb87333",
    "Aluminium": "0xd0d0d0"
}
base_color = color_map[MATERIAL]

# Gewicht & Länge
volume_mm3 = math.pi * (RAD**2 - RID**2) * WIDTH
weight_g = volume_mm3 * rho_g_mm3
weight_kg = weight_g / 1000.0
kg_per_mm = weight_kg / WIDTH
length_mm = math.pi * (RAD**2 - RID**2) / THK
length_m = length_mm / 1000.0

def fmt(x): return f"{x:,.0f}".replace(",", " ")
def fmt2(x): return f"{x:,.2f}".replace(",", " ")

# Anzeige – kleinere Schrift
st.sidebar.markdown("### 📊 Berechnete Werte")
st.sidebar.markdown(
    f"""
    <style>
        .small-text p {{font-size:13px !important; line-height:1.2;}}
    </style>
    <div class="small-text">
        <p><b>Gesamtgewicht:</b> {fmt(weight_kg)} kg</p>
        <p><b>Gewicht/mm:</b> {fmt2(kg_per_mm)} kg/mm</p>
        <p><b>Länge:</b> {fmt2(length_m)} m</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Zuschnittbreiten
st.sidebar.markdown("---")
st.sidebar.subheader("✂️ Zuschnittbreiten (mm)")
cuts_input = st.sidebar.text_input("Kommagetrennt (z. B. 100, 200, 250)", "100, 200, 250")

cuts, cut_weights = [], []
try:
    cuts = [float(x.strip()) for x in cuts_input.split(",") if x.strip()]
    cut_weights = [kg_per_mm * c for c in cuts]
    rest_width = WIDTH - sum(cuts)
    if rest_width > 0:
        cuts.append(rest_width)
        cut_weights.append(kg_per_mm * rest_width)

    df = pd.DataFrame({
        "Zuschnitt": [f"{i+1}" for i in range(len(cuts))],
        "Breite (mm)": cuts,
        "Gewicht (kg)": [round(w, 2) for w in cut_weights]
    })
    st.sidebar.dataframe(df, hide_index=True, use_container_width=True)
except Exception as e:
    st.sidebar.error(f"Eingabefehler: {e}")

# ==============================
# 📐 Layout
# ==============================
col_left, col_right = st.columns([0.55, 0.45])

with col_right:
    st.title("🧲 3D-Coils (hell & liegend)")

    # ---------- Mastercoil ----------
    st.markdown("### 🧩 Mastercoil")
    master_html = f"""
    <html><body style="margin:0; background:white; display:flex; justify-content:center; align-items:center;">
    <script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
    <script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(50, 1.1, 1, 20000);
    const renderer = new THREE.WebGLRenderer({{antialias:true, alpha:true}});
    renderer.setClearColor(0xffffff, 1);
    renderer.setSize(window.innerWidth * 0.5, 450);
    document.body.appendChild(renderer.domElement);

    // Helles, natürliches Lichtsetup
    const sun = new THREE.DirectionalLight(0xffffff, 1.8);
    sun.position.set(2000, 2500, 2000);
    sun.castShadow = true;
    scene.add(sun);
    const fill = new THREE.DirectionalLight(0xfff6e0, 1.0);
    fill.position.set(-1500, 1200, -1000);
    scene.add(fill);
    scene.add(new THREE.AmbientLight(0xffffff, 0.9));

    // Coil
    const RID = {RID}, RAD = {RAD}, WIDTH = {WIDTH};
    const shape = new THREE.Shape();
    shape.absarc(0, 0, RAD, 0, Math.PI * 2, false);
    const hole = new THREE.Path();
    hole.absarc(0, 0, RID, 0, Math.PI * 2, true);
    shape.holes.push(hole);

    const geom = new THREE.ExtrudeGeometry(shape, {{depth: WIDTH, bevelEnabled: false, curveSegments: 128}});
    geom.rotateX(Math.PI/2);
    geom.translate(0, WIDTH/2, 0);

    const mat = new THREE.MeshStandardMaterial({{
        color: {base_color},
        metalness: 1.0,
        roughness: 0.25
    }});
    const coil = new THREE.Mesh(geom, mat);
    scene.add(coil);

    // Kamera automatisch zentrieren
    const box = new THREE.Box3().setFromObject(coil);
    const size = new THREE.Vector3(); box.getSize(size);
    const center = new THREE.Vector3(); box.getCenter(center);
    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = camera.fov * Math.PI/180;
    let dist = (maxDim/2)/Math.tan(fov/2);
    dist *= 1.3;
    camera.position.set(center.x + dist*0.8, center.y + dist*0.3, center.z + dist);
    camera.lookAt(center);

    renderer.render(scene, camera);
    </script></body></html>
    """
    components.html(master_html, height=450)

    # ---------- Zuschnitt-Coils ----------
    st.markdown("### ✂️ Coil mit Zuschnitten (gestapelt)")
    cuts_js_list = ",".join([str(c) for c in cuts]) if cuts else "[]"
    colors_js = ",".join([
        str(int(color_map[MATERIAL], 16) - (i * 0x222222)) for i in range(len(cuts))
    ]) if cuts else "[]"

    cuts_html = f"""
    <html><body style="margin:0; background:white; display:flex; justify-content:center; align-items:center;">
    <script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
    <script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(50, 1.1, 1, 20000);
    const renderer = new THREE.WebGLRenderer({{antialias:true, alpha:true}});
    renderer.setClearColor(0xffffff, 1);
    renderer.setSize(window.innerWidth * 0.5, 450);
    document.body.appendChild(renderer.domElement);

    // Helles Tageslicht
    const sun = new THREE.DirectionalLight(0xffffff, 1.8);
    sun.position.set(2000, 2500, 2000);
    scene.add(sun);
    const fill = new THREE.DirectionalLight(0xfff6e0, 1.0);
    fill.position.set(-1500, 1200, -1000);
    scene.add(fill);
    scene.add(new THREE.AmbientLight(0xffffff, 0.9));

    const RID = {RID}, RAD = {RAD}, TOTAL_WIDTH = {WIDTH};
    const cuts = [{cuts_js_list}];
    const colors = [{colors_js}];
    const sumCuts = cuts.reduce((a,b)=>a+b,0);
    const scaleFactor = TOTAL_WIDTH / sumCuts;
    let heightOffset = 0;

    for (let i = 0; i < cuts.length; i++) {{
        const cutWidth = cuts[i] * scaleFactor;
        const shape = new THREE.Shape();
        shape.absarc(0,0,RAD,0,Math.PI*2,false);
        const hole = new THREE.Path();
        hole.absarc(0,0,RID,0,Math.PI*2,true);
        shape.holes.push(hole);

        const geom = new THREE.ExtrudeGeometry(shape, {{depth: cutWidth, bevelEnabled:false, curveSegments:128}});
        geom.rotateX(Math.PI/2);
        geom.translate(0, heightOffset + cutWidth/2, 0);
        const mat = new THREE.MeshStandardMaterial({{
            color: colors[i % colors.length],
            metalness: 1.0,
            roughness: 0.25
        }});
        const part = new THREE.Mesh(geom, mat);
        scene.add(part);

        if (i < cuts.length - 1) {{
            const lineGeo = new THREE.PlaneGeometry(RAD*2.2, 2);
            const lineMat = new THREE.MeshBasicMaterial({{color: 0xff0000}});
            const line = new THREE.Mesh(lineGeo, lineMat);
            line.rotateX(Math.PI/2);
            line.position.set(0, heightOffset + cutWidth + 1, 0);
            scene.add(line);
        }}
        heightOffset += cutWidth;
    }}

    const box = new THREE.Box3().setFromObject(scene);
    const size = new THREE.Vector3(); box.getSize(size);
    const center = new THREE.Vector3(); box.getCenter(center);
    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = camera.fov * Math.PI/180;
    let dist = (maxDim/2)/Math.tan(fov/2);
    dist *= 1.3;
    camera.position.set(center.x + dist*0.8, center.y + dist*0.3, center.z + dist);
    camera.lookAt(center);

    renderer.render(scene, camera);
    </script></body></html>
    """
    components.html(cuts_html, height=450)
