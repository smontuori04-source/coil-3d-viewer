with col_right:
    st.title("🧲 3D-Coils (liegend)")

    # ---------- Mastercoil ----------
    st.markdown("### 🧩 Mastercoil")
    master_html = f"""
    <html><body style="margin:0; background:#17191C; display:flex; justify-content:center; align-items:center;">
    <script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
    <script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(50, 1.1, 1, 20000);
    const renderer = new THREE.WebGLRenderer({{antialias:true, alpha:true}});
    renderer.setClearColor(0x17191C, 1);
    renderer.setSize(window.innerWidth * 0.5, 450);
    document.body.appendChild(renderer.domElement);

    // Lichtsetup (heller & weicher)
    const key = new THREE.DirectionalLight(0xffffff, 1.6);
    key.position.set(700, 1000, 800);
    key.castShadow = true;
    scene.add(key);
    const fill = new THREE.DirectionalLight(0xfff0d0, 0.8);
    fill.position.set(-600, 400, -500);
    scene.add(fill);
    scene.add(new THREE.AmbientLight(0xffffff, 0.5));

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

    const mat = new THREE.MeshStandardMaterial({{color: {base_color}, metalness: 1.0, roughness: 0.15}});
    const coil = new THREE.Mesh(geom, mat);
    coil.castShadow = true;
    scene.add(coil);

    // Kamera automatisch zentrieren & leicht näher
    const box = new THREE.Box3().setFromObject(coil);
    const size = new THREE.Vector3(); box.getSize(size);
    const center = new THREE.Vector3(); box.getCenter(center);
    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = camera.fov * Math.PI/180;
    let dist = (maxDim/2)/Math.tan(fov/2);
    dist *= 1.2;  // näher ran
    camera.position.set(center.x + dist*0.7, center.y + dist*0.25, center.z + dist);
    camera.lookAt(center);

    renderer.render(scene, camera);
    </script></body></html>
    """
    components.html(master_html, height=450)

    # ---------- Zuschnitt-Coils ----------
    st.markdown("### ✂️ Coil mit Zuschnitten (gestapelt)")
    cuts_js_list = ",".join([str(c) for c in cuts]) if cuts else "[]"
    colors_js = ",".join([
        str(int(color_map[MATERIAL], 16) - (i * 0x111111)) for i in range(len(cuts))
    ]) if cuts else "[]"

    cuts_html = f"""
    <html><body style="margin:0; background:#17191C; display:flex; justify-content:center; align-items:center;">
    <script src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.min.js"></script>
    <script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(50, 1.1, 1, 20000);
    const renderer = new THREE.WebGLRenderer({{antialias:true, alpha:true}});
    renderer.setClearColor(0x17191C, 1);
    renderer.setSize(window.innerWidth * 0.5, 450);
    document.body.appendChild(renderer.domElement);

    // Helleres Licht
    const key = new THREE.DirectionalLight(0xffffff, 1.6);
    key.position.set(700, 1000, 800);
    scene.add(key);
    const fill = new THREE.DirectionalLight(0xfff0d0, 0.8);
    fill.position.set(-600, 400, -500);
    scene.add(fill);
    scene.add(new THREE.AmbientLight(0xffffff, 0.5));

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
        const mat = new THREE.MeshStandardMaterial({{color: colors[i % colors.length], metalness:1.0, roughness:0.15}});
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

    // Kamera mittiger & näher
    const box = new THREE.Box3().setFromObject(scene);
    const size = new THREE.Vector3(); box.getSize(size);
    const center = new THREE.Vector3(); box.getCenter(center);
    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = camera.fov * Math.PI/180;
    let dist = (maxDim/2)/Math.tan(fov/2);
    dist *= 1.2;
    camera.position.set(center.x + dist*0.7, center.y + dist*0.25, center.z + dist);
    camera.lookAt(center);

    renderer.render(scene, camera);
    </script></body></html>
    """
    components.html(cuts_html, height=450)
