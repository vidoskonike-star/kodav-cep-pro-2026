import streamlit as st
import pandas as pd
import os

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.flowables import HRFlowable

# =====================================================
# CONFIGURATION PAGE
# =====================================================

st.set_page_config(
    page_title="Relevé CEP",
    page_icon="📄",
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

st.title("📄 Relevé individuel CEP")

st.success(
    f"Bienvenue {st.session_state['name']}"
)

# =====================================================
# FICHIER NOTES
# =====================================================

FICHIER_NOTES = "data/notes.xlsx"

# =====================================================
# VÉRIFICATION
# =====================================================

if not os.path.exists(FICHIER_NOTES):

    st.error(
        "Le fichier notes.xlsx est introuvable"
    )

    st.stop()

# =====================================================
# CHARGEMENT
# =====================================================

df = pd.read_excel(
    FICHIER_NOTES
)

# =====================================================
# VÉRIFICATION DONNÉES
# =====================================================

if df.empty:

    st.warning("⚠️ Aucun candidat disponible")
    st.stop()

# =====================================================
# SUPPRESSION LIGNES VIDES
# =====================================================

df = df.dropna(
    subset=["Nom", "Prénoms"],
    how="all"
)

# =====================================================
# NOM COMPLET
# =====================================================

df["Nom complet"] = (

    df["Nom"].astype(str).str.strip()
    + " "
    + df["Prénoms"].astype(str).str.strip()
)

# =====================================================
# LISTE CANDIDATS
# =====================================================

liste_candidats = df[
    "Nom complet"
].dropna().tolist()

# =====================================================
# AUCUN CANDIDAT
# =====================================================

if len(liste_candidats) == 0:

    st.warning(
        "⚠️ Aucun candidat trouvé dans le fichier notes.xlsx"
    )

    st.stop()

# =====================================================
# CHOIX CANDIDAT
# =====================================================

candidat = st.selectbox(
    "🎓 Choisir un candidat",
    liste_candidats
)

# =====================================================
# RECHERCHE SÉCURISÉE
# =====================================================

filtre = df[
    df["Nom complet"] == candidat
]

if filtre.empty:

    st.error(
        "❌ Candidat introuvable"
    )

    st.stop()

ligne = filtre.iloc[0]

# =====================================================
# MENTION AUTOMATIQUE
# =====================================================

moyenne = float(
    ligne["Moyenne"]
)

if moyenne >= 16:

    mention = "TRÈS BIEN"

elif moyenne >= 14:

    mention = "BIEN"

elif moyenne >= 12:

    mention = "ASSEZ BIEN"

elif moyenne >= 10:

    mention = "PASSABLE"

else:

    mention = "AJOURNÉ"

# =====================================================
# INFOS CANDIDAT
# =====================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.info(
        f"N° Table : {ligne['N° Table']}"
    )

with col2:

    st.info(
        f"Rang : {ligne['Rang']}"
    )

with col3:

    st.info(
        f"Mention : {mention}"
    )

# =====================================================
# TABLEAU NOTES
# =====================================================

notes_df = pd.DataFrame({

    "Matière": [

        "Lecture",
        "Exp écrite",
        "Dictée",
        "Math",
        "EST",
        "ES",
        "EA/Dessin/Couture",
        "EA/Chant-Poésie",
        "EPS"
    ],

    "Note": [

        ligne["Lecture"],
        ligne["Exp écrite"],
        ligne["Dictée"],
        ligne["Math"],
        ligne["EST"],
        ligne["ES"],
        ligne["EA/Dessin/Couture"],
        ligne["EA/Chant-Poésie"],
        ligne["EPS"]
    ]
})

# =====================================================
# AFFICHAGE NOTES
# =====================================================

st.subheader("📋 Notes du candidat")

st.dataframe(
    notes_df,
    use_container_width=True,
    hide_index=True
)

# =====================================================
# RÉSULTATS
# =====================================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Total",
        ligne["Total"]
    )

with col2:

    st.metric(
        "Moyenne",
        ligne["Moyenne"]
    )

with col3:

    st.metric(
        "Observation",
        ligne["OBS"]
    )

with col4:

    st.metric(
        "Mention",
        mention
    )

# =====================================================
# GÉNÉRATION PDF
# =====================================================

if st.button(
    "📄 Générer le relevé PDF",
    use_container_width=True
):

    nom_pdf = (
        f"releve_{ligne['N° Table']}.pdf"
    )

    doc = SimpleDocTemplate(

        nom_pdf,

        pagesize=A4,

        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    elements = []

    # =================================================
    # EN-TÊTE
    # =================================================

    titre = Paragraph(

        """
        <para align='center'>
        <font size=18 color='darkgreen'>
        <b>CENTRE D'EXAMEN BLANC CEP</b>
        </font>
        <br/><br/>
        <font size=16>
        <b>KODAV CEP PRO</b>
        </font>
        <br/><br/>
        <font size=14>
        <b>RELEVÉ DE NOTES CEP</b>
        </font>
        <br/><br/>
        SESSION 2026
        </para>
        """,

        styles['Title']
    )

    elements.append(titre)

    elements.append(
        Spacer(1, 20)
    )

    elements.append(
        HRFlowable(width="100%")
    )

    elements.append(
        Spacer(1, 15)
    )

    # =================================================
    # INFORMATIONS
    # =================================================

    infos = Paragraph(

        f"""
        <font size=12>

        <b>Nom :</b> {ligne['Nom']}<br/><br/>

        <b>Prénoms :</b> {ligne['Prénoms']}<br/><br/>

        <b>N° Table :</b> {ligne['N° Table']}<br/><br/>

        <b>Sexe :</b> {ligne['Sexe']}<br/><br/>

        <b>Ecole :</b> {ligne['Ecole de provenance']}

        </font>
        """,

        styles['BodyText']
    )

    elements.append(infos)

    elements.append(
        Spacer(1, 20)
    )

    # =================================================
    # TABLEAU NOTES PDF
    # =================================================

    data = [

        ["Matière", "Note"]
    ]

    for i, row in notes_df.iterrows():

        data.append([

            row["Matière"],
            str(row["Note"])
        ])

    table = Table(

        data,

        colWidths=[300, 120]
    )

    table.setStyle(TableStyle([

        (
            'BACKGROUND',
            (0, 0),
            (-1, 0),
            colors.darkgreen
        ),

        (
            'TEXTCOLOR',
            (0, 0),
            (-1, 0),
            colors.white
        ),

        (
            'FONTNAME',
            (0, 0),
            (-1, 0),
            'Helvetica-Bold'
        ),

        (
            'FONTSIZE',
            (0, 0),
            (-1, -1),
            11
        ),

        (
            'GRID',
            (0, 0),
            (-1, -1),
            1,
            colors.black
        ),

        (
            'ALIGN',
            (0, 0),
            (-1, -1),
            'CENTER'
        ),

        (
            'BOTTOMPADDING',
            (0, 0),
            (-1, 0),
            12
        )
    ]))

    elements.append(table)

    elements.append(
        Spacer(1, 25)
    )

    # =================================================
    # RÉSULTATS FINAUX
    # =================================================

    resultats = Paragraph(

        f"""
        <font size=13>

        <b>Total :</b> {ligne['Total']}<br/><br/>

        <b>Moyenne :</b> {ligne['Moyenne']}<br/><br/>

        <b>Rang :</b> {ligne['Rang']}<br/><br/>

        <b>Mention :</b> {mention}<br/><br/>

        <b>Observation :</b> {ligne['OBS']}

        </font>
        """,

        styles['BodyText']
    )

    elements.append(resultats)

    elements.append(
        Spacer(1, 40)
    )

    # =================================================
    # SIGNATURE
    # =================================================

    signature = Paragraph(

        """
        <para align='right'>

        <font size=12>

        Le Chef Centre<br/><br/><br/>

        _______________________

        </font>

        </para>
        """,

        styles['BodyText']
    )

    elements.append(signature)

    # =================================================
    # CRÉATION PDF
    # =================================================

    doc.build(elements)

    st.success(
        "✅ Relevé PDF généré avec succès"
    )

    # =================================================
    # TÉLÉCHARGEMENT
    # =================================================

    with open(nom_pdf, "rb") as pdf:

        st.download_button(

            label="⬇️ Télécharger le relevé PDF",

            data=pdf,

            file_name=nom_pdf,

            mime="application/pdf",

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