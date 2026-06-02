import streamlit as st
import pandas as pd
import os

# =====================================================
# CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Rangs & Synthèse",
    page_icon="🏆",
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

st.title("🏆 Classement & Synthèse CEP")
st.success(f"Bienvenue {st.session_state['name']}")

# =====================================================
# FICHIER
# =====================================================

FICHIER_NOTES = "data/notes.xlsx"

if not os.path.exists(FICHIER_NOTES):
    st.error("Fichier notes introuvable")
    st.stop()

df = pd.read_excel(FICHIER_NOTES)

# =====================================================
# NETTOYAGE
# =====================================================

df = df.dropna(subset=["Nom", "Prénoms"], how="all")

matieres = [
    "Lecture", "Exp écrite", "Dictée", "Math",
    "EST", "ES", "EA/Dessin/Couture",
    "EA/Chant-Poésie", "EPS"
]

# =====================================================
# CONVERSION NUMÉRIQUE
# =====================================================

for col in matieres:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df["N° Table"] = pd.to_numeric(df["N° Table"], errors="coerce")

# =====================================================
# RECALCUL
# =====================================================

df["Total"] = df[matieres].sum(axis=1)
df["Moyenne"] = round(df["Total"] / 9, 2)
df["Moy 6/9"] = round(df["Total"] / 6, 2)

df["OBS"] = df["Moyenne"].apply(
    lambda x: "Admis" if x >= 10 else "Ajourné"
)

# =====================================================
# CLASSEMENT
# =====================================================

df = df.sort_values(by="Moyenne", ascending=False).reset_index(drop=True)
df["Rang"] = df.index + 1

# =====================================================
# KPI
# =====================================================

total = len(df)
admis = (df["OBS"] == "Admis").sum()
ajournes = (df["OBS"] == "Ajourné").sum()

taux_reussite = round((admis / total) * 100, 1) if total > 0 else 0
moyenne_generale = round(df["Moyenne"].mean(), 2)

# =====================================================
# DASHBOARD KPI
# =====================================================

c1, c2, c3, c4 = st.columns(4)

c1.metric("👨‍🎓 Total candidats", total)
c2.metric("🏆 Admis", admis)
c3.metric("❌ Ajournés", ajournes)
c4.metric("📈 Taux réussite", f"{taux_reussite}%")

# =====================================================
# MOYENNE GÉNÉRALE
# =====================================================

st.metric("📊 Moyenne générale du centre", moyenne_generale)

st.divider()

# =====================================================
# TOP 10
# =====================================================

st.subheader("🥇 Top 10 du centre")

st.dataframe(
    df.head(10)[["Rang", "N° Table", "Nom", "Prénoms", "Moyenne", "OBS"]],
    use_container_width=True
)

# =====================================================
# DISTRIBUTION DES MOYENNES (VISUEL)
# =====================================================

st.subheader("📊 Répartition des performances")

bins = [0, 5, 8, 10, 12, 14, 16, 20]
labels = ["0-5", "5-8", "8-10", "10-12", "12-14", "14-16", "16-20"]

df["Tranche"] = pd.cut(df["Moyenne"], bins=bins, labels=labels, include_lowest=True)

distribution = df["Tranche"].value_counts().sort_index()

st.bar_chart(distribution)

# =====================================================
# TABLEAU COMPLET
# =====================================================

st.subheader("📋 Classement complet")

st.dataframe(df, use_container_width=True, height=600)

# =====================================================
# EXPORT
# =====================================================

with open(FICHIER_NOTES, "rb") as f:
    st.download_button(
        "📥 Télécharger classement Excel",
        data=f,
        file_name="classement_CEP.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# =====================================================
# RETOUR
# =====================================================

if st.button("🏠 Retour à l'accueil"):
    st.switch_page("app.py")