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
# CONFIGURATION
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

if not st.session_state["authentication_status"]:
    st.error("Accès refusé")
    st.stop()

st.title("📄 Relevé individuel CEP")
st.success(f"Bienvenue {st.session_state['name']}")

# =====================================================
# FICHIER
# =====================================================

FICHIER_NOTES = "data/notes.xlsx"

if not os.path.exists(FICHIER_NOTES):
    st.error("Fichier notes introuvable")
    st.stop()

df = pd.read_excel(FICHIER_NOTES)

if df.empty:
    st.warning("Aucune donnée disponible")
    st.stop()

df = df.dropna(subset=["Nom", "Prénoms"])

# =====================================================
# NOM COMPLET
# =====================================================

df["Nom complet"] = (
    df["Nom"].astype(str).str.strip()
    + " "
    + df["Prénoms"].astype(str).str.strip()
)

candidat = st.selectbox("🎓 Choisir un candidat", df["Nom complet"].tolist())

ligne = df[df["Nom complet"] == candidat].iloc[0]

# =====================================================
# MENTION
# =====================================================

moyenne = float(ligne["Moyenne"])

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
# CARDS MODERNES
# =====================================================

c1, c2, c3, c4 = st.columns(4)

c1.metric("N° Table", ligne["N° Table"])
c2.metric("Rang", ligne["Rang"])
c3.metric("Moyenne /20", f"{moyenne:.2f}")
c4.metric("Mention", mention)

# =====================================================
# TABLE NOTES (AVEC /20)
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

notes_df = pd.DataFrame({
    "Matière": matieres,
    "Note /20": [float(ligne[m]) for m in matieres]
})

st.subheader("📋 Notes du candidat (/20)")

st.dataframe(notes_df, use_container_width=True, hide_index=True)

# =====================================================
# RESULTATS
# =====================================================

st.subheader("📊 Résultats")

st.metric("Total /180", ligne["Total"])
st.metric("Moyenne /20", ligne["Moyenne"])
st.metric("Observation", ligne["OBS"])
st.metric("Mention", mention)

# =====================================================
# PDF MODERNE
# =====================================================

if st.button("📄 Générer le relevé PDF", use_container_width=True):

    nom_pdf = f"releve_{ligne['N° Table']}.pdf"

    doc = SimpleDocTemplate(nom_pdf, pagesize=A4)

    styles = getSampleStyleSheet()
    elements = []

    # HEADER
    header = Paragraph("""
    <para align='center'>
    <font size=18><b>KODAV CEP PRO</b></font><br/>
    <font size=12>CENTRE D'EXAMEN CEP - RELEVÉ OFFICIEL</font><br/>
    <hr/>
    </para>
    """, styles["Title"])

    elements.append(header)
    elements.append(Spacer(1, 20))

    # INFOS
    infos = Paragraph(f"""
    <b>Nom :</b> {ligne['Nom']}<br/>
    <b>Prénoms :</b> {ligne['Prénoms']}<br/>
    <b>N° Table :</b> {ligne['N° Table']}<br/>
    <b>Sexe :</b> {ligne['Sexe']}<br/>
    <b>Ecole :</b> {ligne['Ecole de provenance']}<br/>
    """, styles["BodyText"])

    elements.append(infos)
    elements.append(Spacer(1, 15))

    # TABLE NOTES PDF
    data = [["Matière", "Note /20"]]
    for m in matieres:
        data.append([m, str(ligne[m])])

    table = Table(data, colWidths=[300, 120])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # RESULTATS
    result = Paragraph(f"""
    <b>Total :</b> {ligne['Total']}<br/>
    <b>Moyenne :</b> {ligne['Moyenne']}<br/>
    <b>Rang :</b> {ligne['Rang']}<br/>
    <b>Mention :</b> {mention}<br/>
    <b>Observation :</b> {ligne['OBS']}<br/>
    """, styles["BodyText"])

    elements.append(result)

    doc.build(elements)

    st.success("PDF généré avec succès")

    with open(nom_pdf, "rb") as f:
        st.download_button(
            "⬇️ Télécharger PDF",
            f,
            file_name=nom_pdf,
            mime="application/pdf"
        )

# =====================================================
# RETOUR
# =====================================================

if st.button("🏠 Retour"):
    st.switch_page("app.py")