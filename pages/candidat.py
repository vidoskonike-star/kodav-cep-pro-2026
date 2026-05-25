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
# TITRE
# =====================================================

st.title("🎓 Gestion des candidats CEP")

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
# CRÉATION FICHIER CANDIDATS
# =====================================================

if not os.path.exists(FICHIER_CANDIDATS):

    df_init = pd.DataFrame(columns=[

        "N° Table",
        "Nom",
        "Prénoms",
        "Sexe",
        "Ecole de provenance"
    ])

    df_init.to_excel(
        FICHIER_CANDIDATS,
        index=False
    )

# =====================================================
# CHARGEMENT
# =====================================================

df = pd.read_excel(FICHIER_CANDIDATS)

# =====================================================
# CONVERSION N° TABLE
# =====================================================

df["N° Table"] = pd.to_numeric(
    df["N° Table"],
    errors="coerce"
)

# =====================================================
# FORMULAIRE
# =====================================================

st.subheader("➕ Ajouter un candidat")

with st.form("formulaire_candidat"):

    numero_table = st.text_input("N° Table")

    nom = st.text_input("Nom")

    prenoms = st.text_input("Prénoms")

    sexe = st.selectbox(

        "Sexe",

        [
            "Masculin",
            "Féminin"
        ]
    )

    ecole = st.text_input(
        "Ecole de provenance"
    )

    enregistrer = st.form_submit_button(
        "💾 Enregistrer le candidat"
    )

# =====================================================
# ENREGISTREMENT
# =====================================================

if enregistrer:

    if (

        numero_table == ""
        or nom == ""
        or prenoms == ""
        or ecole == ""

    ):

        st.warning(
            "Veuillez remplir tous les champs"
        )

    else:

        numero_table = pd.to_numeric(
            numero_table,
            errors="coerce"
        )

        if pd.isna(numero_table):

            st.error(
                "❌ Numéro de table invalide"
            )

        else:

            existe = (

                df["N° Table"]
                == numero_table

            ).any()

            if existe:

                st.error(
                    "❌ Ce numéro de table existe déjà"
                )

            else:

                nouveau = pd.DataFrame([{

                    "N° Table": numero_table,
                    "Nom": nom.upper(),
                    "Prénoms": prenoms.title(),
                    "Sexe": sexe,
                    "Ecole de provenance": ecole.upper()
                }])

                df = pd.concat(
                    [df, nouveau],
                    ignore_index=True
                )

                # =====================================
                # TRI
                # =====================================

                df = df.sort_values(
                    by="N° Table"
                )

                # =====================================
                # SAUVEGARDE CANDIDATS
                # =====================================

                df.to_excel(
                    FICHIER_CANDIDATS,
                    index=False
                )

                # =====================================
                # MISE À JOUR NOTES
                # =====================================

                if os.path.exists(FICHIER_NOTES):

                    df_notes = pd.read_excel(
                        FICHIER_NOTES
                    )

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

                df_notes = pd.concat(

                    [
                        df_notes,
                        nouvelle_note
                    ],

                    ignore_index=True
                )

                df_notes["N° Table"] = pd.to_numeric(
                    df_notes["N° Table"],
                    errors="coerce"
                )

                df_notes = df_notes.sort_values(
                    by="N° Table"
                )

                df_notes.to_excel(
                    FICHIER_NOTES,
                    index=False
                )

                st.success(
                    "✅ Candidat enregistré avec succès"
                )

                st.rerun()

# =====================================================
# IMPORTATION EXCEL
# =====================================================

st.subheader("📥 Importer une liste Excel")

fichier_import = st.file_uploader(

    "Choisir un fichier Excel",

    type=["xlsx"]
)

if fichier_import is not None:

    try:

        df_import = pd.read_excel(
            fichier_import
        )

        st.dataframe(
            df_import.head(),
            use_container_width=True
        )

        if st.button(
            "📥 Importer les candidats",
            use_container_width=True
        ):

            df_import["N° Table"] = pd.to_numeric(
                df_import["N° Table"],
                errors="coerce"
            )

            df_import = df_import.sort_values(
                by="N° Table"
            )

            # =========================================
            # SAUVEGARDE CANDIDATS
            # =========================================

            df_import.to_excel(
                FICHIER_CANDIDATS,
                index=False
            )

            # =========================================
            # CRÉATION NOTES
            # =========================================

            df_notes = df_import.copy()

            colonnes_notes = [

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
                "Moyenne"
            ]

            for col in colonnes_notes:

                df_notes[col] = 0.0

            df_notes["Rang"] = ""
            df_notes["OBS"] = ""

            df_notes.to_excel(
                FICHIER_NOTES,
                index=False
            )

            st.success(
                "✅ Liste importée avec succès"
            )

            st.rerun()

    except Exception as e:

        st.error(e)

# =====================================================
# AFFICHAGE
# =====================================================

st.subheader("📋 Liste des candidats")

df = df.sort_values(
    by="N° Table"
)

st.dataframe(
    df,
    use_container_width=True,
    height=500
)

# =====================================================
# STATISTIQUES
# =====================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "👨 Total Garçons",
        len(df[df["Sexe"] == "Masculin"])
    )

with col2:

    st.metric(
        "👧 Total Filles",
        len(df[df["Sexe"] == "Féminin"])
    )

with col3:

    st.metric(
        "🎓 Total Candidats",
        len(df)
    )

# =====================================================
# TÉLÉCHARGEMENT
# =====================================================

with open(FICHIER_CANDIDATS, "rb") as fichier:

    st.download_button(

        label="⬇️ Télécharger la liste Excel",

        data=fichier,

        file_name="candidats.xlsx",

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