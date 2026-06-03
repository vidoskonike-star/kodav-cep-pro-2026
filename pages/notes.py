import streamlit as st
import pandas as pd
import os

# =====================================================
# CONFIGURATION PAGE
# =====================================================

st.set_page_config(
    page_title="Saisie des notes",
    page_icon="📝",
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
# STYLE
# =====================================================

st.markdown("""
<style>

h1, h2, h3 {
    color: white;
}

.card {
    background: rgba(255,255,255,0.08);
    padding: 18px;
    border-radius: 18px;
    backdrop-filter: blur(10px);
    color: white;
    box-shadow: 0px 0px 15px rgba(0,0,0,0.2);
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# FICHIERS
# =====================================================

os.makedirs("data", exist_ok=True)

FICHIER_NOTES = "data/notes.xlsx"

if not os.path.exists(FICHIER_NOTES):
    st.error("Fichier notes introuvable")
    st.stop()

# =====================================================
# CHARGEMENT
# =====================================================

df_notes = pd.read_excel(FICHIER_NOTES)

if len(df_notes) == 0:
    st.error("Aucun candidat trouvé")
    st.stop()

# =====================================================
# NETTOYAGE MATIÈRES
# =====================================================

colonnes_notes = [
    "Lecture", "Exp écrite", "Dictée", "Math",
    "EST", "ES", "EA/Dessin/Couture",
    "EA/Chant-Poésie", "EPS"
]

df_notes["Nom complet"] = df_notes["Nom"] + " " + df_notes["Prénoms"]

# =====================================================
# CHOIX CANDIDAT
# =====================================================

st.title("📝 Saisie des notes CEP")

candidat = st.selectbox(
    "🎓 Choisir un candidat",
    df_notes["Nom complet"].tolist()
)

ligne = df_notes[df_notes["Nom complet"] == candidat].index[0]

# =====================================================
# INFOS
# =====================================================

col1, col2, col3 = st.columns(3)

col1.markdown(f"""
<div class="card">
<b>N° Table</b><br>
{df_notes.loc[ligne, "N° Table"]}
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="card">
<b>Sexe</b><br>
{df_notes.loc[ligne, "Sexe"]}
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="card">
<b>École</b><br>
{df_notes.loc[ligne, "Ecole de provenance"]}
</div>
""", unsafe_allow_html=True)

# =====================================================
# DETECTION ABSENCE
# =====================================================

is_absent = (df_notes.loc[ligne, colonnes_notes] == -1).any()

if is_absent:
    st.error("🚫 CANDIDAT ABSENT (au moins une matière)")
else:
    st.success("✅ Candidat présent")

# =====================================================
# FORMULAIRE
# =====================================================

st.markdown("### ✍️ Saisie des notes")

with st.form("form_notes"):

    valeurs = {}

    for col in colonnes_notes:
        val = df_notes.loc[ligne, col]

        if val == -1:
            val = 0.0

        valeurs[col] = st.number_input(
            col,
            0.0,
            20.0,
            float(val)
        )

    absent_global = st.checkbox("🚫 Marquer tout le candidat comme absent")

    submit = st.form_submit_button("💾 Enregistrer")

# =====================================================
# SAUVEGARDE
# =====================================================

if submit:

    if absent_global:
        df_notes.loc[ligne, colonnes_notes] = -1
        df_notes.loc[ligne, "Total"] = 0
        df_notes.loc[ligne, "Moyenne"] = 0
        df_notes.loc[ligne, "Moy 6/9"] = 0
        df_notes.loc[ligne, "OBS"] = "ABSENT"
        df_notes.loc[ligne, "Rang"] = ""
    else:

        df_notes.loc[ligne, colonnes_notes] = [
            valeurs[col] for col in colonnes_notes
        ]

        # =================================================
        # REGLE ABSENCE GLOBALE
        # =================================================

        if (df_notes.loc[ligne, colonnes_notes] == -1).any():
            df_notes.loc[ligne, "Total"] = 0
            df_notes.loc[ligne, "Moyenne"] = 0
            df_notes.loc[ligne, "Moy 6/9"] = 0
            df_notes.loc[ligne, "OBS"] = "ABSENT"
            df_notes.loc[ligne, "Rang"] = ""

        else:

            df_notes["Total"] = df_notes[colonnes_notes].sum(axis=1)

            df_notes["Moyenne"] = (df_notes["Total"] / 9).round(2)

            df_notes["Moy 6/9"] = (df_notes["Total"] / 6).round(2)

            df_notes["OBS"] = df_notes["Moyenne"].apply(
                lambda x: "Admis" if x >= 10 else "Ajourné"
            )

            df_notes["Rang"] = df_notes["Total"].rank(
                ascending=False
            ).astype(int)

    df_notes.to_excel(FICHIER_NOTES, index=False)

    st.success("✅ Enregistré avec succès")
    st.rerun()

# =====================================================
# TABLEAU
# =====================================================

st.markdown("### 📋 Tableau des notes")

df_affichage = df_notes.copy()

for col in colonnes_notes:
    df_affichage[col] = df_affichage[col].replace(-1, "ABS")

st.dataframe(df_affichage, use_container_width=True, height=450)

# =====================================================
# EXPORT
# =====================================================

with open(FICHIER_NOTES, "rb") as f:
    st.download_button("⬇️ Télécharger Excel", f, file_name="notes.xlsx")

# =====================================================
# RESET
# =====================================================

st.markdown("### 🗑️ Réinitialisation")

if st.button("❌ Supprimer toutes les notes"):
    df_vide = pd.DataFrame(columns=df_notes.columns)
    df_vide.to_excel(FICHIER_NOTES, index=False)
    st.rerun()

# =====================================================
# RETOUR
# =====================================================

if st.button("🏠 Accueil"):
    st.switch_page("app.py")