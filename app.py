import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import base64
import pandas as pd
import os

# =====================================================
# CONFIGURATION PAGE
# =====================================================

st.set_page_config(
    page_title="KODAV CEP PRO",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CHARGEMENT YAML
# =====================================================

with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# =====================================================
# AUTHENTIFICATION
# =====================================================

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

# =====================================================
# BACKGROUND IMAGE (SAFE VERSION)
# =====================================================

def get_base64(bin_file):
    if not os.path.exists(bin_file):
        return None
    with open(bin_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg = get_base64("assets/background.png")

background_css = ""

if bg:
    background_css = f"""
    url("data:image/png;base64,{bg}")
    """

# =====================================================
# DESIGN SaaS PREMIUM CSS
# =====================================================

st.markdown(f"""
<style>

/* ================================================= */
/* BACKGROUND */
/* ================================================= */

.stApp {{
    background-image:
    linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.55)),
    {background_css};

    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

/* ================================================= */
/* TITRES */
/* ================================================= */

.main-title {{
    text-align:center;
    font-size:60px;
    font-weight:900;
    color:white;
    text-shadow:0px 0px 20px rgba(0,0,0,0.6);
    margin-top:10px;
}}

.sub-title {{
    text-align:center;
    font-size:20px;
    color:#e0e0e0;
    margin-bottom:30px;
}}

/* ================================================= */
/* SIDEBAR */
/* ================================================= */

section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, rgba(0,0,0,0.7), rgba(20,20,20,0.9));
}}

section[data-testid="stSidebar"] * {{
    color:white !important;
}}

/* ================================================= */
/* METRICS (CARDS) */
/* ================================================= */

.metric-card {{
    background: rgba(255,255,255,0.08);
    padding:20px;
    border-radius:20px;
    text-align:center;
    backdrop-filter: blur(10px);
    box-shadow:0px 0px 20px rgba(0,0,0,0.2);
}}

.metric-title {{
    color:white;
    font-size:16px;
}}

.metric-value {{
    color:gold;
    font-size:32px;
    font-weight:800;
}}

/* ================================================= */
/* BUTTONS */
/* ================================================= */

div.stButton > button {{
    background: linear-gradient(90deg, #0072ff, #00c6ff);
    color:white;
    border:none;
    padding:12px;
    border-radius:12px;
    font-weight:700;
    transition:0.3s;
}}

div.stButton > button:hover {{
    transform:scale(1.03);
    box-shadow:0px 0px 15px rgba(0,114,255,0.6);
}}

</style>
""", unsafe_allow_html=True)

# =====================================================
# LOGIN
# =====================================================

try:
    authenticator.login()
except Exception as e:
    st.error(e)

# =====================================================
# PAGE CONNECTÉE
# =====================================================

if st.session_state["authentication_status"]:

    username = st.session_state.get("username")
    user_config = config["credentials"]["usernames"].get(username, {})
    st.session_state["role"] = user_config.get("role", "teacher")
    centre_config = user_config.get("centre", "CENTRE_PAR_DEFAUT")

    if centre_config == "ALL":
        centres_disponibles = sorted(
            [
                nom
                for nom in os.listdir("data")
                if os.path.isdir(os.path.join("data", nom))
            ]
        )
        if not centres_disponibles:
            centres_disponibles = ["CENTRE_PAR_DEFAUT"]

        centre = st.sidebar.selectbox("Centre actif", centres_disponibles)
    else:
        centre = centre_config

    st.session_state["centre"] = centre
    fichier_excel = os.path.join("data", centre, "notes.xlsx")

    total_candidats = 0
    notes_saisies = 0
    admissibles = 0
    releves = 0

    try:
        if os.path.exists(fichier_excel):
            df = pd.read_excel(fichier_excel)
            total_candidats = len(df)

            if "Moyenne" in df.columns and total_candidats > 0:
                notes_saisies = round(
                    (df["Moyenne"].fillna(0).gt(0).sum() / total_candidats) * 100
                )
                admissibles = len(df[df["Moyenne"] >= 10])

            releves = total_candidats
    except Exception as e:
        st.warning(f"Impossible de charger les statistiques du centre {centre}: {e}")

    authenticator.logout("Déconnexion", "sidebar")

    st.sidebar.success(f"Bienvenue {st.session_state['name']}")
    st.sidebar.info(f"Centre : {centre}")
    st.sidebar.info("KODAV CEP PRO 2026")

    # =================================================
    # HEADER
    # =================================================

    st.markdown("""
    <div class="main-title">🎓 KODAV CEP PRO</div>
    <div class="sub-title">Plateforme professionnelle de gestion des centres d’examen CEP</div>
    """, unsafe_allow_html=True)

    # =================================================
    # DASHBOARD CARDS
    # =================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">👨🏽‍🎓 Candidats</div>
            <div class="metric-value">{total_candidats}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">📝 Notes saisies</div>
            <div class="metric-value">{notes_saisies}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">🏆 Admissibles</div>
            <div class="metric-value">{admissibles}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">📄 Relevés</div>
            <div class="metric-value">{releves}</div>
        </div>
        """, unsafe_allow_html=True)

    # =================================================
    # MODULES
    # =================================================

    st.markdown("## 🚀 Modules disponibles")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("👨🏽‍🎓 Candidats", use_container_width=True):
            st.switch_page("pages/candidat.py")

    with col2:
        if st.button("📝 Notes", use_container_width=True):
            st.switch_page("pages/notes.py")

    with col3:
        if st.button("⚡ Saisie Rapide", use_container_width=True):
            st.switch_page("pages/saisie_rapide.py")

    col4, col5 = st.columns(2)

    with col4:
        if st.button("🏆 Synthèse CEP", use_container_width=True):
            st.switch_page("pages/synthese.py")

    with col5:
        if st.button("📄 Relevés CEP", use_container_width=True):
            st.switch_page("pages/releves.py")

    if st.session_state.get("role") in {"admin", "circonscription"}:
        if st.button("📊 Synthèse Circonscription", use_container_width=True):
            st.switch_page("pages/admin_circ.py")

    st.success("✅ Plateforme opérationnelle avec succès")

elif st.session_state["authentication_status"] is False:
    st.error("❌ Nom d'utilisateur ou mot de passe incorrect")

elif st.session_state["authentication_status"] is None:
    st.warning("🔐 Veuillez vous connecter")
