import streamlit as st
import pandas as pd
import os

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
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

if st.session_state["authentication_status"] is not True:
    st.error("Accès refusé")
    st.stop()

# =====================================================
# CENTRE UTILISATEUR
# =====================================================
centre = st.session_state.get("centre", "CENTRE_PAR_DEFAUT")
base_path = os.path.join("data", centre)
os.makedirs(base_path, exist_ok=True)

FICHIER_NOTES = os.path.join(base_path, "notes.xlsx")

if not os.path.exists(FICHIER_NOTES):
    st.error("Fichier notes introuvable pour ce centre")
    st.stop()

df = pd.read_excel(FICHIER_NOTES)

if df.empty:
    st.warning("Aucune donnée disponible")
    st.stop()

# =====================================================
# NETTOYAGE
# =====================================================
df = df.dropna(subset=["Nom", "Prénoms"])
df["Nom complet"] = df["Nom"].astype(str).str.strip() + " " + df["Prénoms"].astype(str).str.strip()

# =====================================================
# LISTE
# =====================================================
candidats = df["Nom complet"].tolist()
if not candidats:
    st.warning("Aucun candidat")
    st.stop()

# =====================================================
# CHOIX
# =====================================================
candidat = st.selectbox("🎓 Choisir un candidat", candidats)
ligne = df[df["Nom complet"] == candidat].iloc[0]

# =====================================================
# MATIÈRES
# =====================================================
matieres = ["Lecture","Exp écrite","Dictée","Math","EST","ES","EA/Dessin/Couture","EA/Chant-Poésie","EPS"]

notes_df = pd.DataFrame({"Matière": matieres, "Note": [ligne[m] for m in matieres]})

# Gestion des absences
notes_affichage = notes_df.copy()
notes_affichage["Note"] = notes_affichage["Note"].apply(lambda x: "ABS" if x == -1 else f"{float(x):.1f}/20")

# =====================================================
# INFO MENTION
# =====================================================
if ligne["OBS"] == "ABSENT":
    mention = "ABSENT"
else:
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
# PDF GENERATION
# =====================================================
def generate_pdf(ligne, notes_affichage, mention):
    file = f"releve_{centre}_{ligne['N° Table']}.pdf"
    doc = SimpleDocTemplate(file, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # HEADER
    header = Paragraph(f"""
    <para align='center'>
    <b style='font-size:18px;'>RÉPUBLIQUE DU BÉNIN – MINISTÈRE DE L’ÉDUCATION</b><br/>
    <b style='font-size:16px;'>CENTRE D’EXAMEN CEP – {centre}</b><br/>
    <b style='font-size:14px;'>RELEVÉ OFFICIEL DE NOTES</b><br/>
    SESSION 2026
    </para>
    """, styles["Title"])
    elements += [header, Spacer(1, 20), HRFlowable(width="100%"), Spacer(1, 15)]

    # INFOS
    infos = Paragraph(f"""
    <font size=12>
    <b>Nom :</b> {ligne['Nom']}<br/>
    <b>Prénoms :</b> {ligne['Prénoms']}<br/>
    <b>N° Table :</b> {ligne['N° Table']}<br/>
    <b>Sexe :</b> {ligne['Sexe']}<br/>
    <b>École :</b> {ligne['Ecole de provenance']}
    </font>
    """, styles["BodyText"])
    elements += [infos, Spacer(1, 15)]

    # TABLE
    table_data = [["Matière", "Note /20"]]
    for _, row in notes_affichage.iterrows():
        table_data.append([row["Matière"], row["Note"]])
    table = Table(table_data, colWidths=[300, 120])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
    ]))
    elements += [table, Spacer(1, 20)]

    # RESULTATS
    resultats = Paragraph(f"""
    <font size=12>
    <b>Total :</b> {ligne['Total'] if ligne['OBS'] != 'ABSENT' else '-'}<br/>
    <b>Moyenne :</b> {ligne['Moyenne'] if ligne['OBS'] != 'ABSENT' else '-'} /20<br/>
    <b>Rang :</b> {ligne['Rang'] if ligne['OBS'] != 'ABSENT' else '-'}<br/>
    <b>Mention :</b> {mention}<br/>
    <b>Observation :</b> {ligne['OBS']}
    </font>
    """, styles["BodyText"])
    elements += [resultats, Spacer(1, 40)]

    # SIGNATURE
    signature = Paragraph("""
    <para align='right'>
    Le Chef Centre<br/><br/>
    _______________________
    </para>
    """, styles["BodyText"])
    elements.append(signature)

    doc.build(elements)
    return file

# =====================================================
# GENERATION PDF
# =====================================================
if st.button("📄 Générer le relevé PDF", use_container_width=True):
    pdf = generate_pdf(ligne, notes_affichage, mention)
    with open(pdf, "rb") as f:
        st.download_button("⬇️ Télécharger PDF", f, file_name=pdf, mime="application/pdf")

# =====================================================
# RETOUR
# =====================================================
if st.button("🏠 Accueil", use_container_width=True):
    st.switch_page("app.py")
