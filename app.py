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
    page_title="KODAV CEP",
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
# IMAGE FOND PERSONNALISÉE
# =====================================================

def get_base64(bin_file):

    with open(bin_file, "rb") as f:
        data = f.read()

    return base64.b64encode(data).decode()

bg = get_base64("assets/background.jpg")

# =====================================================
# CALCUL STATISTIQUES AUTOMATIQUES
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
                (
                    df["Moyenne"]
                    .fillna(0)
                    .gt(0)
                    .sum()
                    / total_candidats
                ) * 100
            )

            admissibles = len(
                df[df["Moyenne"] >= 10]
            )

        releves = total_candidats

except:
    pass

# =====================================================
# CSS ULTRA PREMIUM
# =====================================================

page_style = f"""
<style>

#MainMenu {{
    visibility: hidden;
}}

footer {{
    visibility: hidden;
}}

header {{
    visibility: visible;
}}

html, body, [class*="css"] {{
    font-family: 'Segoe UI', sans-serif;
}}

/* ================================================= */
/* FOND GENERAL */
/* ================================================= */

.stApp {{

    background-image:
    linear-gradient(
        rgba(255,255,255,0.70),
        rgba(255,255,255,0.70)
    ),
    url("data:image/jpg;base64,{bg}");

    background-size: cover;

    background-position: center;

    background-repeat: no-repeat;

    background-attachment: fixed;

    background-color: #f4f6f9;
}}

/* ================================================= */
/* FLECHE SIDEBAR */
/* ================================================= */

button[kind="header"] {{

    background: rgba(13,71,161,0.75) !important;

    border-radius: 12px !important;

    border: 1px solid rgba(255,255,255,0.25) !important;

    backdrop-filter: blur(8px);

    color: white !important;

    margin-left: 10px !important;

    margin-top: 10px !important;

    width: 46px !important;

    height: 46px !important;

    transition: 0.3s;
}}

button[kind="header"]:hover {{

    background: rgba(24,119,242,0.95) !important;

    transform: scale(1.05);
}}

/* ================================================= */
/* ANIMATIONS */
/* ================================================= */

@keyframes fadeUp {{

    from {{
        opacity: 0;
        transform: translateY(30px);
    }}

    to {{
        opacity: 1;
        transform: translateY(0px);
    }}
}}

@keyframes pulse {{

    0% {{
        transform: scale(1);
    }}

    50% {{
        transform: scale(1.02);
    }}

    100% {{
        transform: scale(1);
    }}
}}

@keyframes glowBlue {{

    0% {{
        box-shadow:
        0px 0px 12px rgba(24,119,242,0.4),
        0px 0px 6px rgba(255,215,0,0.3);
    }}

    50% {{
        box-shadow:
        0px 0px 24px rgba(24,119,242,0.7),
        0px 0px 14px rgba(255,215,0,0.7);
    }}

    100% {{
        box-shadow:
        0px 0px 12px rgba(24,119,242,0.4),
        0px 0px 6px rgba(255,215,0,0.3);
    }}
}}

@keyframes goldShine {{

    0% {{
        left: -40%;
    }}

    100% {{
        left: 120%;
    }}
}}

/* ================================================= */
/* TITRES */
/* ================================================= */

.main-title {{

    text-align: center;

    font-size: 76px;

    font-weight: 900;

    color: #0d47a1;

    margin-top: 10px;

    animation: pulse 4s infinite;

    text-shadow:
    0px 3px 10px rgba(255,255,255,0.9);
}}

.sub-title {{

    text-align: center;

    font-size: 26px;

    color: #111;

    font-weight: 700;

    margin-bottom: 40px;

    text-shadow:
    0px 2px 6px rgba(255,255,255,0.9);
}}

/* ================================================= */
/* SECTION MODULES */
/* ================================================= */

.modules-title {{

    text-align: center;

    font-size: 42px;

    font-weight: bold;

    color: #0d47a1;

    margin-top: 25px;

    margin-bottom: 40px;

    animation: fadeUp 1s ease;
}}

/* ================================================= */
/* BOUTONS MODULES */
/* ================================================= */

div.stButton > button {{

    width: 100%;

    height: 110px;

    border-radius: 26px;

    border: 2px solid rgba(255,215,0,0.85);

    background:
    linear-gradient(
        135deg,
        rgba(24,119,242,0.82),
        rgba(13,71,161,0.72)
    );

    backdrop-filter: blur(10px);

    color: white;

    font-size: 20px;

    font-weight: 700;

    letter-spacing: 0.5px;

    box-shadow:
    0px 10px 25px rgba(0,0,0,0.25),
    0px 0px 12px rgba(255,215,0,0.35);

    transition: all 0.35s ease;

    margin-bottom: 28px;

    animation:
    fadeUp 1s ease,
    glowBlue 5s infinite;

    text-align: center;
}}

div.stButton > button:hover {{

    transform:
    translateY(-6px)
    scale(1.02);

    background:
    linear-gradient(
        135deg,
        rgba(43,132,255,0.92),
        rgba(24,119,242,0.88)
    );

    border: 2px solid gold;

    box-shadow:
    0px 15px 35px rgba(0,0,0,0.35),
    0px 0px 20px rgba(255,215,0,0.8);
}}

/* ================================================= */
/* STATISTIQUES PREMIUM */
/* ================================================= */

div[data-testid="metric-container"] {{

    background:
    linear-gradient(
        135deg,
        rgba(255,255,255,0.22),
        rgba(255,255,255,0.10)
    );

    backdrop-filter: blur(14px);

    border-radius: 24px;

    padding: 22px;

    border:
    1.5px solid rgba(255,255,255,0.25);

    position: relative;

    overflow: hidden;

    transition: 0.4s ease;

    box-shadow:
    0px 8px 25px rgba(0,0,0,0.18),
    0px 0px 12px rgba(255,215,0,0.18),
    inset 0px 0px 12px rgba(255,255,255,0.08);
}}

div[data-testid="metric-container"]::before {{

    content: "";

    position: absolute;

    top: -40%;

    left: -20%;

    width: 140%;

    height: 80%;

    background:
    linear-gradient(
        120deg,
        transparent,
        rgba(255,215,0,0.22),
        transparent
    );

    transform: rotate(8deg);

    animation: goldShine 6s linear infinite;
}}

div[data-testid="metric-container"]::after {{

    content: "";

    position: absolute;

    inset: 0;

    border-radius: 24px;

    padding: 1.5px;

    background:
    linear-gradient(
        135deg,
        rgba(255,215,0,0.9),
        rgba(255,255,255,0.2),
        rgba(24,119,242,0.8),
        rgba(255,215,0,0.9)
    );

    pointer-events: none;
}}

div[data-testid="metric-container"] label {{

    color: white !important;

    font-size: 18px !important;

    font-weight: 600 !important;
}}

div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{

    color: gold !important;

    font-size: 34px !important;

    font-weight: 800 !important;

    text-shadow:
    0px 0px 12px rgba(255,215,0,0.45);
}}

div[data-testid="metric-container"]:hover {{

    transform:
    translateY(-6px)
    scale(1.02);

    box-shadow:
    0px 12px 35px rgba(0,0,0,0.28),
    0px 0px 18px rgba(255,215,0,0.45),
    0px 0px 20px rgba(24,119,242,0.35);
}}

/* ================================================= */
/* SIDEBAR */
/* ================================================= */

section[data-testid="stSidebar"] {{

    background:
    linear-gradient(
        180deg,
        rgba(66,165,245,0.42),
        rgba(13,71,161,0.28)
    ) !important;

    backdrop-filter: blur(10px);

    border-right:
    1px solid rgba(255,255,255,0.20);
}}

section[data-testid="stSidebar"] * {{

    color: white !important;
}}

/* ================================================= */
/* BOUTON DECONNEXION */
/* ================================================= */

section[data-testid="stSidebar"] .stButton > button {{

    background: #d32f2f !important;

    width: 100% !important;

    height: 55px !important;

    border-radius: 14px !important;

    border: none !important;

    font-size: 18px !important;

    font-weight: 700 !important;

    margin-top: 20px !important;

    animation: none !important;

    box-shadow:
    0px 6px 18px rgba(0,0,0,0.25) !important;
}}

section[data-testid="stSidebar"] .stButton > button:hover {{

    background: #b71c1c !important;

    transform: scale(1.02);
}}

/* ================================================= */
/* MESSAGE FINAL */
/* ================================================= */

.success-box {{

    margin-top: 45px;

    padding: 22px;

    border-radius: 22px;

    text-align: center;

    font-size: 22px;

    font-weight: bold;

    color: #0d47a1;

    background:
    linear-gradient(
        135deg,
        rgba(255,255,255,0.90),
        rgba(230,240,255,0.82)
    );

    box-shadow:
    0px 8px 25px rgba(0,0,0,0.15);

    backdrop-filter: blur(8px);

    animation: fadeUp 1s ease;
}}

</style>
"""

st.markdown(page_style, unsafe_allow_html=True)

# =====================================================
# CONNEXION
# =====================================================

try:

    authenticator.login()

except Exception as e:

    st.error(e)

# =====================================================
# UTILISATEUR CONNECTÉ
# =====================================================

if st.session_state["authentication_status"]:

    authenticator.logout(
        "Déconnexion",
        "sidebar"
    )

    st.sidebar.success(
        f"Bienvenue {st.session_state['name']}"
    )

    st.sidebar.info(
        "KODAV CEP PRO 2026"
    )

    st.markdown("""

    <div class="main-title">
        KODAV CEP PRO
    </div>

    <div class="sub-title">
        Plateforme professionnelle de gestion du centre d’examen blanc CEP
    </div>

    """, unsafe_allow_html=True)

    d1, d2, d3, d4 = st.columns(4)

    with d1:
        st.metric("👨🏽‍🎓 Candidats", total_candidats)

    with d2:
        st.metric("📝 Notes saisies", f"{notes_saisies}%")

    with d3:
        st.metric("🏆 Admissibles", admissibles)

    with d4:
        st.metric("📄 Relevés générés", releves)

    st.markdown("""

    <div class="modules-title">
        🚀 Modules Disponibles
    </div>

    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button("👨🏽‍🎓\nCandidats", use_container_width=True):
            st.switch_page("pages/candidat.py")

    with col2:

        if st.button("📝\nNotes", use_container_width=True):
            st.switch_page("pages/notes.py")

    with col3:

        if st.button("⚡\nSaisie Rapide", use_container_width=True):
            st.switch_page("pages/saisie_rapide.py")

    col4, col5 = st.columns(2)

    with col4:

        if st.button("🏆\nSynthèse CEP", use_container_width=True):
            st.switch_page("pages/synthese.py")

    with col5:

        if st.button("📄\nRelevés CEP", use_container_width=True):
            st.switch_page("pages/releves.py")

    st.markdown("""

    <div class="success-box">
        ✅ Plateforme opérationnelle avec succès
    </div>

    """, unsafe_allow_html=True)

elif st.session_state["authentication_status"] is False:

    st.error(
        "❌ Nom d'utilisateur ou mot de passe incorrect"
    )

elif st.session_state["authentication_status"] is None:

    st.warning(
        "🔐 Veuillez vous connecter"
    )