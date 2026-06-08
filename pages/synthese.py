import os

import pandas as pd
import streamlit as st
from fpdf import FPDF


st.set_page_config(page_title="Synthèse CEP", page_icon="📊", layout="wide")


if "authentication_status" not in st.session_state:
    st.error("Veuillez vous connecter")
    st.stop()

if not st.session_state["authentication_status"]:
    st.error("Accès refusé")
    st.stop()


st.title("📊 Synthèse CEP")
st.success(f"Bienvenue {st.session_state['name']}")


centre = st.session_state.get("centre", "CENTRE_PAR_DEFAUT")
base_path = os.path.join("data", centre)
fichier_notes = os.path.join(base_path, "notes.xlsx")

if not os.path.exists(fichier_notes):
    st.error("Fichier notes introuvable")
    st.stop()

df = pd.read_excel(fichier_notes, engine="openpyxl")

if df.empty:
    st.warning("Aucune donnée disponible pour ce centre")
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


def export_pdf_tableau(tableau, titre, file_name):
    os.makedirs(base_path, exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, f"Synthese CEP - {centre}", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, titre, ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "", 9)
    for _, row in tableau.reset_index().iterrows():
        texte = " | ".join(str(x) for x in row.values)
        pdf.multi_cell(0, 7, texte[:180])

    pdf.ln(15)
    pdf.cell(200, 10, "Rapport officiel - CEP 2026", ln=True, align="C")
    pdf.cell(200, 10, "Le Chef du centre", ln=True, align="R")

    file_path = os.path.join(base_path, file_name)
    pdf.output(file_path)
    return file_path


df = df.copy()
df["Sexe_code"] = df["Sexe"].apply(sexe_code)


st.subheader("📋 Statistiques par sexe")

df_par_sexe = df.groupby("Sexe_code").agg(
    Inscrits=("Nom", "count"),
    Admis=("OBS", lambda x: (x == "Admis").sum()),
)
df_par_sexe.loc["Total"] = [df["Nom"].count(), (df["OBS"] == "Admis").sum()]
df_par_sexe["% Réussite"] = [
    pourcentage(row.Admis, row.Inscrits) for row in df_par_sexe.itertuples()
]

st.dataframe(df_par_sexe, use_container_width=True)

if st.button("📄 Exporter Statistiques par sexe en PDF"):
    file_path = export_pdf_tableau(
        df_par_sexe, "Statistiques par sexe", "statistiques_par_sexe.pdf"
    )
    with open(file_path, "rb") as f:
        st.download_button(
            "⬇️ Télécharger PDF",
            f,
            file_name="statistiques_par_sexe.pdf",
            mime="application/pdf",
        )


st.subheader("📋 Statistiques par école")

stats_ecoles = []
for ecole, groupe in df.groupby("Ecole de provenance"):
    inscrits_g = int((groupe["Sexe_code"] == "G").sum())
    inscrits_f = int((groupe["Sexe_code"] == "F").sum())
    admis_g = int(((groupe["Sexe_code"] == "G") & (groupe["OBS"] == "Admis")).sum())
    admis_f = int(((groupe["Sexe_code"] == "F") & (groupe["OBS"] == "Admis")).sum())
    inscrits_t = inscrits_g + inscrits_f
    admis_t = admis_g + admis_f

    stats_ecoles.append(
        {
            "École": ecole,
            "Inscrits_G": inscrits_g,
            "Inscrits_F": inscrits_f,
            "Inscrits_T": inscrits_t,
            "Admis_G": admis_g,
            "Admis_F": admis_f,
            "Admis_T": admis_t,
            "% Réussite G": pourcentage(admis_g, inscrits_g),
            "% Réussite F": pourcentage(admis_f, inscrits_f),
            "% Réussite T": pourcentage(admis_t, inscrits_t),
        }
    )

df_ecole = pd.DataFrame(stats_ecoles)
st.dataframe(df_ecole, use_container_width=True)

if st.button("📄 Exporter Statistiques par école en PDF"):
    file_path = export_pdf_tableau(
        df_ecole, "Statistiques par école", "statistiques_par_ecole.pdf"
    )
    with open(file_path, "rb") as f:
        st.download_button(
            "⬇️ Télécharger PDF",
            f,
            file_name="statistiques_par_ecole.pdf",
            mime="application/pdf",
        )


st.subheader("📋 Statistiques par matière")

stats_matieres = []
for matiere in MATIERES:
    if matiere not in df.columns:
        continue

    notes_valides = df[df[matiere] != -1]
    garcons = notes_valides[notes_valides["Sexe_code"] == "G"]
    filles = notes_valides[notes_valides["Sexe_code"] == "F"]

    inscrits_g = len(garcons)
    inscrits_f = len(filles)
    admis_g = int((garcons[matiere] >= 10).sum())
    admis_f = int((filles[matiere] >= 10).sum())
    inscrits_t = inscrits_g + inscrits_f
    admis_t = admis_g + admis_f

    stats_matieres.append(
        {
            "Matière": matiere,
            "Inscrits_G": inscrits_g,
            "Inscrits_F": inscrits_f,
            "Inscrits_T": inscrits_t,
            "Admis_G": admis_g,
            "Admis_F": admis_f,
            "Admis_T": admis_t,
            "% Réussite G": pourcentage(admis_g, inscrits_g),
            "% Réussite F": pourcentage(admis_f, inscrits_f),
            "% Réussite T": pourcentage(admis_t, inscrits_t),
        }
    )

df_matiere = pd.DataFrame(stats_matieres)
st.dataframe(df_matiere, use_container_width=True)

if st.button("📄 Exporter Statistiques par matière en PDF"):
    file_path = export_pdf_tableau(
        df_matiere, "Statistiques par matière", "statistiques_par_matiere.pdf"
    )
    with open(file_path, "rb") as f:
        st.download_button(
            "⬇️ Télécharger PDF",
            f,
            file_name="statistiques_par_matiere.pdf",
            mime="application/pdf",
        )


st.subheader("🏆 Top 5 Garçons")
df_top5_garcons = df[df["Sexe_code"] == "G"].sort_values("Total", ascending=False).head(5)
st.dataframe(df_top5_garcons, use_container_width=True)

st.subheader("🏆 Top 5 Filles")
df_top5_filles = df[df["Sexe_code"] == "F"].sort_values("Total", ascending=False).head(5)
st.dataframe(df_top5_filles, use_container_width=True)


if st.button("🏠 Accueil"):
    st.switch_page("app.py")
