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
# TITRE
# =====================================================

st.title("📝 Saisie des notes CEP")

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
# VÉRIFICATION
# =====================================================

if not os.path.exists(FICHIER_CANDIDATS):

    st.error(
        "Aucun candidat enregistré"
    )

    st.stop()

if not os.path.exists(FICHIER_NOTES):

    st.error(
        "Le fichier notes.xlsx est introuvable"
    )

    st.stop()

# =====================================================
# CHARGEMENT
# =====================================================

df_candidats = pd.read_excel(
    FICHIER_CANDIDATS
)

df_notes = pd.read_excel(
    FICHIER_NOTES
)

# =====================================================
# CORRECTION DES COLONNES MANQUANTES
# =====================================================

colonnes_obligatoires = [

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

for col in colonnes_obligatoires:

    if col not in df_notes.columns:

        if col in [

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

        ]:

            df_notes[col] = 0.0

        else:

            df_notes[col] = ""

# =====================================================
# CONVERSION NUMÉRIQUE
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

for col in colonnes_notes:

    df_notes[col] = pd.to_numeric(
        df_notes[col],
        errors="coerce"
    ).fillna(0.0)

# =====================================================
# TRI PAR NUMÉRO TABLE
# =====================================================

df_notes = df_notes.sort_values(
    by="N° Table"
)

# =====================================================
# NOM COMPLET
# =====================================================

df_notes["Nom complet"] = (

    df_notes["Nom"].astype(str)
    + " "
    + df_notes["Prénoms"].astype(str)
)

# =====================================================
# LISTE CANDIDATS
# =====================================================

liste_candidats = df_notes[
    "Nom complet"
].tolist()

# =====================================================
# VÉRIFICATION LISTE VIDE
# =====================================================

if len(liste_candidats) == 0:

    st.error(
        "❌ Aucun candidat trouvé dans le fichier notes.xlsx"
    )

    st.stop()

# =====================================================
# CHOIX CANDIDAT
# =====================================================

st.subheader("🎓 Choisir un candidat")

candidat = st.selectbox(
    "Sélectionner un candidat",
    liste_candidats
)

# =====================================================
# RECHERCHE SÉCURISÉE
# =====================================================

resultat = df_notes[

    df_notes["Nom complet"]
    .astype(str)
    .str.strip()
    .str.lower()

    ==

    candidat
    .strip()
    .lower()
]

if not resultat.empty:

    ligne = resultat.index[0]

else:

    st.error(
        "❌ Candidat introuvable dans le fichier des notes"
    )

    st.stop()

# =====================================================
# INFOS CANDIDAT
# =====================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.info(
        f"N° Table : {df_notes.loc[ligne, 'N° Table']}"
    )

with col2:

    st.info(
        f"Sexe : {df_notes.loc[ligne, 'Sexe']}"
    )

with col3:

    st.info(
        f"Ecole : {df_notes.loc[ligne, 'Ecole de provenance']}"
    )

# =====================================================
# FORMULAIRE NOTES
# =====================================================

st.subheader("✍️ Saisie des notes")

with st.form("form_notes"):

    lecture = st.number_input(

        "Lecture",

        min_value=0.0,
        max_value=20.0,
        step=0.5,

        value=float(
            df_notes.loc[ligne, "Lecture"]
        )
    )

    exp_ecrite = st.number_input(

        "Exp écrite",

        min_value=0.0,
        max_value=20.0,
        step=0.5,

        value=float(
            df_notes.loc[ligne, "Exp écrite"]
        )
    )

    dictee = st.number_input(

        "Dictée",

        min_value=0.0,
        max_value=20.0,
        step=0.5,

        value=float(
            df_notes.loc[ligne, "Dictée"]
        )
    )

    math = st.number_input(

        "Math",

        min_value=0.0,
        max_value=20.0,
        step=0.5,

        value=float(
            df_notes.loc[ligne, "Math"]
        )
    )

    est = st.number_input(

        "EST",

        min_value=0.0,
        max_value=20.0,
        step=0.5,

        value=float(
            df_notes.loc[ligne, "EST"]
        )
    )

    es = st.number_input(

        "ES",

        min_value=0.0,
        max_value=20.0,
        step=0.5,

        value=float(
            df_notes.loc[ligne, "ES"]
        )
    )

    ea_dessin = st.number_input(

        "EA/Dessin/Couture",

        min_value=0.0,
        max_value=20.0,
        step=0.5,

        value=float(
            df_notes.loc[
                ligne,
                "EA/Dessin/Couture"
            ]
        )
    )

    ea_chant = st.number_input(

        "EA/Chant-Poésie",

        min_value=0.0,
        max_value=20.0,
        step=0.5,

        value=float(
            df_notes.loc[
                ligne,
                "EA/Chant-Poésie"
            ]
        )
    )

    eps = st.number_input(

        "EPS",

        min_value=0.0,
        max_value=20.0,
        step=0.5,

        value=float(
            df_notes.loc[ligne, "EPS"]
        )
    )

    enregistrer = st.form_submit_button(
        "💾 Enregistrer les notes"
    )

# =====================================================
# ENREGISTREMENT
# =====================================================

if enregistrer:

    df_notes.loc[ligne, "Lecture"] = lecture

    df_notes.loc[ligne, "Exp écrite"] = exp_ecrite

    df_notes.loc[ligne, "Dictée"] = dictee

    df_notes.loc[ligne, "Math"] = math

    df_notes.loc[ligne, "EST"] = est

    df_notes.loc[ligne, "ES"] = es

    df_notes.loc[
        ligne,
        "EA/Dessin/Couture"
    ] = ea_dessin

    df_notes.loc[
        ligne,
        "EA/Chant-Poésie"
    ] = ea_chant

    df_notes.loc[ligne, "EPS"] = eps

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
    # OBS
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
    # RANG
    # =================================================

    df_notes["Rang"] = df_notes[
        "Total"
    ].rank(
        ascending=False,
        method="min"
    ).astype(int)

    # =================================================
    # TRI
    # =================================================

    df_notes = df_notes.sort_values(
        by="N° Table"
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
# IMPORTATION EXCEL
# =====================================================

st.subheader("📥 Importation Excel des notes")

fichier_importe = st.file_uploader(

    "Choisir le fichier Excel des notes",

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

            for i, row in df_import.iterrows():

                numero_table = row["N° Table"]

                for matiere in colonnes_notes:

                    if matiere in df_import.columns:

                        valeur = row[matiere]

                        df_notes.loc[
                            df_notes["N° Table"]
                            == numero_table,

                            matiere
                        ] = valeur

            # =========================================
            # TOTAL
            # =========================================

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

            # =========================================
            # MOYENNE
            # =========================================

            df_notes["Moyenne"] = round(
                df_notes["Total"] / 9,
                2
            )

            # =========================================
            # MOY 6/9
            # =========================================

            df_notes["Moy 6/9"] = round(
                df_notes["Total"] / 6,
                2
            )

            # =========================================
            # OBS
            # =========================================

            df_notes["OBS"] = df_notes[
                "Moyenne"
            ].apply(

                lambda x:
                "Admis"
                if x >= 10
                else "Ajourné"
            )

            # =========================================
            # RANG
            # =========================================

            df_notes["Rang"] = df_notes[
                "Total"
            ].rank(
                ascending=False,
                method="min"
            ).astype(int)

            # =========================================
            # TRI
            # =========================================

            df_notes = df_notes.sort_values(
                by="N° Table"
            )

            # =========================================
            # SAUVEGARDE
            # =========================================

            df_notes.to_excel(
                FICHIER_NOTES,
                index=False
            )

            st.success(
                "✅ Notes importées avec succès"
            )

            st.rerun()

    except Exception as e:

        st.error(e)

# =====================================================
# APERÇU
# =====================================================

st.subheader("📋 Tableau général des notes")

st.dataframe(
    df_notes,
    use_container_width=True,
    height=500
)

# =====================================================
# TÉLÉCHARGEMENT
# =====================================================

with open(FICHIER_NOTES, "rb") as fichier:

    st.download_button(

        label="⬇️ Télécharger le fichier Excel",

        data=fichier,

        file_name="notes.xlsx",

        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

        use_container_width=True
    )

# =====================================================
# RÉINITIALISATION DES NOTES
# =====================================================

st.markdown("---")

st.subheader("🗑️ Réinitialisation des notes")

st.warning(
    "Cette action supprimera toutes les notes enregistrées."
)

if st.button(
    "❌ Réinitialiser toutes les notes",
    use_container_width=True
):

    colonnes_notes = [

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

    df_vide = pd.DataFrame(
        columns=colonnes_notes
    )

    df_vide.to_excel(
        FICHIER_NOTES,
        index=False
    )

    st.success(
        "✅ Toutes les notes ont été supprimées avec succès"
    )

    st.rerun()
    
# =====================================================
# RETOUR
# =====================================================

if st.button(
    "🏠 Retour à l'accueil",
    use_container_width=True
):

    st.switch_page("app.py")