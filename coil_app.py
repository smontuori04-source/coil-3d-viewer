import math
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Coil – Zuschnitt & Gewicht", layout="wide")

# ==============================
# 🤏 Eingaben
# ==============================
st.sidebar.title("🌀 Coil Parameter")

RID = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD = st.sidebar.number_input("Außenradius (mm)", 600, 1600, 800, step=10)
WIDTH = st.sidebar.number_input("Breite (mm)", 8, 600, 300, step=1)
THK = st.sidebar.number_input("Bandstärke (mm)", 0.1, 5.0, 1.0, step=0.1)
MATERIAL = st.sidebar.selectbox("Material", ["Stahl", "Kupfer", "Aluminium", "Messing"], index=1)

# =================================
# 📌 Material-Dichten (g/cm3 → g/mm3)
# =================================
rho_g_cm3 = {
    "Stahl": 7.85,
    "Kupfer": 8.96,
    "Aluminium": 2.70,
    "Messing": 8.50
}
rho_g_mm3 = rho_g_cm3[MATERIAL] / 1000.0

# ==============================
# 🎨 Farbwerte (HEX)
# ==============================
color_map = {
    "Stahl": 0x777777,
    "Kupfer": 0xb87333,
    "Aluminium": 0xe6e6e6,
    "Messing": 0xd4af37
}
base_hex = color_map[MATERIAL]

# ==============================
# 🌈 Funktion zur Farbabstufung
# ==============================
def shade_color(hex_color, factor):
    r = (hex_color >> 16) & 255
    g = (hex_color >> 8) & 255
    b = hex_color & 255

    r = max(0, min(255, int(r * factor)))
    g = max(0, min(255, int(g * factor)))
    b = max(0, min(255, int(b * factor)))

    return (r << 16) + (g << 8) + b

# ==============================
# ⚖️ Gewichte
# ==============================
volume_mm3 = math.pi * (RAD**2 - RID**2) * WIDTH
weight_kg = (volume_mm3 * rho_g_mm3) / 1000.0
kg_per_mm = weight_kg / WIDTH
length_m = math.pi * (RAD**2 - RID**2) / THK / 1000.0

def fmt(x): return f"{x:,.0f}".replace(",", " ")
def fmt2(x): return f"{x:,.2f}".replace(",", " ")

# Sidebar-Ergebnisse
st.sidebar.markdown("### 📊 Berechnete Werte")
st.sidebar.markdown(
    f"""
    <div style="font-size:13px; line-height:1.3;">
    <b>Gesamtgewicht:</b> {fmt(weight_kg)} kg<br>
    <b>Gewicht/mm:</b> {fmt2(kg_per_mm)} kg/mm<br>
    <b>Länge:</b> {fmt2(length_m)} m
    </div>
    """,
    unsafe_allow_html=True
)

# ==============================
# ✂️ Zuschnitte
# ==============================
st.sidebar.markdown("---")
st.sidebar.subheader("✂️ Zuschnittbreiten (mm)")
cuts_input = st.sidebar.text_input("Kommagetrennt (z. B. 100, 200, 250)", "100, 60, 60, 20")

cuts, cut_weights = [], []

try:
    cuts = [float(x.strip()) for x in cuts_input.split(",") if x.strip()]
    cut_weights = [kg_per_mm * c for c in cuts]

    rest = WIDTH - sum(cuts)
    if rest > 0:
        cuts.append(rest)
        cut_weights.append(kg_per_mm * rest)

    df = pd.DataFrame({
        "Zuschnitt": [f"{i+1}" for i in range(len(cuts))],
        "Breite (mm)": cuts,
        "Gewicht (kg)": [round(w, 2) for w in cut_weights]
    })
    st.sidebar.dataframe(df, hide_index=True, use_container_width=True)
except:
    st.sidebar.error("Fehlerhafte Eingabe bei Zuschnitten.")

# ==============================
# 🎨 HTML-Bausteine für Licht + Szene
# ==============================
LIGHT_JS = """
// --- Perfekte Beleuchtung ---
const key = new THREE.DirectionalLight(0xffffff, 1.35);
key.position.set(1500, 1200, 800);
scene.add(key);

const fill = new THREE.DirectionalLight(0xfff8e5, 0.75);
fill.position.set(-1000, 600, -500);
scene.add(fill);

const rim = new THREE.DirectionalLight(0xffffff, 0.55);
rim.position.set(0, -400, 900);
scene.add(rim);

scene.add(new THREE.AmbientLight(0xffffff, 0.45));
"""

# ==============================
# 📐 Layout
# ==============================
col_left, col_right = st.columns([0.45, 0.55])


# ============================================
# 🧲 3D MASTERCOIL
# ============================================
with col_right:
    st.markdown("## 🧲 3D-Coils (hell & liegend)")
    st.markdown("### 🧩 Mastercoil")

    master_html = f"""
    <html><body style='margin:0; background:white;'>
    <script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>

    <div id="c" style="width:100%; height:420px;"></div>

    <script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(55, 1.9, 1, 20000);
    const renderer = new THREE.WebGLRenderer({antialias:true, alpha:true});
    renderer.setClearColor(0xffffff, 1);
    renderer.setSize(window.innerWidth*0.52, 420);
    document.getElementById("c").appendChild(renderer.domElement);

    {LIGHT_JS}

    // COIL GEOMETRIE
    const shape = new THREE.Shape();
    shape.absarc(0,0,{RAD},0,Math.PI*2,false);
    const hole = new THREE.Path();
    hole.absarc(0,0,{RID},0,Math.PI*2,true);
    shape.holes.push(hole);

    const geom = new THREE.ExtrudeGeometry(shape, {{depth:{WIDTH}, bevelEnabled:false}});
    geom.rotateX(Math.PI/2);
    geom.translate(0,{WIDTH}/2,0);

    const mat = new THREE.MeshStandardMaterial({{
        color:{base_hex},
        metalness:1.0,
        roughness:0.22
    }});
    const coil = new THREE.Mesh(geom, mat);
    scene.add(coil);

    // Kamera zentrieren
    const box = new THREE.Box3().setFromObject(coil);
    const size = new THREE.Vector3(); box.getSize(size);
    const center = new THREE.Vector3(); box.getCenter(center);
    const dist = size.length()*0.9;
    camera.position.set(center.x + dist, center.y + dist*0.25, center.z + dist);
    camera.lookAt(center);

    renderer.render(scene, camera);
    </script></body></html>
    """
    components.html(master_html, height=420)


# ============================================
# ✂️ 3D ZUSCHNITTE – GESTAPELT
# ============================================
    st.markdown("### ✂️ Coil mit Zuschnitten (gestapelt)")

    colors_js = ",".join([str(shade_color(base_hex, 1 - i*0.12)) for i in range(len(cuts))])
    cuts_js = ",".join([str(c) for c in cuts])

    cuts_html = f"""
    <html><body style='margin:0; background:white;'>
    <script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>

    <div id="cut" style="width:100%; height:420px;"></div>

    <script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(55, 1.9, 1, 20000);
    const renderer = new THREE.WebGLRenderer({antialias:true, alpha:true});
    renderer.setClearColor(0xffffff, 1);
    renderer.setSize(window.innerWidth*0.52, 420);
    document.getElementById("cut").appendChild(renderer.domElement);

    {LIGHT_JS}

    const RID = {RID}, RAD = {RAD}, TOTAL = {WIDTH};
    const cuts = [{cuts_js}];
    const cols = [{colors_js}];

    let offset = 0;
    for (let i=0; i<cuts.length; i++) {{
        const w = cuts[i];

        const shape = new THREE.Shape();
        shape.absarc(0,0,RAD,0,Math.PI*2,false);
        const hole = new THREE.Path();
        hole.absarc(0,0,RID,0,Math.PI*2,true);
        shape.holes.push(hole);

        const g = new THREE.ExtrudeGeometry(shape, {{depth:w, bevelEnabled:false}});
        g.rotateX(Math.PI/2);
        g.translate(0, offset + w/2, 0);

        const m = new THREE.MeshStandardMaterial({{
            color: cols[i],
            metalness: 1.0,
            roughness: 0.22
        }});
        const part = new THREE.Mesh(g, m);
        scene.add(part);

        offset += w + 3; // Abstand zwischen Zuschnitten
    }}

    const box = new THREE.Box3().setFromObject(scene);
    const size = new THREE.Vector3(); box.getSize(size);
    const center = new THREE.Vector3(); box.getCenter(center);
    const dist = size.length()*0.85;
    camera.position.set(center.x + dist, center.y + dist*0.22, center.z + dist);
    camera.lookAt(center);

    renderer.render(scene, camera);
    </script></body></html>
    """

    components.html(cuts_html, height=420)
