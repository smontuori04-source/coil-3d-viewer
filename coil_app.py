import math
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Coil – Zuschnittplanung", layout="wide")

# ==============================
# 🔹 Sidebar: Coil Parameter
# ==============================
st.sidebar.title("Coil Parameter")
RID = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD = st.sidebar.slider("Außenradius (mm)", 600, 1600, 800, step=10)
WIDTH = st.sidebar.slider("Breite (mm)", 8, 600, 300, step=1)
MATERIAL = st.sidebar.selectbox("Material", ["Stahl", "Kupfer", "Aluminium"], index=0)

# Materialdichte (g/mm³)
density_map = {"Stahl": 0.00785, "Kupfer": 0.00896, "Aluminium": 0.00270}
rho = density_map[MATERIAL]

# ==============================
# 🔹 Layout mit 2 Hauptspalten
# ==============================
col_left, col_right = st.columns([1.8, 2])

# --- Spalte 1: Eingaben & Berechnungen ---
with col_left:
    st.title("🌀 Coil Berechnung & Zuschnittplanung")
    st.caption("Gib Coil-Parameter ein, um Gewichte und Zuschnitte zu berechnen.")

    volume_mm3 = math.pi * (RAD**2 - RID**2) * WIDTH
    weight_g = volume_mm3 * rho
    weight_kg = weight_g / 1000
    kg_per_mm = weight_kg / WIDTH

    col1, col2, col3 = st.columns(3)
    col1.metric("Gesamtgewicht", f"{weight_kg:,.0f} kg")
    col2.metric("Gewicht pro mm", f"{kg_per_mm:,.2f} kg/mm")
    col3.metric("Volumen", f"{volume_mm3/1e9:,.2f} dm³")

    # --- Zuschnitt Eingabe ---
    st.subheader("✂️ Zuschnittbreiten")
    cuts_input = st.text_input("Gib Zuschnittbreiten ein (Komma getrennt)", "100, 200, 250")

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
            "Gewicht (kg)": [round(w, 2) for w in cut_weights] + ([round(rest_weight, 2)] if rest_weight > 0 else []),
        })
        st.dataframe(df, hide_index=True, use_container_width=True)
    except Exception as e:
        st.error(f"Fehler in der Eingabe: {e}")

# ==============================
# 🔹 Spalte 2: 3D-Ansichten
# ==============================
with col_right:
    st.markdown("### Mastercoil (3D Ansicht)")
    threejs_master = f"""
    <html><body style="margin:0; background-color:#0E1117;">
    <script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
    <script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(55, 1, 1, 20000);
    const renderer = new THREE.WebGLRenderer({{antialias:true, alpha:true}});
    renderer.setClearColor(0x0E1117, 1);
    renderer.setSize(400,400);
    document.body.appendChild(renderer.domElement);
    const light = new THREE.DirectionalLight(0xffffff, 1); light.position.set(1,1,1); scene.add(light);

    const shape = new THREE.Shape();
    shape.absarc(0,0,{RAD},0,Math.PI*2,false);
    const hole = new THREE.Path();
    hole.absarc(0,0,{RID},0,Math.PI*2,true);
    shape.holes.push(hole);
    const geom = new THREE.ExtrudeGeometry(shape,{{depth:{WIDTH},bevelEnabled:false}});
    geom.rotateZ(Math.PI/2);
    geom.translate(0,{RAD},0);
    const mat = new THREE.MeshPhongMaterial({{color:0x999999, shininess:100}});
    const coil = new THREE.Mesh(geom,mat);
    scene.add(coil);
    camera.position.set({RAD*2},{RAD*1.2},{RAD*2});
    camera.lookAt(0,{RAD/2},0);
    renderer.render(scene,camera);
    </script></body></html>
    """
    components.html(threejs_master, height=400)

    st.markdown("### Coil mit Zuschnitten (3D Ansicht)")
    threejs_cuts = f"""
    <html><body style="margin:0; background-color:#0E1117;">
    <script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
    <script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(55, 1, 1, 20000);
    const renderer = new THREE.WebGLRenderer({{antialias:true, alpha:true}});
    renderer.setClearColor(0x0E1117, 1);
    renderer.setSize(400,400);
    document.body.appendChild(renderer.domElement);
    const light = new THREE.DirectionalLight(0xffffff, 1); light.position.set(1,1,1); scene.add(light);

    const RID = {RID}, RAD = {RAD};
    const cuts = [{','.join(map(str, cuts)) if 'cuts' in locals() else ''}];
    let offset = 0;
    const colors = [0xb87333, 0x999999, 0xd0d0d0, 0x888888, 0xaaaaaa];
    
    for (let i=0; i<cuts.length; i++) {{
        const shape = new THREE.Shape();
        shape.absarc(0,0,RAD,0,Math.PI*2,false);
        const hole = new THREE.Path();
        hole.absarc(0,0,RID,0,Math.PI*2,true);
        shape.holes.push(hole);
        const geom = new THREE.ExtrudeGeometry(shape,{{depth:cuts[i],bevelEnabled:false}});
        geom.rotateZ(Math.PI/2);
        geom.translate(offset, RAD, 0);
        const mat = new THREE.MeshPhongMaterial({{color:colors[i % colors.length], shininess:100}});
        const part = new THREE.Mesh(geom, mat);
        scene.add(part);
        offset += cuts[i];
    }}

    camera.position.set({RAD*2},{RAD*1.2},{RAD*2});
    camera.lookAt(0,{RAD/2},0);
    renderer.render(scene,camera);
    </script></body></html>
    """
    components.html(threejs_cuts, height=400)
