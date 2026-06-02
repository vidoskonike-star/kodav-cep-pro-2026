import streamlit as st
import pandas as pd
import os

# =====================================================
# CONFIGURATION PAGE
# =====================================================

st.set_page_config(
    page_title="Gestion des candidats",
    page_icon="🎓",
    layout="wide"
)

# =====================================================
# SÉCURITÉ SESSION
# =====================================================

if "authentication_status" not in st.session_state:
    st.error("Veuillez vous connecter")
    st.stop()

if st.session_state["authentication_status"] is not True:
    st.error("Accès refusé")
    st.stop()

# =====================================================
# STYLE SAAS SIMPLE (HARMONISÉ APP)
# =====================================================

st.markdown("""
<style>

h1, h2, h3 {
    color: white;
}

.block-title {
    font-size: 28px;
    font-weight: 800;
    color: white;
    margin-top: 20px;
    margin-bottom: 10px;
}

.card {
    background: rgba(255,255,255,0.08);
    padding: 18px;
    border-radius: 18px;
    backdrop-filter: blur(10px);
    box-shadow: 0px 0px 15px rgba(0,0,0,0.2);
    color: white;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# TITRE
# =====================================================

st.title("🎓 Gestion des candidats CEP")

st.success(f"Bienvenue {st.session_state['name']}")

# =====================================================
# DOSSIER DATA
# =====================================================

os.makedirs("data", exist_ok=True)

FICHIER_CANDIDATS = "data/candidats.xlsx"
FICHIER_NOTES = "data/notes.xlsx"

# =====================================================
# INIT FICHIER
# =====================================================

if not os.path.exists(FICHIER_CANDIDATS):

    df_init = pd.DataFrame(columns=[
        "N° Table", "Nom", "Prénoms", "Sexe", "Ecole de provenance"
    ])

    df_init.to_excel(FICHIER_CANDIDATS, index=False)

# =====================================================
# CHARGEMENT
# =====================================================

df = pd.read_excel(FICHIER_CANDIDATS)

df["N° Table"] = pd.to_numeric(df["N° Table"], errors="coerce")

# =====================================================
# FORMULAIRE
# =====================================================

st.markdown("### ➕ Ajouter un candidat")

with st.form("formulaire_candidat"):

    col1, col2 = st.columns(2)

    with col1:
        numero_table = st.text_input("N° Table")
        nom = st.text_input("Nom")

    with col2:
        prenoms = st.text_input("Prénoms")
        sexe = st.selectbox("Sexe", ["Masculin", "Féminin"])

    ecole = st.text_input("École de provenance")

    enregistrer = st.form_submit_button("💾 Enregistrer")

# =====================================================
# ENREGISTREMENT
# =====================================================

if enregistrer:

    if numero_table == "" or nom == "" or prenoms == "" or ecole == "":
        st.warning("Veuillez remplir tous les champs")

    else:

        numero_table = pd.to_numeric(numero_table, errors="coerce")

        if pd.isna(numero_table):
            st.error("❌ Numéro de table invalide")

        elif (df["N° Table"] == numero_table).any():
            st.error("❌ Ce numéro de table existe déjà")

        else:

            nouveau = pd.DataFrame([{
                "N° Table": numero_table,
                "Nom": nom.upper(),
                "Prénoms": prenoms.title(),
                "Sexe": sexe,
                "Ecole de provenance": ecole.upper()
            }])

            df = pd.concat([df, nouveau], ignore_index=True)
            df = df.sort_values(by="N° Table")
            df.to_excel(FICHIER_CANDIDATS, index=False)

            # =================================================
            # CREATION NOTES
            # =================================================

            if os.path.exists(FICHIER_NOTES):
                df_notes = pd.read_excel(FICHIER_NOTES)
            else:
                df_notes = pd.DataFrame()

            nouvelle_note = pd.DataFrame([{
                "N° Table": numero_table,
                "Nom": nom.upper(),
                "Prénoms": prenoms.title(),
                "Sexe": sexe,
                "Ecole de provenance": ecole.upper(),
                "Lecture": 0.0,
                "Exp écrite": 0.0,
                "Dictée": 0.0,
                "Math": 0.0,
                "EST": 0.0,
                "ES": 0.0,
                "EA/Dessin/Couture": 0.0,
                "EA/Chant-Poésie": 0.0,
                "EPS": 0.0,
                "Total": 0.0,
                "Moy 6/9": 0.0,
                "Moyenne": 0.0,
                "Rang": "",
                "OBS": ""
            }])

            df_notes = pd.concat([df_notes, nouvelle_note], ignore_index=True)
            df_notes.to_excel(FICHIER_NOTES, index=False)

            st.success("✅ Candidat enregistré avec succès")
            st.rerun()

# =====================================================
# IMPORT EXCEL
# =====================================================

st.markdown("### 📥 Import Excel")

fichier_import = st.file_uploader("Importer fichier", type=["xlsx"])

if fichier_import is not None:

    df_import = pd.read_excel(fichier_import)
    st.dataframe(df_import.head(), use_container_width=True)

    if st.button("📥 Importer"):

        df_import["N° Table"] = pd.to_numeric(df_import["N° Table"], errors="coerce")
        df_import = df_import.sort_values(by="N° Table")

        df_import.to_excel(FICHIER_CANDIDATS, index=False)

        df_notes = df_import.copy()

        for col in [
            "Lecture","Exp écrite","Dictée","Math","EST","ES",
            "EA/Dessin/Couture","EA/Chant-Poésie","EPS",
            "Total","Moy 6/9","Moyenne"
        ]:
            df_notes[col] = 0.0

        df_notes["Rang"] = ""
        df_notes["OBS"] = ""

        df_notes.to_excel(FICHIER_NOTES, index=False)

        st.success("✅ Import réussi")
        st.rerun()

# =====================================================
# AFFICHAGE
# =====================================================

st.markdown("### 📋 Liste des candidats")

st.dataframe(df.sort_values(by="N° Table"), use_container_width=True, height=450)

# =====================================================
# STATISTIQUES
# =====================================================

col1, col2, col3 = st.columns(3)

col1.metric("👨 Masculins", len(df[df["Sexe"] == "Masculin"]))
col2.metric("👩 Féminins", len(df[df["Sexe"] == "Féminin"]))
col3.metric("🎓 Total", len(df))

# =====================================================
# EXPORT
# =====================================================

with open(FICHIER_CANDIDATS, "rb") as f:
    st.download_button(
        "⬇️ Télécharger Excel",
        f,
        file_name="candidats.xlsx"
    )

# =====================================================
# RESET
# =====================================================

st.markdown("### 🗑️ Réinitialisation")

col1, col2 = st.columns(2)

with col1:
    if st.button("❌ Supprimer candidats"):
        os.remove(FICHIER_CANDIDATS)
        st.rerun()

with col2:
    if st.button("⚠️ Supprimer notes"):
        if os.path.exists(FICHIER_NOTES):
            os.remove(FICHIER_NOTES)
        st.rerun()

# =====================================================
# RETOUR
# =====================================================

if st.button("🏠 Accueil"):
    st.switch_page("app.py")