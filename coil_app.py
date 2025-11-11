import math
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Coil – Zuschnittplanung", layout="wide")

# ==============================
# 🎨 Layout & Farben
# ==============================
st.markdown("""
<style>
    body, [data-testid="stAppViewContainer"] {
        background-color: #2C2F35;
        color: #EDEDED;
    }
    [data-testid="stSidebar"] {
        background-color: #2C2F35 !important;
        color: #EDEDED;
    }
    h1, h2, h3 { color: #EDEDED; font-weight: 600; }
    .threejs-box {
        background-color: #0E1117;
        border-radius: 12px;
        box-shadow: 0 0 18px rgba(0,0,0,0.4);
        padding: 10px;
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================
# 🧮 Spaltenlayout
# ==============================
col_left, col_right = st.columns([0.6, 0.4])

# --- Eingaben & Berechnung (linke Spalte) ---
with col_left:
    st.title("🌀 Coil Berechnung & Zuschnittplanung")

    RID = st.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
    RAD = st.slider("Außenradius (mm)", 600, 1600, 800, step=10)
    WIDTH = st.slider("Breite (mm)", 8, 600, 300, step=1)
    MATERIAL = st.selectbox("Material", ["Stahl", "Kupfer", "Aluminium"], index=1)

    density_map = {"Stahl": 0.00785, "Kupfer": 0.00896, "Aluminium": 0.00270}
    rho = density_map[MATERIAL]

    # Physik
    volume_mm3 = math.pi * (RAD**2 - RID**2) * WIDTH
    weight_g = volume_mm3 * rho
    weight_kg = weight_g / 1000
    kg_per_mm = weight_kg / WIDTH

    st.markdown("### 📏 Berechnete Werte")
    c1, c2 = st.columns(2)
    c1.metric("Gesamtgewicht", f"{weight_kg:,.0f} kg")
    c2.metric("Gewicht/mm", f"{kg_per_mm:,.2f} kg/mm")
    st.metric("Volumen", f"{volume_mm3/1e9:,.2f} dm³")

    st.markdown("---")
    st.subheader("✂️ Zuschnittbreiten")
    cuts_input = st.text_input("Gib Zuschnittbreiten (Komma getrennt) ein:", "100, 200, 250")

    try:
        cuts = [float(x.strip()) for x in cuts_input.split(",") if x.strip()]
        sum_cuts = sum(cuts)
        cut_weights = [kg_per_mm * c for c in cuts]
        rest_width = WIDTH - sum_cuts
        rest_weight = kg_per_mm * rest_width if rest_width > 0 else 0

        df = pd.DataFrame({
            "Zuschnitt": [f"{i+1}" for i in range(len(cuts))] + (["Rest"] if rest_width > 0 else []),
            "Breite (mm)": cuts + ([rest_width] if rest_width > 0 else []),
            "Gewicht (kg)": [round(w, 2) for w in cut_weights] + ([round(rest_weight, 2)] if rest_width > 0 else []),
        })
        st.dataframe(df, hide_index=True, use_container_width=True)
    except Exception as e:
        st.error(f"Fehler in der Eingabe: {e}")

# --- 3D-Visualisierung (rechte Spalte) ---
with col_right:
    st.title("🧲 3D-Coil Visualisierung")

    coil_height = 340

    # ========== Mastercoil ==========
    st.markdown('<div class="threejs-box">', unsafe_allow_html=True)
    st.markdown("### 🧩 Mastercoil (liegend)")

    threejs_master = f"""
    <html><body style="margin:0; background:#0E1117;">
    <script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
    <script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, 1, 1, 20000);
    const renderer = new THREE.WebGLRenderer({{antialias:true, alpha:true}});
    renderer.setClearColor(0x0E1117, 1);
    renderer.setSize(window.innerWidth, {coil_height});
    document.body.appendChild(renderer.domElement);

    // Lichtsetup
    const key = new THREE.DirectionalLight(0xffffff, 0.9);
    key.position.set(500, 800, 700);
    scene.add(key);
    const fill = new THREE.DirectionalLight(0xffeedd, 0.3);
    fill.position.set(-400, 300, -200);
    scene.add(fill);
    scene.add(new THREE.AmbientLight(0xffffff, 0.25));

    // Coil
    const RID = {RID}, RAD = {RAD}, WIDTH = {WIDTH};
    const shape = new THREE.Shape();
    shape.absarc(0, 0, RAD, 0, Math.PI*2, false);
    const hole = new THREE.Path();
    hole.absarc(0, 0, RID, 0, Math.PI*2, true);
    shape.holes.push(hole);

    const geom = new THREE.ExtrudeGeometry(shape, {{depth: WIDTH, bevelEnabled: false}});
    geom.rotateX(Math.PI/2);  // 🔹 liegt flach auf X-Z-Ebene
    geom.translate(0, WIDTH/2, 0);

    const mat = new THREE.MeshStandardMaterial({{
        color: 0x999999,
        metalness: 0.9,
        roughness: 0.25
    }});
    const coil = new THREE.Mesh(geom, mat);
    scene.add(coil);

    // Kamera
    camera.position.set(RAD*2.3, RAD*1.2, RAD*2.3);
    camera.lookAt(0, 0, 0);
    renderer.render(scene, camera);
    </script></body></html>
    """
    components.html(threejs_master, height=coil_height)
    st.markdown('</div>', unsafe_allow_html=True)

    # ========== Coil mit Zuschnitten ==========
    st.markdown('<div class="threejs-box">', unsafe_allow_html=True)
    st.markdown("### ✂️ Coil mit Zuschnitten (liegend)")

    threejs_cuts = f"""
    <html><body style="margin:0; background:#0E1117;">
    <script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
    <script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, 1, 1, 20000);
    const renderer = new THREE.WebGLRenderer({{antialias:true, alpha:true}});
    renderer.setClearColor(0x0E1117, 1);
    renderer.setSize(window.innerWidth, {coil_height});
    document.body.appendChild(renderer.domElement);

    const key = new THREE.DirectionalLight(0xffffff, 0.9);
    key.position.set(500, 800, 700);
    scene.add(key);
    scene.add(new THREE.AmbientLight(0xffffff, 0.3));

    const RID = {RID}, RAD = {RAD};
    const cuts = [{','.join(map(str, cuts)) if 'cuts' in locals() else ''}];
    let offset = 0;
    const colors = [0xb87333, 0x999999, 0xd0d0d0, 0x888888, 0xaaaaaa];

    for (let i=0; i<cuts.length; i++) {{
        const shape = new THREE.Shape();
        shape.absarc(0, 0, RAD, 0, Math.PI*2, false);
        const hole = new THREE.Path();
        hole.absarc(0, 0, RID, 0, Math.PI*2, true);
        shape.holes.push(hole);

        const geom = new THREE.ExtrudeGeometry(shape, {{depth: cuts[i], bevelEnabled: false}});
        geom.rotateX(Math.PI/2);
        geom.translate(offset, cuts[i]/2, 0);

        const mat = new THREE.MeshStandardMaterial({{
            color: colors[i % colors.length],
            metalness: 0.85,
            roughness: 0.3
        }});
        const part = new THREE.Mesh(geom, mat);
        scene.add(part);
        offset += cuts[i];
    }}

    camera.position.set(RAD*2.3, RAD*1.2, RAD*2.3);
    camera.lookAt(0, 0, 0);
    renderer.render(scene, camera);
    </script></body></html>
    """
    components.html(threejs_cuts, height=coil_height)
    st.markdown('</div>', unsafe_allow_html=True)
