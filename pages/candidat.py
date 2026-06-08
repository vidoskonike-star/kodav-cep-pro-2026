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
# STYLE
# =====================================================
st.markdown("""
<style>
h1, h2, h3 { color: white; }
.block-title { font-size: 28px; font-weight: 800; color: white; margin-top: 20px; margin-bottom: 10px; }
.card { background: rgba(255,255,255,0.08); padding: 18px; border-radius: 18px; backdrop-filter: blur(10px); box-shadow: 0px 0px 15px rgba(0,0,0,0.2); color: white; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# TITRE
# =====================================================
st.title("🎓 Gestion des candidats CEP")
st.success(f"Bienvenue {st.session_state['name']}")

# =====================================================
# CENTRE UTILISATEUR
# =====================================================
centre = st.session_state.get("centre", "CENTRE_PAR_DEFAUT")
base_path = os.path.join("data", centre)
os.makedirs(base_path, exist_ok=True)

FICHIER_CANDIDATS = os.path.join(base_path, "candidats.xlsx")
FICHIER_NOTES = os.path.join(base_path, "notes.xlsx")

# =====================================================
# INIT FICHIERS VIDES
# =====================================================
if not os.path.exists(FICHIER_CANDIDATS):
    pd.DataFrame(columns=["N° Table","Nom","Prénoms","Sexe","Ecole de provenance"]).to_excel(FICHIER_CANDIDATS, index=False)

if not os.path.exists(FICHIER_NOTES):
    colonnes_notes = [
        "N° Table","Nom","Prénoms","Sexe","Ecole de provenance",
        "Lecture","Exp écrite","Dictée","Math","EST","ES",
        "EA/Dessin/Couture","EA/Chant-Poésie","EPS",
        "Total","Moy 6/9","Moyenne","Rang","OBS"
    ]
    pd.DataFrame(columns=colonnes_notes).to_excel(FICHIER_NOTES, index=False)

# =====================================================
# CHARGEMENT
# =====================================================
df = pd.read_excel(FICHIER_CANDIDATS)
df["N° Table"] = pd.to_numeric(df["N° Table"], errors="coerce")

# =====================================================
# FORMULAIRE AJOUT
# =====================================================
st.markdown("### ➕ Ajouter un candidat")
with st.form("formulaire_candidat"):
    col1, col2 = st.columns(2)
    with col1:
        numero_table = st.text_input("N° Table")
        nom = st.text_input("Nom")
    with col2:
        prenoms = st.text_input("Prénoms")
        sexe = st.selectbox("Sexe", ["Masculin","Féminin"])
    ecole = st.text_input("École de provenance")
    enregistrer = st.form_submit_button("💾 Enregistrer")

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
            df = pd.concat([df, nouveau], ignore_index=True).sort_values(by="N° Table")
            df.to_excel(FICHIER_CANDIDATS, index=False)

            # Ajout dans notes
            df_notes = pd.read_excel(FICHIER_NOTES)
            nouvelle_note = pd.DataFrame([{
                "N° Table": numero_table,
                "Nom": nom.upper(),
                "Prénoms": prenoms.title(),
                "Sexe": sexe,
                "Ecole de provenance": ecole.upper(),
                "Lecture": 0.0,"Exp écrite": 0.0,"Dictée": 0.0,"Math": 0.0,
                "EST": 0.0,"ES": 0.0,"EA/Dessin/Couture": 0.0,"EA/Chant-Poésie": 0.0,
                "EPS": 0.0,"Total": 0.0,"Moy 6/9": 0.0,"Moyenne": 0.0,"Rang": "","OBS": ""
            }])
            df_notes = pd.concat([df_notes, nouvelle_note], ignore_index=True)
            df_notes.to_excel(FICHIER_NOTES, index=False)

            st.success("✅ Candidat enregistré avec succès")
            st.rerun()

# =====================================================
# IMPORT EXCEL
# =====================================================
st.markdown("### 📥 Importer une liste de candidats")
fichier_import = st.file_uploader("Importer fichier Excel", type=["xlsx"])

if fichier_import is not None:
    df_import = pd.read_excel(fichier_import)
    colonnes_attendues = ["N° Table","Nom","Prénoms","Sexe","Ecole de provenance"]

    if not all(col in df_import.columns for col in colonnes_attendues):
        st.error("❌ Colonnes manquantes dans le fichier importé")
    else:
        st.dataframe(df_import.head(), use_container_width=True)
        if st.button("📥 Importer dans le centre"):
            df_import["N° Table"] = pd.to_numeric(df_import["N° Table"], errors="coerce")
            df_import = df_import.dropna(subset=["N° Table"]).sort_values(by="N° Table")
            df_import.to_excel(FICHIER_CANDIDATS, index=False)

            df_notes = df_import.copy()
            for col in ["Lecture","Exp écrite","Dictée","Math","EST","ES",
                        "EA/Dessin/Couture","EA/Chant-Poésie","EPS",
                        "Total","Moy 6/9","Moyenne"]:
                df_notes[col] = 0.0
            df_notes["Rang"] = ""
            df_notes["OBS"] = ""
            df_notes.to_excel(FICHIER_NOTES, index=False)

            st.success("✅ Importation réussie")
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
    st.download_button("⬇️ Télécharger Excel", f, file_name=f"candidats_{centre}.xlsx")

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
        os.remove(FICHIER_NOTES)
        st.rerun()

# =====================================================
# RETOUR
# =====================================================
if st.button("🏠 Accueil"):
    st.switch_page("app.py")
