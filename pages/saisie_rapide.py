import streamlit as st
import pandas as pd
import os

# =====================================================
# CONFIGURATION PAGE
# =====================================================

st.set_page_config(
    page_title="Saisie Rapide",
    page_icon="⚡",
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
# STYLE SIMPLE PREMIUM (AMÉLIORATION UX)
# =====================================================

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}
.stDataFrame {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# TITRE
# =====================================================

st.title("⚡ Saisie Rapide des Notes CEP")
st.success(f"Bienvenue {st.session_state['name']}")

# =====================================================
# DOSSIERS
# =====================================================

os.makedirs("data", exist_ok=True)

FICHIER_CANDIDATS = "data/candidats.xlsx"
FICHIER_NOTES = "data/notes.xlsx"

# =====================================================
# VÉRIFICATION
# =====================================================

if not os.path.exists(FICHIER_CANDIDATS):
    st.error("Aucun candidat enregistré")
    st.stop()

# =====================================================
# CRÉATION AUTO NOTES SI ABSENT
# =====================================================

colonnes = [
    "N° Table", "Nom", "Prénoms", "Sexe", "Ecole de provenance",
    "Lecture", "Exp écrite", "Dictée", "Math", "EST",
    "ES", "EA/Dessin/Couture", "EA/Chant-Poésie", "EPS",
    "Total", "Moy 6/9", "Moyenne", "Rang", "OBS"
]

if not os.path.exists(FICHIER_NOTES):
    pd.DataFrame(columns=colonnes).to_excel(FICHIER_NOTES, index=False)

# =====================================================
# CHARGEMENT
# =====================================================

df_candidats = pd.read_excel(FICHIER_CANDIDATS)
df_notes = pd.read_excel(FICHIER_NOTES)

# =====================================================
# MATIÈRES
# =====================================================

matieres = [
    "Lecture", "Exp écrite", "Dictée", "Math", "EST",
    "ES", "EA/Dessin/Couture", "EA/Chant-Poésie", "EPS"
]

matiere = st.selectbox("📘 Choisir une matière", matieres)

st.subheader(f"✍️ Saisie rapide : {matiere}")

# =====================================================
# SYNCHRONISATION CANDIDATS → NOTES
# =====================================================

for _, row in df_candidats.iterrows():

    num = row["N° Table"]

    if not (df_notes["N° Table"].astype(str) == str(num)).any():

        nouvelle_ligne = {
            "N° Table": num,
            "Nom": row["Nom"],
            "Prénoms": row["Prénoms"],
            "Sexe": row["Sexe"],
            "Ecole de provenance": row["Ecole de provenance"],
        }

        for m in matieres:
            nouvelle_ligne[m] = 0.0

        nouvelle_ligne.update({
            "Total": 0.0,
            "Moy 6/9": 0.0,
            "Moyenne": 0.0,
            "Rang": "",
            "OBS": ""
        })

        df_notes = pd.concat([df_notes, pd.DataFrame([nouvelle_ligne])], ignore_index=True)

# =====================================================
# TRI
# =====================================================

df_notes["N° Table"] = pd.to_numeric(df_notes["N° Table"], errors="coerce")
df_notes = df_notes.sort_values(by="N° Table")

# conversion matière
df_notes[matiere] = pd.to_numeric(df_notes[matiere], errors="coerce").fillna(0.0)

# nom complet
df_notes["Nom complet"] = df_notes["Nom"].astype(str) + " " + df_notes["Prénoms"].astype(str)

# =====================================================
# TABLEAU EDITABLE
# =====================================================

df_saisie = df_notes[["N° Table", "Nom complet", matiere]].copy()

edited_df = st.data_editor(
    df_saisie,
    use_container_width=True,
    hide_index=True,
    num_rows="fixed",
    column_config={
        "N° Table": st.column_config.NumberColumn(disabled=True),
        "Nom complet": st.column_config.TextColumn(disabled=True),
        matiere: st.column_config.NumberColumn(
            matiere,
            min_value=0,
            max_value=20,
            step=0.5,
            format="%.1f"
        )
    }
)

# =====================================================
# SAUVEGARDE
# =====================================================

if st.button("💾 Enregistrer", use_container_width=True):

    # mise à jour matière
    df_notes[matiere] = edited_df[matiere]

    # recalcul total
    df_notes["Total"] = df_notes[matieres].sum(axis=1)

    # moyenne
    df_notes["Moyenne"] = (df_notes["Total"] / 9).round(2)
    df_notes["Moy 6/9"] = (df_notes["Total"] / 6).round(2)

    # observation
    df_notes["OBS"] = df_notes["Moyenne"].apply(
        lambda x: "Admis" if x >= 10 else "Ajourné"
    )

    # rang
    df_notes["Rang"] = df_notes["Total"].rank(ascending=False, method="min").astype(int)

    # nettoyage
    df_notes.drop(columns=["Nom complet"], inplace=True, errors="ignore")

    # sauvegarde
    df_notes.to_excel(FICHIER_NOTES, index=False)

    st.success("✅ Notes enregistrées avec succès")
    st.rerun()

# =====================================================
# APERÇU GLOBAL
# =====================================================

st.subheader("📊 Aperçu global")

st.dataframe(df_notes, use_container_width=True, height=500)

# =====================================================
# DOWNLOAD
# =====================================================

with open(FICHIER_NOTES, "rb") as f:
    st.download_button(
        "⬇️ Télécharger notes.xlsx",
        f,
        file_name="notes.xlsx",
        use_container_width=True
    )

# =====================================================
# RETOUR
# =====================================================

if st.button("🏠 Retour accueil", use_container_width=True):
    st.switch_page("app.py")