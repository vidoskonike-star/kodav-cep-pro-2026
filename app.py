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
# IMPORT DU STYLE
# =====================================================
from utils.styl import load_css
load_css()   # applique ton CSS premium

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
# STATISTIQUES
# =====================================================
fichier_excel = "data/notes.xlsx"

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
    st.error(f"Erreur lors du chargement des données : {e}")

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

    authenticator.logout("Déconnexion", "sidebar")

    st.sidebar.success(f"Bienvenue {st.session_state['name']}")
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
        <div class="card">
            <h3>👨🏽‍🎓 Candidats</h3>
            <p style="color:gold;font-size:28px;font-weight:800;">{total_candidats}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card">
            <h3>📝 Notes saisies</h3>
            <p style="color:gold;font-size:28px;font-weight:800;">{notes_saisies}%</p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(notes_saisies / 100)

    with col3:
        st.markdown(f"""
        <div class="card">
            <h3>🏆 Admissibles</h3>
            <p style="color:gold;font-size:28px;font-weight:800;">{admissibles}</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="card">
            <h3>📄 Relevés</h3>
            <p style="color:gold;font-size:28px;font-weight:800;">{releves}</p>
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

    st.success("✅ Plateforme opérationnelle avec succès")

elif st.session_state["authentication_status"] is False:
    st.error("❌ Nom d'utilisateur ou mot de passe incorrect")

elif st.session_state["authentication_status"] is None:
    st.warning("🔐 Veuillez vous connecter")
