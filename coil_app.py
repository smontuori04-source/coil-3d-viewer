import math
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Coil – Zuschnitt & Gewicht", layout="wide")

# ============== Sidebar (Eingaben) ==============
st.sidebar.title("🌀 Coil Parameter")

RID   = st.sidebar.radio("Innenradius (mm)", [150, 300, 400, 500], index=1)
RAD   = st.sidebar.slider("Außenradius (mm)", 600, 1600, 800, step=10)
WIDTH = st.sidebar.slider("Breite (mm)", 8, 600, 300, step=1)
THK   = st.sidebar.slider("Bandstärke (mm)", 0.1, 5.0, 1.0, step=0.1)
MATERIAL = st.sidebar.selectbox("Material", ["Stahl", "Kupfer", "Aluminium"], index=0)

# korrekte Dichten (g/cm³) -> g/mm³ = g/cm³ / 1000
rho_g_cm3 = {"Stahl": 7.85, "Kupfer": 8.96, "Aluminium": 2.70}
rho_g_mm3 = rho_g_cm3[MATERIAL] / 1000.0   # g/mm³

# Physik
# Volumen (mm³) des Rings
volume_mm3 = math.pi * (RAD**2 - RID**2) * WIDTH
# Gewicht
weight_g = volume_mm3 * rho_g_mm3
weight_kg = weight_g / 1000.0
# kg pro mm Breite
kg_per_mm = weight_kg / WIDTH
# Streifenlänge (entrollt): V = Länge * THK * WIDTH  -> Länge = π(R^2 - r^2)/THK  (in mm)
length_mm = math.pi * (RAD**2 - RID**2) / THK
length_m  = length_mm / 1000.0

# Kennzahlen: nur Gesamtgewicht; kg/mm; Länge  (nebeneinander)
c1, c2, c3 = st.columns(3)
c1.metric("Gesamtgewicht", f"{weight_kg:,.0f} kg")
c2.metric("Gewicht/mm", f"{kg_per_mm:,.2f} kg/mm")
c3.metric("Länge", f"{length_m:,.1f} m")

st.sidebar.markdown("---")
st.sidebar.subheader("✂️ Zuschnittbreiten (mm)")
cuts_input = st.sidebar.text_input("Kommagetrennt (z. B. 100, 200, 250)", "100, 200, 250")

# Zuschnitt-Tabelle
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
        "Gewicht (kg)": [round(w, 2) for w in cut_weights] + ([round(rest_weight, 2)] if rest_weight > 0 else []),
    })
    st.sidebar.dataframe(df, hide_index=True, use_container_width=True)
except Exception as e:
    st.sidebar.error(f"Eingabefehler: {e}")

# ============== Layout: links Berechnung, rechts 3D (oben/unten) ==============
col_left, col_right = st.columns([0.6, 0.4])

with col_left:
    st.title("🧮 Planung & Ergebnisse")
    st.write("Oben siehst du die Kernwerte. Links kannst du Material und Geometrie ändern und Zuschnitte eingeben.")

with col_right:
    st.title("🧲 3D-Ansichten")

    # ===== 3D: MASTERCOIL (liegend) =====
    st.markdown("### 🧩 Mastercoil (liegend)")
    master_html = f"""
    <html><body style="margin:0;background:#0E1117;">
    <script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.157.0/examples/js/controls/OrbitControls.js"></script>
    <script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, 1, 1, 1e6);
    const renderer = new THREE.WebGLRenderer({{antialias:true, alpha:true}});
    renderer.setClearColor(0x0E1117, 1);
    renderer.setSize(window.innerWidth, 360);
    document.body.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enablePan = false; controls.enableDamping = true; controls.dampingFactor = 0.06;

    // Lights
    const key = new THREE.DirectionalLight(0xffffff, 0.95); key.position.set(800, 1000, 900); scene.add(key);
    const fill = new THREE.DirectionalLight(0xffeedd, 0.35); fill.position.set(-600, 400, -300); scene.add(fill);
    scene.add(new THREE.AmbientLight(0xffffff, 0.25));

    // Coil (liegend)
    const RID = {RID}, RAD = {RAD}, WIDTH = {WIDTH};
    const shape = new THREE.Shape();
    shape.absarc(0,0,RAD,0,Math.PI*2,false);
    const hole = new THREE.Path(); hole.absarc(0,0,RID,0,Math.PI*2,true); shape.holes.push(hole);

    const geom = new THREE.ExtrudeGeometry(shape, {{ depth: WIDTH, bevelEnabled:false, curveSegments: 128 }});
    geom.rotateX(Math.PI/2);        // liegend
    geom.translate(0, WIDTH/2, 0);  // auf "Boden"
    const mat = new THREE.MeshStandardMaterial({{ color:0x999999, metalness:0.9, roughness:0.25 }});
    const coil = new THREE.Mesh(geom, mat);
    scene.add(coil);

    // Auto-fit camera
    function frame(obj) {{
      const box = new THREE.Box3().setFromObject(obj);
      const size = new THREE.Vector3(); box.getSize(size);
      const center = new THREE.Vector3(); box.getCenter(center);
      const maxDim = Math.max(size.x, size.y, size.z);
      const fov = camera.fov * Math.PI/180;
      let dist = (maxDim/2)/Math.tan(fov/2);
      dist *= 1.8; // etwas Luft
      camera.position.set(center.x + dist, center.y + dist*0.6, center.z + dist);
      controls.target.copy(center);
      controls.update();
    }}
    frame(coil);

    function animate(){{ requestAnimationFrame(animate); controls.update(); renderer.render(scene,camera); }}
    animate();
    </script></body></html>
    """
    components.html(master_html, height=360)

    # ===== 3D: ZUSCHNITTE (gestapelt, Hover mit Label) =====
    st.markdown("### ✂️ Gestapelte Zuschnitte (Hover zeigt Gewicht)")
    cuts_js_list = ",".join([str(c) for c in cuts]) if cuts else ""
    weights_js_list = ",".join([f"{kg_per_mm * c:.2f}" for c in cuts]) if cuts else ""

    cuts_html = f"""
    <html><body style="margin:0;background:#0E1117;">
    <script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.157.0/examples/js/controls/OrbitControls.js"></script>
    <script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, 1, 1, 1e6);
    const renderer = new THREE.WebGLRenderer({{antialias:true, alpha:true}});
    renderer.setClearColor(0x0E1117, 1);
    renderer.setSize(window.innerWidth, 360);
    document.body.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enablePan = false; controls.enableDamping = true; controls.dampingFactor = 0.06;

    // Licht
    const key = new THREE.DirectionalLight(0xffffff, 0.95); key.position.set(800, 1000, 900); scene.add(key);
    scene.add(new THREE.AmbientLight(0xffffff, 0.28));

    // Daten
    const RID = {RID}, RAD = {RAD};
    const cuts = [{cuts_js_list}];                      // mm
    const weights = [{weights_js_list}];                // kg
    const colors = [0xb87333, 0x999999, 0xd0d0d0, 0x888888, 0xaaaaaa, 0x7f8c8d, 0x95a5a6];

    // Hilfsfunktionen: Label als Sprite aus Canvas
    function makeLabelSprite(text) {{
      const cvs = document.createElement('canvas');
      const ctx = cvs.getContext('2d');
      ctx.font = '28px Arial';
      const pad = 16;
      const textW = ctx.measureText(text).width;
      cvs.width = textW + pad*2; cvs.height = 48 + pad*2;
      // Hintergrund
      ctx.fillStyle = 'rgba(0,0,0,0.6)'; ctx.fillRect(0,0,cvs.width,cvs.height);
      // Text
      ctx.fillStyle = '#ffffff'; ctx.font = '28px Arial'; ctx.fillText(text, pad, 34 + pad/2);
      const tex = new THREE.CanvasTexture(cvs);
      tex.minFilter = THREE.LinearFilter;
      const mat = new THREE.SpriteMaterial({{ map: tex, depthTest: false, depthWrite: false }});
      const spr = new THREE.Sprite(mat);
      const scale = 0.6 * {RAD};  // skaliert in Relation zur Szene
      spr.scale.set(cvs.width/cvs.height * scale, scale, 1);
      return spr;
    }}

    // Zuschnitte erzeugen (liegend, gestapelt entlang X)
    const group = new THREE.Group();
    let offset = 0;
    for(let i=0;i<cuts.length;i++) {{
      const shape = new THREE.Shape();
      shape.absarc(0,0,RAD,0,Math.PI*2,false);
      const hole = new THREE.Path(); hole.absarc(0,0,RID,0,Math.PI*2,true); shape.holes.push(hole);
      const geom = new THREE.ExtrudeGeometry(shape, {{ depth: cuts[i], bevelEnabled:false, curveSegments:128 }});
      geom.rotateX(Math.PI/2);                // liegend
      geom.translate(offset, cuts[i]/2, 0);   // Stapel entlang X, Anhebung um halbe Dicke
      const mat = new THREE.MeshStandardMaterial({{ color: colors[i % colors.length], metalness: 0.85, roughness: 0.32 }});
      const mesh = new THREE.Mesh(geom, mat);
      mesh.userData = {{ weight: (weights[i]||0), width: cuts[i], index: i+1 }};
      group.add(mesh);
      offset += cuts[i];
    }}
    scene.add(group);

    // Kamera Auto-Fit (auf gesamte Gruppe)
    function frame(obj) {{
      const box = new THREE.Box3().setFromObject(obj);
      const size = new THREE.Vector3(); box.getSize(size);
      const center = new THREE.Vector3(); box.getCenter(center);
      const maxDim = Math.max(size.x,size.y,size.z);
      const fov = camera.fov * Math.PI/180;
      let dist = (maxDim/2)/Math.tan(fov/2);
      dist *= 2.0;
      camera.position.set(center.x + dist, center.y + dist*0.6, center.z + dist);
      controls.target.copy(center);
      controls.update();
    }}
    frame(group);

    // Raycasting (Hover)
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    let current = null;
    let label = null;

    function onMove(e) {{
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(group.children, false);

      if (intersects.length > 0) {{
        const hit = intersects[0].object;
        if (current !== hit) {{
          if (current) current.material.emissive && (current.material.emissive.setHex(0x000000));
          current = hit;
          if (!hit.material.emissive) hit.material.emissive = new THREE.Color(0x000000);
          hit.material.emissive.setHex(0x222222);
          // Label
          if (label) {{ scene.remove(label); label.material.map.dispose(); }}
          const kg = hit.userData.weight?.toFixed(0) || "0";
          const mm = hit.userData.width?.toFixed(0) || "0";
          label = makeLabelSprite(`${{kg}} kg / ${{mm}} mm`);
          const box = new THREE.Box3().setFromObject(hit);
          const c = new THREE.Vector3(); box.getCenter(c);
          label.position.set(c.x, c.y + Math.max(40, hit.userData.width*0.4), c.z);
          scene.add(label);
        }}
      }} else {{
        if (current) current.material.emissive && (current.material.emissive.setHex(0x000000));
        current = null;
        if (label) {{ scene.remove(label); label.material.map.dispose(); label = null; }}
      }}
    }}
    renderer.domElement.addEventListener('mousemove', onMove);

    function animate() {{
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    }}
    animate();
    </script></body></html>
    """
    components.html(cuts_html, height=360)

# Hinweis zu Dichte-Einheiten
st.caption("Hinweis: Dichten sind korrekt in **g/cm³** angegeben (z. B. Kupfer 8.96 g/cm³). Für die Rechnung werden sie intern zu g/mm³ umgerechnet.")
