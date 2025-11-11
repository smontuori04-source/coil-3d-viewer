import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="3D Coil Visualisierung", layout="wide")

# --- Sidebar Eingaben ---
st.sidebar.title("🌀 Coil Parameter")
RID = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD = st.sidebar.number_input("Außenradius (mm)", min_value=600, max_value=1600, value=800, step=10)
WIDTH = st.sidebar.number_input("Breite (mm)", min_value=8, max_value=600, value=300, step=1)
THICK = st.sidebar.number_input("Bandstärke (mm)", min_value=0.5, max_value=20.0, value=3.0, step=0.1)
MATERIAL = st.sidebar.selectbox("Material", ["Stahl", "Kupfer", "Aluminium"], index=0)

# --- Materialdichten ---
density = {"Stahl": 7.85, "Kupfer": 8.96, "Aluminium": 2.70}
rho = density[MATERIAL]

# --- Berechnungen ---
volume_mm3 = math.pi * (RAD**2 - RID**2) * WIDTH
volume_m3 = volume_mm3 * 1e-9
gewicht = rho * volume_m3 * 1000  # kg
gewicht_pro_mm = gewicht / WIDTH
laenge = (math.pi * (RAD + RID)) * (WIDTH / THICK) / 1000

# --- Anzeige: Berechnete Werte ---
st.sidebar.markdown("### 📊 Berechnete Werte")
c1, c2, c3 = st.sidebar.columns(3)
c1.metric("Gesamtgewicht", f"{gewicht:,.0f} kg".replace(",", " "))
c2.metric("Gewicht/mm", f"{gewicht_pro_mm:,.2f} kg/mm")
c3.metric("Länge", f"{laenge:,.2f} m")

# --- Zuschnittparameter ---
st.sidebar.markdown("---")
st.sidebar.subheader("✂️ Zuschnittbreiten (mm)")
cuts_input = st.sidebar.text_input("Kommagetrennt (z. B. 100,200,250)", "100,200,250")
cuts = [float(c.strip()) for c in cuts_input.split(",") if c.strip()]
rest = WIDTH - sum(cuts)
if rest > 0:
    cuts.append(rest)

# --- Farbzuordnung ---
color_map = {"Stahl": "0x777777", "Kupfer": "0xb87333", "Aluminium": "0xd0d0d0"}
color = color_map[MATERIAL]

# --- HTML Template für Coil-Darstellung ---
def coil_html(title, stacked=False):
    stack_script = ""
    if stacked:
        y_offset = 0
        stack_script += "const group = new THREE.Group();\n"
        for i, c in enumerate(cuts):
            stack_script += f"""
            const shape{i} = new THREE.Shape();
            shape{i}.absarc(0, 0, {RAD}, 0, Math.PI*2);
            const hole{i} = new THREE.Path();
            hole{i}.absarc(0, 0, {RID}, 0, Math.PI*2, true);
            shape{i}.holes.push(hole{i});
            const geo{i} = new THREE.ExtrudeGeometry(shape{i}, {{depth:{c}, bevelEnabled:false}});
            geo{i}.rotateX(Math.PI/2);
            geo{i}.translate(0, {y_offset:.1f}, 0);
            const mat{i} = new THREE.MeshPhongMaterial({{color:{color}, shininess:100}});
            const coil{i} = new THREE.Mesh(geo{i}, mat{i});
            group.add(coil{i});
            """
            y_offset += c + 10
        stack_script += "scene.add(group);\n"

    else:
        stack_script = f"""
        const shape = new THREE.Shape();
        shape.absarc(0, 0, {RAD}, 0, Math.PI*2);
        const hole = new THREE.Path();
        hole.absarc(0, 0, {RID}, 0, Math.PI*2, true);
        shape.holes.push(hole);
        const geom = new THREE.ExtrudeGeometry(shape, {{depth:{WIDTH}, bevelEnabled:false}});
        geom.rotateX(Math.PI/2);
        const mat = new THREE.MeshPhongMaterial({{color:{color}, shininess:100}});
        const coil = new THREE.Mesh(geom, mat);
        scene.add(coil);
        """

    return f"""
    <div style="
        background-color:#1e1e1e;
        border-radius:15px;
        width:95%;
        height:400px;
        margin:auto;
        display:flex;
        flex-direction:column;
        align-items:center;
        justify-content:center;
    ">
    <h3 style="color:white;font-family:sans-serif;">{title}</h3>
    <script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
    <script>
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1e1e1e);
    const camera = new THREE.PerspectiveCamera(55, 1.6, 0.1, 20000);
    const renderer = new THREE.WebGLRenderer({{antialias:true}});
    renderer.setSize(window.innerWidth * 0.38, 350);
    document.currentScript.parentElement.appendChild(renderer.domElement);

    const light1 = new THREE.DirectionalLight(0xffffff, 1.1);
    light1.position.set(800, 1000, 800);
    scene.add(light1);
    scene.add(new THREE.AmbientLight(0xffffff, 0.6));

    {stack_script}

    camera.position.set(0, {RAD*1.2}, {RAD*2});
    camera.lookAt(0, 0, 0);
    renderer.render(scene, camera);
    </script>
    </div>
    """

# --- Layout ---
left, right = st.columns([0.55, 0.45])

with right:
    st.markdown("### 🧲 Mastercoil (liegend)")
    components.html(coil_html("Mastercoil", stacked=False), height=420)
    st.markdown("### ✂️ Coil mit Zuschnitten (gestapelt)")
    components.html(coil_html("Coil mit Zuschnitten", stacked=True), height=420)
