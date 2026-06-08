import streamlit as st
import pandas as pd
import os

# =====================================================
# CONFIGURATION
# =====================================================
st.set_page_config(page_title="Saisie Rapide Mobile", page_icon="📱", layout="centered")

# =====================================================
# SÉCURITÉ
# =====================================================
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.error("Veuillez vous connecter")
    st.stop()

# =====================================================
# CENTRE UTILISATEUR
# =====================================================
centre = st.session_state.get("centre", "CENTRE_PAR_DEFAUT")
base_path = os.path.join("data", centre)
os.makedirs(base_path, exist_ok=True)

FICHIER_NOTES = os.path.join(base_path, "notes.xlsx")

if not os.path.exists(FICHIER_NOTES):
    st.error("Fichier notes introuvable")
    st.stop()

# Lecture avec moteur openpyxl
df = pd.read_excel(FICHIER_NOTES, engine="openpyxl")
if df.empty:
    st.warning("Aucun candidat trouvé.")
    st.stop()

df = df.sort_values("N° Table").reset_index(drop=True)

# =====================================================
# FONCTION DE RECALCUL SYNTHÈSES
# =====================================================
def recalculer_synthese(df):
    colonnes_notes = [
        "Lecture","Exp écrite","Dictée","Math",
        "EST","ES","EA/Dessin/Couture","EA/Chant-Poésie","EPS"
    ]
    df["Total"] = df[colonnes_notes].replace(-1, 0).sum(axis=1)
    df["Moyenne"] = (df["Total"] / 9).round(2)
    df["Moy 6/9"] = (df["Total"] / 6).round(2)
    df["OBS"] = df.apply(
        lambda row: "ABSENT" if (row[colonnes_notes] == -1).any()
        else ("Admis" if row["Moyenne"] >= 10 else "Ajourné"),
        axis=1
    )
    df["Rang"] = df["Total"].rank(ascending=False, method="min").astype(int)
    return df

# =====================================================
# INDEX COURANT
# =====================================================
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

index = st.session_state.current_index
total = len(df)

if index >= total:
    st.session_state.current_index = 0
    index = 0

# =====================================================
# TITRE
# =====================================================
st.title("📱 Saisie Rapide Mobile")

# =====================================================
# CHOIX MATIÈRE
# =====================================================
matiere = st.selectbox("📚 Matière", [
    "Lecture","Exp écrite","Dictée","Math","EST","ES",
    "EA/Dessin/Couture","EA/Chant-Poésie","EPS"
])

# =====================================================
# PROGRESSION
# =====================================================
st.progress((index + 1) / total)
st.caption(f"Candidat {index + 1}/{total}")

# =====================================================
# CANDIDAT
# =====================================================
candidat = df.iloc[index]
nom_complet = f"{candidat['Nom']} {candidat['Prénoms']}"

st.markdown(f"""
<div style="padding:15px;border-radius:10px;background:#222;color:#fff;text-align:center;margin-bottom:10px;">
    <h2>{nom_complet}</h2>
    <h3>N° TABLE : {candidat['N° Table']}</h3>
    <p>{candidat['Sexe']} | {candidat['Ecole de provenance']}</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# SAISIE RAPIDE (CASE VIDE PAR DÉFAUT)
# =====================================================
note = st.text_input("Note", value="", placeholder="Entrez la note (0-20)")

col1, col2 = st.columns(2)

with col1:
    if st.button("💾 ENREGISTRER", use_container_width=True):
        try:
            if note.strip() == "":
                st.error("Veuillez saisir une note")
            else:
                note_num = float(note)
                if 0 <= note_num <= 20:
                    df.loc[index, matiere] = note_num
                    df = recalculer_synthese(df)
                    df.to_excel(FICHIER_NOTES, index=False, engine="openpyxl")
                    st.session_state.current_index = min(index+1, total-1)
                    st.rerun()
                else:
                    st.error("La note doit être comprise entre 0 et 20")
        except:
            st.error("Entrez une note valide")

with col2:
    if st.button("🚫 ABSENT", use_container_width=True):
        df.loc[index, matiere] = -1
        df = recalculer_synthese(df)
        df.to_excel(FICHIER_NOTES, index=False, engine="openpyxl")
        st.session_state.current_index = min(index+1, total-1)
        st.rerun()

# =====================================================
# NAVIGATION
# =====================================================
col1, col2 = st.columns(2)
if col1.button("⬅️ Précédent", disabled=index == 0, use_container_width=True):
    st.session_state.current_index -= 1
    st.rerun()
if col2.button("➡️ Suivant", disabled=index == total-1, use_container_width=True):
    st.session_state.current_index += 1
    st.rerun()

# =====================================================
# STATISTIQUES
# =====================================================
absents = (df[matiere] == -1).sum()
saisis = (df[matiere].notna() & (df[matiere] != -1)).sum()
restants = total - absents - saisis

c1, c2, c3 = st.columns(3)
c1.metric("✅ Saisis", int(saisis))
c2.metric("🚫 Absents", int(absents))
c3.metric("⏳ Restants", int(restants))

# =====================================================
# TABLEAU RÉCAPITULATIF INTERACTIF
# =====================================================
st.markdown("---")
st.markdown("### 📋 Tableau récapitulatif")

df_affichage = df.copy()
df_affichage[matiere] = df_affichage[matiere].replace(-1, "ABS")

edited_df = st.data_editor(
    df_affichage[["N° Table","Nom","Prénoms",matiere,"Total","Moyenne","OBS","Rang"]],
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic"
)

# Bouton pour enregistrer les modifications du tableau
if st.button("💾 Enregistrer les modifications", use_container_width=True):
    edited_df[matiere] = edited_df[matiere].replace("ABS", -1)
    df.update(edited_df)
    df = recalculer_synthese(df)
    df.to_excel(FICHIER_NOTES, index=False, engine="openpyxl")
    st.success("✅ Notes enregistrées automatiquement dans notes.xlsx")
    st.rerun()

# =====================================================
# RETOUR
# =====================================================
if st.button("🏠 Accueil", use_container_width=True):
    st.switch_page("app.py")
