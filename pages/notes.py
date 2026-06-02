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
# STYLE SAAS SIMPLE
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
# TITRE
# =====================================================

st.title("📝 Saisie des notes CEP")
st.success(f"Bienvenue {st.session_state['name']}")

# =====================================================
# FICHIERS
# =====================================================

os.makedirs("data", exist_ok=True)

FICHIER_CANDIDATS = "data/candidats.xlsx"
FICHIER_NOTES = "data/notes.xlsx"

# =====================================================
# CONTRÔLE
# =====================================================

if not os.path.exists(FICHIER_CANDIDATS):
    st.error("Aucun candidat enregistré")
    st.stop()

if not os.path.exists(FICHIER_NOTES):
    st.error("Fichier notes introuvable")
    st.stop()

# =====================================================
# CHARGEMENT
# =====================================================

df_candidats = pd.read_excel(FICHIER_CANDIDATS)
df_notes = pd.read_excel(FICHIER_NOTES)

# =====================================================
# NETTOYAGE COLONNES
# =====================================================

colonnes_notes = [
    "Lecture", "Exp écrite", "Dictée", "Math",
    "EST", "ES", "EA/Dessin/Couture",
    "EA/Chant-Poésie", "EPS"
]

for col in colonnes_notes:
    df_notes[col] = pd.to_numeric(df_notes[col], errors="coerce").fillna(0.0)

df_notes["Nom complet"] = df_notes["Nom"] + " " + df_notes["Prénoms"]

liste = df_notes["Nom complet"].tolist()

if len(liste) == 0:
    st.error("Aucun candidat trouvé")
    st.stop()

# =====================================================
# CHOIX CANDIDAT
# =====================================================

st.markdown("### 🎓 Sélection du candidat")

candidat = st.selectbox("Choisir un candidat", liste)

resultat = df_notes[
    df_notes["Nom complet"].str.lower().str.strip()
    == candidat.lower().strip()
]

if resultat.empty:
    st.error("Candidat introuvable")
    st.stop()

ligne = resultat.index[0]

# =====================================================
# INFOS CANDIDAT (CARDS)
# =====================================================

col1, col2, col3 = st.columns(3)

col1.markdown(f"""
<div class="card">
<b>N° Table</b><br>
{df_notes.loc[ligne, 'N° Table']}
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="card">
<b>Sexe</b><br>
{df_notes.loc[ligne, 'Sexe']}
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="card">
<b>École</b><br>
{df_notes.loc[ligne, 'Ecole de provenance']}
</div>
""", unsafe_allow_html=True)

# =====================================================
# FORMULAIRE NOTES
# =====================================================

st.markdown("### ✍️ Saisie des notes")

with st.form("notes_form"):

    lecture = st.number_input("Lecture", 0.0, 20.0, float(df_notes.loc[ligne, "Lecture"]))
    exp_ecrite = st.number_input("Exp écrite", 0.0, 20.0, float(df_notes.loc[ligne, "Exp écrite"]))
    dictee = st.number_input("Dictée", 0.0, 20.0, float(df_notes.loc[ligne, "Dictée"]))
    math = st.number_input("Math", 0.0, 20.0, float(df_notes.loc[ligne, "Math"]))
    est = st.number_input("EST", 0.0, 20.0, float(df_notes.loc[ligne, "EST"]))
    es = st.number_input("ES", 0.0, 20.0, float(df_notes.loc[ligne, "ES"]))
    ea_dessin = st.number_input("EA/Dessin/Couture", 0.0, 20.0, float(df_notes.loc[ligne, "EA/Dessin/Couture"]))
    ea_chant = st.number_input("EA/Chant-Poésie", 0.0, 20.0, float(df_notes.loc[ligne, "EA/Chant-Poésie"]))
    eps = st.number_input("EPS", 0.0, 20.0, float(df_notes.loc[ligne, "EPS"]))

    submit = st.form_submit_button("💾 Enregistrer")

# =====================================================
# SAUVEGARDE
# =====================================================

if submit:

    df_notes.loc[ligne, colonnes_notes] = [
        lecture, exp_ecrite, dictee, math,
        est, es, ea_dessin, ea_chant, eps
    ]

    # TOTAL
    df_notes["Total"] = df_notes[colonnes_notes].sum(axis=1)

    # MOYENNE
    df_notes["Moyenne"] = (df_notes["Total"] / 9).round(2)

    # MOY 6/9
    df_notes["Moy 6/9"] = (df_notes["Total"] / 6).round(2)

    # OBS
    df_notes["OBS"] = df_notes["Moyenne"].apply(
        lambda x: "Admis" if x >= 10 else "Ajourné"
    )

    # RANG
    df_notes["Rang"] = df_notes["Total"].rank(ascending=False).astype(int)

    df_notes.to_excel(FICHIER_NOTES, index=False)

    st.success("✅ Notes enregistrées")
    st.rerun()

# =====================================================
# TABLEAU
# =====================================================

st.markdown("### 📋 Tableau des notes")

st.dataframe(df_notes, use_container_width=True, height=450)

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
    st.success("Notes supprimées")
    st.rerun()

# =====================================================
# RETOUR
# =====================================================

if st.button("🏠 Accueil"):
    st.switch_page("app.py")