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
# TITRE
# =====================================================

st.title("⚡ Saisie Rapide des Notes CEP")

st.success(
    f"Bienvenue {st.session_state['name']}"
)

# =====================================================
# DOSSIER DATA
# =====================================================

os.makedirs("data", exist_ok=True)

# =====================================================
# FICHIERS
# =====================================================

FICHIER_CANDIDATS = "data/candidats.xlsx"
FICHIER_NOTES = "data/notes.xlsx"

# =====================================================
# VÉRIFICATION FICHIERS
# =====================================================

if not os.path.exists(FICHIER_CANDIDATS):

    st.error("Aucun candidat enregistré")
    st.stop()

# =====================================================
# CRÉATION AUTOMATIQUE NOTES.XLSX
# =====================================================

if not os.path.exists(FICHIER_NOTES):

    colonnes = [

        "N° Table",
        "Nom",
        "Prénoms",
        "Sexe",
        "Ecole de provenance",

        "Lecture",
        "Exp écrite",
        "Dictée",
        "Math",
        "EST",
        "ES",
        "EA/Dessin/Couture",
        "EA/Chant-Poésie",
        "EPS",

        "Total",
        "Moy 6/9",
        "Moyenne",
        "Rang",
        "OBS"
    ]

    pd.DataFrame(columns=colonnes).to_excel(
        FICHIER_NOTES,
        index=False
    )

# =====================================================
# CHARGEMENT EXCEL
# =====================================================

df_candidats = pd.read_excel(
    FICHIER_CANDIDATS
)

df_notes = pd.read_excel(
    FICHIER_NOTES
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
# CHOIX MATIÈRE
# =====================================================

matiere = st.selectbox(
    "📘 Choisir une matière",
    matieres
)

# =====================================================
# TITRE MATIÈRE
# =====================================================

st.subheader(
    f"✍️ Saisie rapide : {matiere}"
)

# =====================================================
# AJOUT AUTOMATIQUE CANDIDATS
# =====================================================

for i, row in df_candidats.iterrows():

    numero_table = row["N° Table"]

    nom = str(row["Nom"]).strip()
    prenoms = str(row["Prénoms"]).strip()

    existe = (

        (df_notes["N° Table"].astype(str) == str(numero_table))
    ).any()

    if not existe:

        nouvelle_ligne = {

            "N° Table": numero_table,
            "Nom": nom,
            "Prénoms": prenoms,
            "Sexe": row["Sexe"],
            "Ecole de provenance": row["Ecole de provenance"],

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
        }

        df_notes = pd.concat(
            [
                df_notes,
                pd.DataFrame([nouvelle_ligne])
            ],
            ignore_index=True
        )

# =====================================================
# CONVERSION NUMÉRO TABLE
# =====================================================

df_notes["N° Table"] = pd.to_numeric(
    df_notes["N° Table"],
    errors="coerce"
)

# =====================================================
# TRI PAR NUMÉRO TABLE
# =====================================================

df_notes = df_notes.sort_values(
    by="N° Table"
)
# =====================================================
# CONVERSION NUMÉRIQUE
# =====================================================

for col in matieres:

    df_notes[col] = pd.to_numeric(
        df_notes[col],
        errors="coerce"
    ).fillna(0.0)

# =====================================================
# NOM COMPLET
# =====================================================

df_notes["Nom complet"] = (

    df_notes["Nom"].astype(str)
    + " "
    + df_notes["Prénoms"].astype(str)
)

# =====================================================
# TABLEAU DE SAISIE
# =====================================================

st.info(
    "Utilisez TAB, ENTER ou les flèches du clavier pour vous déplacer rapidement."
)

df_saisie = df_notes[
    ["N° Table", "Nom complet", matiere]
].copy()

# =====================================================
# ÉDITEUR STYLE EXCEL
# =====================================================

edited_df = st.data_editor(

    df_saisie,

    use_container_width=True,

    hide_index=True,

    num_rows="fixed",

    key="table_saisie",

    column_config={

        "N° Table": st.column_config.NumberColumn(
            "N° Table",
            disabled=True
        ),

        "Nom complet": st.column_config.TextColumn(
            "Nom du candidat",
            disabled=True
        ),

        matiere: st.column_config.NumberColumn(
            matiere,
            min_value=0.0,
            max_value=20.0,
            step=0.5,
            format="%.1f",
            required=True
        )
    }
)

# =====================================================
# BOUTON ENREGISTREMENT
# =====================================================

if st.button(
    "💾 Enregistrer les notes",
    use_container_width=True
):

    # =================================================
    # MISE À JOUR MATIÈRE
    # =================================================

    df_notes[matiere] = edited_df[matiere]

    # =================================================
    # TOTAL
    # =================================================

    df_notes["Total"] = (

        df_notes["Lecture"]
        + df_notes["Exp écrite"]
        + df_notes["Dictée"]
        + df_notes["Math"]
        + df_notes["EST"]
        + df_notes["ES"]
        + df_notes["EA/Dessin/Couture"]
        + df_notes["EA/Chant-Poésie"]
        + df_notes["EPS"]

    )

    # =================================================
    # MOYENNE
    # =================================================

    df_notes["Moyenne"] = round(
        df_notes["Total"] / 9,
        2
    )

    # =================================================
    # MOY 6/9
    # =================================================

    df_notes["Moy 6/9"] = round(
        df_notes["Total"] / 6,
        2
    )

    # =================================================
    # OBSERVATION
    # =================================================

    df_notes["OBS"] = df_notes[
        "Moyenne"
    ].apply(

        lambda x:
        "Admis"
        if x >= 10
        else "Ajourné"
    )

    # =================================================
    # PAS DE RANG AUTOMATIQUE
    # =================================================

    df_notes["Rang"] = ""

    # =================================================
    # SUPPRESSION COLONNE TEMPORAIRE
    # =================================================

    if "Nom complet" in df_notes.columns:

        df_notes = df_notes.drop(
            columns=["Nom complet"]
        )

    # =================================================
    # SAUVEGARDE
    # =================================================

    df_notes.to_excel(
        FICHIER_NOTES,
        index=False
    )

    st.success(
        "✅ Notes enregistrées avec succès"
    )

    st.rerun()

# =====================================================
# APERÇU GÉNÉRAL
# =====================================================

st.subheader("📋 Résultats complets")

st.dataframe(
    df_notes,
    use_container_width=True,
    height=500
)

# =====================================================
# IMPORTATION FICHIER EXCEL
# =====================================================

st.subheader("📥 Importer un fichier Excel de notes")

fichier_importe = st.file_uploader(
    "Choisir un fichier Excel",
    type=["xlsx"]
)

if fichier_importe is not None:

    try:

        df_import = pd.read_excel(
            fichier_importe
        )

        st.success(
            "✅ Fichier chargé avec succès"
        )

        st.dataframe(
            df_import.head(),
            use_container_width=True
        )

        if st.button(
            "📥 Importer les notes",
            use_container_width=True
        ):

            df_import.to_excel(
                FICHIER_NOTES,
                index=False
            )

            st.success(
                "✅ Fichier importé avec succès"
            )

            st.rerun()

    except Exception as e:

        st.error(
            f"Erreur : {e}"
        )

# =====================================================
# TÉLÉCHARGEMENT
# =====================================================

with open(FICHIER_NOTES, "rb") as fichier:

    st.download_button(
        label="⬇️ Télécharger notes.xlsx",
        data=fichier,
        file_name="notes.xlsx",
        mime="application/vnd.ms-excel"
    )

# =====================================================
# RETOUR
# =====================================================

if st.button("🏠 Retour à l'accueil"):

    st.switch_page("app.py")