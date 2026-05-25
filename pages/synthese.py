import streamlit as st
import pandas as pd
import os

# =====================================================
# CONFIGURATION PAGE
# =====================================================

st.set_page_config(
    page_title="Rangs & Synthèse",
    page_icon="🏆",
    layout="wide"
)

# =====================================================
# SÉCURITÉ
# =====================================================

if "authentication_status" not in st.session_state:

    st.error("Veuillez vous connecter")
    st.stop()

if st.session_state["authentication_status"] is not True:

    st.error("Accès refusé")
    st.stop()

# =====================================================
# TITRE
# =====================================================

st.title("🏆 Rangs & Synthèse CEP")

st.success(
    f"Bienvenue {st.session_state['name']}"
)

# =====================================================
# FICHIER NOTES
# =====================================================

FICHIER_NOTES = "data/notes.xlsx"

# =====================================================
# VÉRIFICATION
# =====================================================

if not os.path.exists(FICHIER_NOTES):

    st.error(
        "Le fichier notes.xlsx est introuvable"
    )

    st.stop()

# =====================================================
# CHARGEMENT
# =====================================================

df = pd.read_excel(
    FICHIER_NOTES
)

# =====================================================
# NETTOYAGE DES DONNÉES
# =====================================================

df = df.dropna(
    subset=["Nom", "Prénoms"],
    how="all"
)

# =====================================================
# CONVERSION NUMÉRIQUE
# =====================================================

df["Moyenne"] = pd.to_numeric(
    df["Moyenne"],
    errors="coerce"
).fillna(0)

df["Total"] = pd.to_numeric(
    df["Total"],
    errors="coerce"
).fillna(0)

# =====================================================
# CONVERSION N° TABLE
# =====================================================

df["N° Table"] = pd.to_numeric(
    df["N° Table"],
    errors="coerce"
)

# =====================================================
# TRI
# =====================================================

df = df.sort_values(
    by="N° Table"
)
# =====================================================
# MATIÈRES
# =====================================================

matieres = [

    "Lecture",
    "Exp écrite",
    "Dictée",
    "Math",
    "EST",
    "ES",
    "EA/Dessin/Couture",
    "EA/Chant-Poésie",
    "EPS"
]

# =====================================================
# CONVERSION NUMÉRIQUE
# =====================================================

for col in matieres:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    ).fillna(0)

# =====================================================
# RECALCUL TOTAL
# =====================================================

df["Total"] = (

    df["Lecture"]
    + df["Exp écrite"]
    + df["Dictée"]
    + df["Math"]
    + df["EST"]
    + df["ES"]
    + df["EA/Dessin/Couture"]
    + df["EA/Chant-Poésie"]
    + df["EPS"]
)

# =====================================================
# RECALCUL MOYENNE
# =====================================================

df["Moyenne"] = round(
    df["Total"] / 9,
    2
)

# =====================================================
# RECALCUL MOY 6/9
# =====================================================

df["Moy 6/9"] = round(
    df["Total"] / 6,
    2
)

# =====================================================
# CLASSEMENT
# =====================================================

df = df.sort_values(
    by="Moyenne",
    ascending=False
).reset_index(drop=True)

# =====================================================
# RANGS
# =====================================================

df["Rang"] = range(
    1,
    len(df) + 1
)

# =====================================================
# OBSERVATION
# =====================================================

df["OBS"] = df["Moyenne"].apply(

    lambda x:
    "Admis"
    if x >= 10
    else "Ajourné"
)

# =====================================================
# SAUVEGARDE
# =====================================================

df.to_excel(
    FICHIER_NOTES,
    index=False
)

# =====================================================
# STATISTIQUES
# =====================================================

nb_admis = len(
    df[df["OBS"] == "Admis"]
)

nb_ajournes = len(
    df[df["OBS"] == "Ajourné"]
)

moyenne_generale = round(
    df["Moyenne"].mean(),
    2
)

# =====================================================
# CARTES STATS
# =====================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "🎓 Admis",
        nb_admis
    )

with col2:

    st.metric(
        "❌ Ajournés",
        nb_ajournes
    )

with col3:

    st.metric(
        "📊 Moyenne Générale",
        moyenne_generale
    )

# =====================================================
# TOP 10
# =====================================================

st.subheader("🥇 Top 10")

st.dataframe(

    df.head(10)[

        [
            "Rang",
            "N° Table",
            "Nom",
            "Prénoms",
            "Moyenne",
            "OBS"
        ]
    ],

    use_container_width=True
)

# =====================================================
# TABLEAU GÉNÉRAL
# =====================================================

st.subheader("📋 Classement Général")

st.dataframe(
    df,
    use_container_width=True,
    height=600
)

# =====================================================
# TÉLÉCHARGEMENT
# =====================================================

with open(FICHIER_NOTES, "rb") as file:

    st.download_button(

        label="📥 Télécharger le classement Excel",

        data=file,

        file_name="classement_CEP.xlsx",

        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

        use_container_width=True
    )

# =====================================================
# RETOUR
# =====================================================

if st.button(
    "🏠 Retour à l'accueil",
    use_container_width=True
):

    st.switch_page("app.py")