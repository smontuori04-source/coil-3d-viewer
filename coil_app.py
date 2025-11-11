import math
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Coil – Zuschnitt & Gewicht", layout="wide")

# ==============================
# 📥 Eingaben
# ==============================
st.sidebar.title("🌀 Coil Parameter")

RID   = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD   = st.sidebar.slider("Außenradius (mm)", 600, 1600, 800, step=10)
WIDTH = st.sidebar.slider("Breite (mm)", 8, 600, 300, step=1)
THK   = st.sidebar.slider("Bandstärke (mm)", 0.1, 5.0, 1.0, step=0.1)
MATERIAL = st.sidebar.selectbox("Material", ["Stahl", "Kupfer", "Aluminium"], index=0)

# Dichten g/cm³ → g/mm³
rho_g_cm3 = {"Stahl": 7.85, "Kupfer": 8.96, "Aluminium": 2.70}
rho_g_mm3 = rho_g_cm3[MATERIAL] / 1000.0

# Gewicht & Länge
volume_mm3 = math.pi * (RAD**2 - RID**2) * WIDTH
weight_g = volume_mm3 * rho_g_mm3
weight_kg = weight_g / 1000.0
kg_per_mm = weight_kg / WIDTH
length_mm = math.pi * (RAD**2 - RID**2) / THK
length_m = length_mm / 1000.0

def fmt(x): return f"{x:,.0f}".replace(",", " ")
def fmt2(x): return f"{x:,.2f}".replace(",", " ")

# Anzeige
st.sidebar.markdown("### 📊 Berechnete Werte")
c1, c2, c3 = st.sidebar.columns(3)
c1.metric("Gesamtgewicht", f"{fmt(weight_kg)} kg")
c2.metric("Gewicht/mm", f"{fmt2(kg_per_mm)} kg/mm")
c3.metric("Länge", f"{fmt2(length_m)} m")

st.sidebar.markdown("---")
st.sidebar.subheader("✂️ Zuschnittbreiten (mm)")
cuts_input = st.sidebar.text_input("Kommagetrennt (z. B. 100, 200, 250)", "100, 200, 250")

# Zuschnitte
cuts = []
cut_weights = []
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
col_left, col_right = st.columns([0.6, 0.4])

with col_right:
    st.title("🧲 3D-Coils (liegend)")

    # ---------- Mastercoil ----------
    st.markdown("### 🧩 Mastercoil")
    master_html = f"""
    <html><body style="margin:0; background:#0E1117; display:flex; justify-content:center; align-items:center;">
    <script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
    <script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, 1, 1, 20000);
    const renderer = new THREE.WebGLRenderer({{antialias:true, alpha:true}});
    renderer.setClearColor(0x0E1117, 1);
    renderer.setSize(window.innerWidth * 0.35, 340);
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
    geom.rotateX(Math.PI/2);
    geom.translate(0, WIDTH/2, 0);

    const mat = new THREE.MeshStandardMaterial({{color: 0x999999, metalness: 0.9, roughness: 0.25}});
    const coil = new THREE.Mesh(geom, mat);
    scene.add(coil);

    const box = new THREE.Box3().setFromObject(coil);
    const size = new THREE.Vector3(); box.getSize(size);
    const center = new THREE.Vector3(); box.getCenter(center);
    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = camera.fov * Math.PI/180;
    let dist = (maxDim/2)/Math.tan(fov/2);
    dist *= 1.4;
    camera.position.set(center.x + dist, center.y + dist*0.3, center.z + dist);
    camera.lookAt(center);

    renderer.render(scene, camera);
    </script></body></html>
    """
    components.html(master_html, height=340)

    # ---------- Zuschnitt-Coils ----------
    st.markdown("### ✂️ Coil mit Zuschnitten (gestapelt)")
    cuts_js_list = ",".join([str(c) for c in cuts]) if cuts else "[]"
    weights_js_list = ",".join([str(round(w, 2)) for w in cut_weights]) if cuts else "[]"

    cuts_html = f"""
    <html><body style="margin:0; background:#0E1117; display:flex; justify-content:center; align-items:center;">
    <script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.157.0/examples/js/renderers/CSS2DRenderer.js"></script>
    <script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, 1, 1, 20000);
    const renderer = new THREE.WebGLRenderer({{antialias:true, alpha:true}});
    renderer.setClearColor(0x0E1117, 1);
    renderer.setSize(window.innerWidth * 0.35, 340);
    document.body.appendChild(renderer.domElement);

    const labelRenderer = new THREE.CSS2DRenderer();
    labelRenderer.setSize(window.innerWidth * 0.35, 340);
    labelRenderer.domElement.style.position = 'absolute';
    labelRenderer.domElement.style.top = '0px';
    document.body.appendChild(labelRenderer.domElement);

    const key = new THREE.DirectionalLight(0xffffff, 1);
    key.position.set(600, 1000, 800);
    scene.add(key);
    scene.add(new THREE.AmbientLight(0xffffff, 0.4));

    const RID = {RID}, RAD = {RAD}, TOTAL_WIDTH = {WIDTH};
    const cuts = [{cuts_js_list}];
    const weights = [{weights_js_list}];
    if (cuts.length === 0) {{
        const text = document.createElement('div');
        text.style.color = 'white';
        text.innerHTML = 'Keine Zuschnitte';
        document.body.appendChild(text);
    }}

    const sumCuts = cuts.reduce((a,b)=>a+b,0);
    const scaleFactor = TOTAL_WIDTH / sumCuts;
    const colors = [0xb87333, 0x999999, 0xd0d0d0, 0x888888, 0xaaaaaa];
    let heightOffset = 0;

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    const labels = [];

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
        const mat = new THREE.MeshStandardMaterial({{color: colors[i % colors.length], metalness:0.85, roughness:0.3}});
        const part = new THREE.Mesh(geom, mat);
        scene.add(part);

        // Linie
        if (i < cuts.length - 1) {{
            const lineGeo = new THREE.PlaneGeometry(RAD*2.2, 2);
            const lineMat = new THREE.MeshBasicMaterial({{color: 0xff0000}});
            const line = new THREE.Mesh(lineGeo, lineMat);
            line.rotateX(Math.PI/2);
            line.position.set(0, heightOffset + cutWidth + 1, 0);
            scene.add(line);
        }}

        // Hover Label
        const div = document.createElement('div');
        div.className = 'label';
        div.textContent = weights[i] + ' kg';
        div.style.padding = '2px 6px';
        div.style.borderRadius = '5px';
        div.style.backgroundColor = 'rgba(255,0,0,0.8)';
        div.style.color = 'white';
        div.style.fontSize = '12px';
        div.style.display = 'none';
        const label = new THREE.CSS2DObject(div);
        label.position.set(0, heightOffset + cutWidth/2 + 10, RAD * 1.3);
        scene.add(label);
        labels.push({{mesh: part, element: div}});

        heightOffset += cutWidth;
    }}

    const box = new THREE.Box3().setFromObject(scene);
    const size = new THREE.Vector3(); box.getSize(size);
    const center = new THREE.Vector3(); box.getCenter(center);
    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = camera.fov * Math.PI/180;
    let dist = (maxDim/2)/Math.tan(fov/2);
    dist *= 1.6;
    camera.position.set(center.x + dist, center.y + dist*0.6, center.z + dist);
    camera.lookAt(center);

    function animate() {{
      requestAnimationFrame(animate);
      renderer.render(scene, camera);
      labelRenderer.render(scene, camera);
    }}
    animate();

    // Hover Logik
    window.addEventListener('mousemove', (event) => {{
      mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
      mouse.y = - (event.clientY / 340) * 2 + 1;
      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(scene.children);
      labels.forEach(lbl => lbl.element.style.display = 'none');
      if (intersects.length > 0) {{
        const hovered = labels.find(l => l.mesh === intersects[0].object);
        if (hovered) hovered.element.style.display = 'block';
      }}
    }});
    </script></body></html>
    """
    components.html(cuts_html, height=340)
