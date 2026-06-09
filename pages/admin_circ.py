import os
from io import BytesIO

import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


st.set_page_config(
    page_title="Synthese Circonscription",
    page_icon="📊",
    layout="wide",
)


if "authentication_status" not in st.session_state:
    st.error("Veuillez vous connecter")
    st.stop()

if st.session_state["authentication_status"] is not True:
    st.error("Acces refuse")
    st.stop()

role = st.session_state.get("role", "teacher")
if role not in {"admin", "circonscription"}:
    st.error("Cette page est reservee a l'administration de circonscription")
    st.stop()


MATIERES = [
    "Lecture",
    "Exp écrite",
    "Dictée",
    "Math",
    "EST",
    "ES",
    "EA/Dessin/Couture",
    "EA/Chant-Poésie",
    "EPS",
]


def sexe_code(valeur):
    valeur = str(valeur).strip().lower()
    if valeur in {"m", "masculin", "garçon", "garcon"}:
        return "G"
    if valeur in {"f", "féminin", "feminin", "fille"}:
        return "F"
    return "Autre"


def pourcentage(admis, inscrits):
    if inscrits == 0:
        return 0
    return round((admis / inscrits) * 100, 1)


def charger_notes_centres():
    lignes = []
    erreurs = []

    if not os.path.isdir("data"):
        return pd.DataFrame(), ["Dossier data introuvable"]

    for centre in sorted(os.listdir("data")):
        dossier = os.path.join("data", centre)
        fichier_notes = os.path.join(dossier, "notes.xlsx")

        if not os.path.isdir(dossier) or not os.path.exists(fichier_notes):
            continue

        try:
            df_centre = pd.read_excel(fichier_notes, engine="openpyxl")
            if df_centre.empty:
                continue

            df_centre = df_centre.copy()
            df_centre["Centre"] = centre
            lignes.append(df_centre)
        except Exception as exc:
            erreurs.append(f"{centre}: {exc}")

    if not lignes:
        return pd.DataFrame(), erreurs

    return pd.concat(lignes, ignore_index=True), erreurs


def preparer_donnees(df):
    df = df.copy()
    df["Sexe_code"] = df["Sexe"].apply(sexe_code) if "Sexe" in df.columns else "Autre"

    for matiere in MATIERES:
        if matiere in df.columns:
            df[matiere] = pd.to_numeric(df[matiere], errors="coerce").fillna(0)

    matieres_presentes = [matiere for matiere in MATIERES if matiere in df.columns]
    if matieres_presentes:
        absents = (df[matieres_presentes] == -1).any(axis=1)
        df["Absent_calc"] = absents
        df["Total_calc"] = df[matieres_presentes].replace(-1, 0).sum(axis=1)
        df["Moyenne_calc"] = (df["Total_calc"] / len(matieres_presentes)).round(2)
    else:
        df["Absent_calc"] = False
        df["Total_calc"] = pd.to_numeric(df.get("Total", 0), errors="coerce").fillna(0)
        df["Moyenne_calc"] = pd.to_numeric(df.get("Moyenne", 0), errors="coerce").fillna(0)

    if "Total" not in df.columns:
        df["Total"] = df["Total_calc"]
    if "Moyenne" not in df.columns:
        df["Moyenne"] = df["Moyenne_calc"]
    if "OBS" not in df.columns:
        df["OBS"] = df["Moyenne_calc"].apply(lambda x: "Admis" if x >= 10 else "Ajourné")

    df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(df["Total_calc"])
    df["Moyenne"] = pd.to_numeric(df["Moyenne"], errors="coerce").fillna(df["Moyenne_calc"])
    df["OBS_norm"] = df["OBS"].astype(str).str.upper().str.strip()
    df["Admis_calc"] = (~df["Absent_calc"]) & (df["Moyenne"] >= 10)
    return df


def stats_par_centre(df):
    lignes = []
    for centre, groupe in df.groupby("Centre"):
        inscrits = len(groupe)
        absents = int(groupe["Absent_calc"].sum())
        presents = inscrits - absents
        admis = int(groupe["Admis_calc"].sum())
        ajournes = max(presents - admis, 0)
        moyenne = round(groupe.loc[~groupe["Absent_calc"], "Moyenne"].mean(), 2) if presents else 0

        lignes.append(
            {
                "Centre": centre,
                "Inscrits": inscrits,
                "Presents": presents,
                "Absents": absents,
                "Admis": admis,
                "Ajournes": ajournes,
                "Taux reussite": pourcentage(admis, presents),
                "Moyenne generale": moyenne,
            }
        )

    return pd.DataFrame(lignes).sort_values("Taux reussite", ascending=False)


def stats_par_sexe(df):
    lignes = []
    for sexe, groupe in df.groupby("Sexe_code"):
        inscrits = len(groupe)
        absents = int(groupe["Absent_calc"].sum())
        presents = inscrits - absents
        admis = int(groupe["Admis_calc"].sum())
        lignes.append(
            {
                "Sexe": sexe,
                "Inscrits": inscrits,
                "Presents": presents,
                "Absents": absents,
                "Admis": admis,
                "Ajournes": max(presents - admis, 0),
                "Taux reussite": pourcentage(admis, presents),
            }
        )

    total_inscrits = len(df)
    total_absents = int(df["Absent_calc"].sum())
    total_presents = total_inscrits - total_absents
    total_admis = int(df["Admis_calc"].sum())
    lignes.append(
        {
            "Sexe": "Total",
            "Inscrits": total_inscrits,
            "Presents": total_presents,
            "Absents": total_absents,
            "Admis": total_admis,
            "Ajournes": max(total_presents - total_admis, 0),
            "Taux reussite": pourcentage(total_admis, total_presents),
        }
    )

    return pd.DataFrame(lignes)


def stats_par_matiere(df):
    lignes = []
    for matiere in MATIERES:
        if matiere not in df.columns:
            continue

        notes = df[matiere]
        absents = int((notes == -1).sum())
        notes_valides = notes[notes != -1]
        inscrits = len(notes)
        presents = len(notes_valides)
        admis = int((notes_valides >= 10).sum())

        lignes.append(
            {
                "Matiere": matiere,
                "Inscrits": inscrits,
                "Presents": presents,
                "Absents": absents,
                "Notes >= 10": admis,
                "Notes < 10": max(presents - admis, 0),
                "Taux reussite": pourcentage(admis, presents),
                "Moyenne": round(notes_valides.mean(), 2) if presents else 0,
            }
        )

    return pd.DataFrame(lignes).sort_values("Moyenne", ascending=False)


def creer_export_excel(feuilles):
    sortie = BytesIO()
    with pd.ExcelWriter(sortie, engine="xlsxwriter") as writer:
        for nom, tableau in feuilles.items():
            tableau.to_excel(writer, sheet_name=nom[:31], index=False)
    sortie.seek(0)
    return sortie


def texte_pdf(valeur):
    if pd.isna(valeur):
        return ""
    texte = str(valeur)
    return texte.encode("latin-1", "replace").decode("latin-1")


def tableau_pdf(titre, tableau, styles, largeur_disponible):
    elements = [
        Paragraph(texte_pdf(titre), styles["Heading2"]),
        Spacer(1, 8),
    ]

    if tableau.empty:
        elements.append(Paragraph("Aucune donnee disponible.", styles["BodyText"]))
        elements.append(Spacer(1, 14))
        return elements

    donnees = [list(tableau.columns)]
    donnees.extend(tableau.astype(object).values.tolist())

    nb_colonnes = max(len(donnees[0]), 1)
    largeur_colonne = largeur_disponible / nb_colonnes
    style_cellule = styles["BodyText"]
    style_cellule.fontSize = 7
    style_cellule.leading = 8

    donnees_pdf = [
        [Paragraph(texte_pdf(cellule), style_cellule) for cellule in ligne]
        for ligne in donnees
    ]

    table = Table(donnees_pdf, colWidths=[largeur_colonne] * nb_colonnes, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#174A3C")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F5F3")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )

    elements.append(table)
    elements.append(Spacer(1, 18))
    return elements


def creer_export_pdf(feuilles):
    sortie = BytesIO()
    doc = SimpleDocTemplate(
        sortie,
        pagesize=landscape(A4),
        rightMargin=24,
        leftMargin=24,
        topMargin=24,
        bottomMargin=24,
        title="Synthese circonscription CEP",
    )

    styles = getSampleStyleSheet()
    largeur_disponible = doc.width
    elements = [
        Paragraph("Synthese de la circonscription - CEP 2026", styles["Title"]),
        Spacer(1, 8),
        Paragraph(
            "Rapport compile automatiquement a partir des fichiers notes.xlsx de tous les centres.",
            styles["BodyText"],
        ),
        Spacer(1, 16),
    ]

    for index, (titre, tableau) in enumerate(feuilles.items()):
        if index > 0:
            elements.append(PageBreak())
        elements.extend(tableau_pdf(titre, tableau, styles, largeur_disponible))

    doc.build(elements)
    sortie.seek(0)
    return sortie


st.title("📊 Synthese de la circonscription")
st.caption("Compilation automatique des fichiers notes.xlsx de tous les centres.")

df_brut, erreurs = charger_notes_centres()

if erreurs:
    with st.expander("Centres avec erreur de lecture"):
        for erreur in erreurs:
            st.warning(erreur)

if df_brut.empty:
    st.error("Aucune donnee de notes n'a ete trouvee dans les centres.")
    st.stop()

df = preparer_donnees(df_brut)

tableau_centres = stats_par_centre(df)
tableau_sexe = stats_par_sexe(df)
tableau_matiere = stats_par_matiere(df)

inscrits_total = len(df)
absents_total = int(df["Absent_calc"].sum())
presents_total = inscrits_total - absents_total
admis_total = int(df["Admis_calc"].sum())
ajournes_total = max(presents_total - admis_total, 0)
taux_global = pourcentage(admis_total, presents_total)
moyenne_globale = round(df.loc[~df["Absent_calc"], "Moyenne"].mean(), 2) if presents_total else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Centres", tableau_centres["Centre"].nunique())
c2.metric("Candidats", inscrits_total)
c3.metric("Admis", admis_total)
c4.metric("Taux reussite", f"{taux_global}%")

c5, c6, c7, c8 = st.columns(4)
c5.metric("Presents", presents_total)
c6.metric("Absents", absents_total)
c7.metric("Ajournes", ajournes_total)
c8.metric("Moyenne generale", moyenne_globale)

st.divider()

st.subheader("Statistiques par centre")
st.dataframe(tableau_centres, use_container_width=True, hide_index=True)

st.subheader("Statistiques par sexe")
st.dataframe(tableau_sexe, use_container_width=True, hide_index=True)

st.subheader("Statistiques par matiere")
st.dataframe(tableau_matiere, use_container_width=True, hide_index=True)

st.subheader("Top 10 candidats")
colonnes_top = [
    col
    for col in ["Centre", "N° Table", "Nom", "Prénoms", "Sexe", "Total", "Moyenne", "OBS"]
    if col in df.columns
]
top_10 = df[~df["Absent_calc"]].sort_values("Moyenne", ascending=False).head(10)
st.dataframe(top_10[colonnes_top], use_container_width=True, hide_index=True)

st.subheader("Export")
resume = pd.DataFrame(
    [
        {
            "Centres": tableau_centres["Centre"].nunique(),
            "Inscrits": inscrits_total,
            "Presents": presents_total,
            "Absents": absents_total,
            "Admis": admis_total,
            "Ajournes": ajournes_total,
            "Taux reussite": taux_global,
            "Moyenne generale": moyenne_globale,
        }
    ]
)

feuilles_export = {
    "Resume global": resume,
    "Par centre": tableau_centres,
    "Par sexe": tableau_sexe,
    "Par matiere": tableau_matiere,
    "Top candidats": top_10[colonnes_top],
}

export_excel = creer_export_excel(feuilles_export)
export_pdf = creer_export_pdf(feuilles_export)

st.download_button(
    "Telecharger la synthese Excel",
    data=export_excel,
    file_name="synthese_circonscription.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)

st.download_button(
    "Telecharger la synthese PDF",
    data=export_pdf,
    file_name="synthese_circonscription.pdf",
    mime="application/pdf",
    use_container_width=True,
)

if st.button("Accueil", use_container_width=True):
    st.switch_page("app.py")
