import streamlit as st

st.set_page_config(page_title="3D Coil Base", layout="wide")

# Sidebar mit Platzhaltern
st.sidebar.title("Parameter")
st.sidebar.radio("RID (mm)", [150, 300, 400, 500], index=1)
st.sidebar.slider("RAD (mm)", 200, 1600, 800, step=10)
st.sidebar.slider("Breite (mm)", 8, 600, 300)
st.sidebar.slider("Dicke (mm)", 0.1, 5.0, 1.0, step=0.1)
st.sidebar.selectbox("Material", ["Stahl", "Kupfer", "Aluminium", "Zink"], index=1)
st.sidebar.radio("Ansicht", ["Isometrisch", "Vorne", "Oben", "Seite"], index=0)

# CSS-Layout: Sidebar links fixiert, rechter Bereich Vollbild
st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            position: fixed !important;
            top: 0;
            left: 0;
            height: 100vh !important;
            width: 320px !important;
            background-color: #1e2328 !important;
            border-right: 1px solid #2f343a !important;
            padding: 18px !important;
            color: #f2f2f2 !important;
            z-index: 10;
        }
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p {
            color: #f2f2f2 !important;
        }
        div[data-testid="stAppViewContainer"] > div:nth-child(1) {
            margin-left: 320px !important;
            height: 100vh !important;
            width: calc(100vw - 320px) !important;
            background: #ffffff !important;
        }
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
            background: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# Platzhalter im Hauptbereich
st.markdown(
    """
    <div style="display:flex;justify-content:center;align-items:center;
                height:100vh;font-size:1.5rem;color:#444;">
        <p><b>3D-Bereich (bereit für Lagerraum / Coil Visualisierung)</b></p>
    </div>
    """,
    unsafe_allow_html=True
)
