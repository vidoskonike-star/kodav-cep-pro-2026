import streamlit as st
import pandas as pd
import os

# =====================================================
# CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="Saisie Rapide Mobile",
    page_icon="📱",
    layout="wide"
)

# =====================================================
# SECURITE
# =====================================================
if "authentication_status" not in st.session_state:
    st.error("Veuillez vous connecter")
    st.stop()

if st.session_state["authentication_status"] is not True:
    st.error("Accès refusé")
    st.stop()

# =====================================================
# CENTRE
# =====================================================
centre = st.session_state.get("centre", "CENTRE_PAR_DEFAUT")
base_path = os.path.join("data", centre)
os.makedirs(base_path, exist_ok=True)

FICHIER_NOTES = os.path.join(base_path, "notes.xlsx")

if not os.path.exists(FICHIER_NOTES):
    st.error("Fichier notes introuvable")
    st.stop()

# =====================================================
# CHARGEMENT
# =====================================================
df = pd.read_excel(FICHIER_NOTES)

if df.empty:
    st.warning("Aucun candidat trouvé.")
    st.stop()

df = df.sort_values("N° Table").reset_index(drop=True)

# =====================================================
# MATIERES
# =====================================================
colonnes_notes = [
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

# 🔧 Forcer les colonnes de notes en float
for col in colonnes_notes:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)

# =====================================================
# RECALCUL
# =====================================================
def recalculer_synthese(df):
    notes_calc = df[colonnes_notes].replace(-1, 0)
    df["Total"] = notes_calc.sum(axis=1)
    df["Moyenne"] = (df["Total"] / 9).round(2)
    df["Moy 6/9"] = (df["Total"] / 6).round(2)

    df["OBS"] = df.apply(
        lambda row:
        "ABSENT" if (row[colonnes_notes] == -1).any()
        else ("Admis" if row["Moyenne"] >= 10 else "Ajourné"),
        axis=1
    )

    df["Rang"] = (
        df["Total"]
        .rank(ascending=False, method="min")
        .astype(int)
    )
    return df

# =====================================================
# INDEX COURANT
# =====================================================
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

index = st.session_state.current_index
if index >= len(df):
    index = 0
    st.session_state.current_index = 0

total = len(df)

# =====================================================
# TITRE
# =====================================================
st.title("📱 Saisie Rapide Mobile")

# =====================================================
# CHOIX MATIERE
# =====================================================
matiere = st.selectbox("📚 Matière", colonnes_notes)

# =====================================================
# PROGRESSION
# =====================================================
st.progress((index + 1) / total)
st.caption(f"Candidat {index+1}/{total}")

# =====================================================
# CANDIDAT
# =====================================================
candidat = df.iloc[index]
nom_complet = f"{candidat['Nom']} {candidat['Prénoms']}"

st.markdown(
    f"""
    <div style="
        padding:15px;
        border-radius:10px;
        background:#222;
        color:white;
        text-align:center;
        margin-bottom:10px;
    ">
        <h2>{nom_complet}</h2>
        <h3>N° TABLE : {candidat['N° Table']}</h3>
        <p>{candidat['Sexe']} | {candidat['Ecole de provenance']}</p>
    </div>
    """,
    unsafe_allow_html=True
)

valeur_actuelle = candidat[matiere]
if valeur_actuelle == -1:
    st.warning("🚫 Absent")
elif pd.notna(valeur_actuelle):
    st.info(f"Note actuelle : {valeur_actuelle}")

# =====================================================
# SAUVEGARDE RAPIDE
# =====================================================
def sauvegarder(valeur):
    global df
    df.loc[index, matiere] = float(valeur)
    df = recalculer_synthese(df)
    df.to_excel(FICHIER_NOTES, index=False)

    # Navigation fluide
    if index < total - 1:
        st.session_state.current_index = index + 1
    else:
        st.session_state.current_index = 0  # Retour au début

    st.rerun()

# =====================================================
# SAISIE NOTE
# =====================================================
if "note_temp" not in st.session_state:
    st.session_state.note_temp = ""

note = st.text_input("📝 Note", key="note_temp", placeholder="Entrez une note (0 à 20)")

col1, col2 = st.columns(2)

with col1:
    if st.button("💾 ENREGISTRER", use_container_width=True):
        if note.strip() == "":
            st.warning("Saisissez une note")
        else:
            try:
                note_valeur = float(note.replace(",", "."))
                if 0 <= note_valeur <= 20:
                    sauvegarder(round(note_valeur, 2))
                else:
                    st.error("La note doit être comprise entre 0 et 20")
            except ValueError:
                st.error("Veuillez entrer un nombre valide (ex: 12,5)")

with col2:
    if st.button("🚫 ABSENT", use_container_width=True):
        sauvegarder(-1)

# =====================================================
# NAVIGATION
# =====================================================
col1, col2 = st.columns(2)
with col1:
    if st.button("⬅️ Précédent", disabled=index == 0, use_container_width=True):
        st.session_state.current_index -= 1
        st.rerun()
with col2:
    if st.button("➡️ Suivant", disabled=index == total - 1, use_container_width=True):
        st.session_state.current_index += 1
        st.rerun()

# =====================================================
# STATISTIQUES
# =====================================================
absents = (df[matiere] == -1).sum()
saisis = (df[matiere].notna() & (df[matiere] != -1)).sum()
restants = total - absents - saisis

st.markdown("---")
c1, c2, c3 = st.columns(3)
c1.metric("✅ Saisis", int(saisis))
c2.metric("🚫 Absents", int(absents))
c3.metric("⏳ Restants", int(restants))

# =====================================================
# TABLEAU RECAPITULATIF
# =====================================================
st.markdown("---")
st.subheader("📋 Tableau récapitulatif")

df_affichage = df.copy()
df_affichage[matiere] = df_affichage[matiere].replace(-1, "ABS")

edited_df = st.data_editor(
    df_affichage[["N° Table", "Nom", "Prénoms", matiere, "Total", "Moyenne", "OBS", "Rang"]],
    hide_index=True,
    use_container_width=True,
    disabled=["N° Table", "Nom", "Prénoms", "Total", "Moyenne", "OBS", "Rang"]
)

# =====================================================
# ENREGISTRER MODIFICATIONS
# =====================================================
if st.button("💾 Enregistrer les corrections", use_container_width=True):
    colonne = edited_df[matiere]
    for i in edited_df.index:
        valeur = colonne.iloc[i]
        if str(valeur).upper() == "ABS":
            valeur = -1
        elif pd.notna(valeur):
            try:
                valeur = float(str(valeur).replace(",", "."))
                if not (0 <= valeur <= 20):
                    continue
            except ValueError:
                continue
        df.loc[i, matiere] = valeur

    df = recalculer_synthese(df)
    df.to_excel(FICHIER_NOTES, index=False)
    st.success("✅ Corrections enregistrées")
    st.rerun()

# =====================================================
# RETOUR
# =====================================================
st.markdown("---")
if st.button("🏠 Accueil", use_container_width=True):
    st.switch_page("app.py")
