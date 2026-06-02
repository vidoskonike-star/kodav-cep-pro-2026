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
# FONCTIONS UTILITAIRES
# =====================================================
def set_background(image_path):
    """Applique un fond d’écran institutionnel"""
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.55)),
                        url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """, unsafe_allow_html=True)

def load_excel(file_path):
    """Charge le fichier Excel et calcule les statistiques"""
    stats = {"total": 0, "notes": 0, "admissibles": 0, "releves": 0}
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        stats["total"] = len(df)
        if "Moyenne" in df.columns and stats["total"] > 0:
            stats["notes"] = round((df["Moyenne"].fillna(0).gt(0).sum() / stats["total"]) * 100)
            stats["admissibles"] = len(df[df["Moyenne"] >= 10])
        stats["releves"] = stats["total"]
    return stats

# =====================================================
# CHARGEMENT CONFIGURATION
# =====================================================
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

# =====================================================
# STYLE GLOBAL
# =====================================================
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

set_background("assets/background.png")

# =====================================================
# AUTHENTIFICATION
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

    st.markdown("""
    <div class="main-title">🎓 KODAV CEP PRO</div>
    <div class="sub-title">Plateforme professionnelle de gestion des centres d’examen CEP</div>
    """, unsafe_allow_html=True)

    stats = load_excel("data/notes.xlsx")

    col1, col2, col3, col4 = st.columns(4)
    cards = [
        ("👨🏽‍🎓 Candidats", stats["total"]),
        ("📝 Notes saisies", f"{stats['notes']}%"),
        ("🏆 Admissibles", stats["admissibles"]),
        ("📄 Relevés", stats["releves"])
    ]

    for col, (title, value) in zip([col1, col2, col3, col4], cards):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.progress(stats["notes"] / 100)

    st.markdown("## 🚀 Modules disponibles")
    col1, col2, col3 = st.columns(3)
    modules = [
        ("👨🏽‍🎓 Candidats", "pages/candidat.py"),
        ("📝 Notes", "pages/notes.py"),
        ("⚡ Saisie Rapide", "pages/saisie_rapide.py"),
        ("🏆 Synthèse CEP", "pages/synthese.py"),
        ("📄 Relevés CEP", "pages/releves.py")
    ]

    for label, page in modules:
        if st.button(label, use_container_width=True):
            st.switch_page(page)

    st.success("✅ Plateforme opérationnelle avec succès")

elif st.session_state["authentication_status"] is False:
    st.error("❌ Nom d'utilisateur ou mot de passe incorrect")

else:
    st.warning("🔐 Veuillez vous connecter")
