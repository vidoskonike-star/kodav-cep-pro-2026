import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="KODAV CEP PRO - Saisie Rapide",
    page_icon="📝",
    layout="centered"
)

# =====================================================
# CHARGEMENT DES DONNÉES
# =====================================================

if "df_notes" not in st.session_state:

    st.session_state.df_notes = pd.DataFrame({
        "N° Table": [1, 2, 3, 4, 5],
        "Nom": [
            "AHOUANVOEBLA David",
            "KOSSOU Marc",
            "ADJOVI Marie",
            "HOUNKPATIN Jean",
            "SOSSOU Paul"
        ],
        "Note": ["", "", "", "", ""]
    })

df = st.session_state.df_notes

# =====================================================
# INDEX CANDIDAT COURANT
# =====================================================

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

index = st.session_state.current_index
total = len(df)

# =====================================================
# PROGRESSION
# =====================================================

st.title("⚡ Saisie Rapide PRO")

st.progress((index + 1) / total)

st.caption(f"Candidat {index + 1} sur {total}")

# =====================================================
# CANDIDAT ACTUEL
# =====================================================

candidat = df.iloc[index]

st.markdown("---")

st.markdown(
    f"""
    <div style="
        padding:20px;
        border-radius:15px;
        background:#f5f5f5;
        text-align:center;
    ">
        <h2>N° TABLE : {candidat['N° Table']}</h2>
        <h3>{candidat['Nom']}</h3>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("")

# =====================================================
# STATUT
# =====================================================

note_actuelle = candidat["Note"]

if note_actuelle == "-":
    st.error("🚫 ABSENT")

elif str(note_actuelle).strip() != "":
    st.success(f"✅ Note enregistrée : {note_actuelle}")

else:
    st.warning("⏳ Note non saisie")

# =====================================================
# SAISIE
# =====================================================

note = st.text_input(
    "Note",
    value="" if pd.isna(note_actuelle) else str(note_actuelle),
    placeholder="Ex : 15 ou -",
    key=f"saisie_{index}"
)

# =====================================================
# BOUTONS ACTION
# =====================================================

col1, col2 = st.columns(2)

with col1:

    if st.button(
        "💾 Enregistrer",
        use_container_width=True
    ):
        df.loc[index, "Note"] = note.strip()

        st.success("Note enregistrée")

with col2:

    if st.button(
        "🚫 ABSENT",
        use_container_width=True
    ):
        df.loc[index, "Note"] = "-"
        st.rerun()

# =====================================================
# NAVIGATION
# =====================================================

st.markdown("---")

col1, col2 = st.columns(2)

with col1:

    if st.button(
        "⬅ Précédent",
        use_container_width=True,
        disabled=index == 0
    ):
        st.session_state.current_index -= 1
        st.rerun()

with col2:

    if st.button(
        "Suivant ➡",
        use_container_width=True,
        disabled=index == total - 1
    ):
        st.session_state.current_index += 1
        st.rerun()

# =====================================================
# STATISTIQUES
# =====================================================

st.markdown("---")

absents = (df["Note"] == "-").sum()

saisis = (
    (df["Note"] != "")
    & (df["Note"] != "-")
).sum()

non_saisis = total - absents - saisis

c1, c2, c3 = st.columns(3)

c1.metric("✅ Saisis", int(saisis))
c2.metric("🚫 Absents", int(absents))
c3.metric("⏳ Restants", int(non_saisis))

# =====================================================
# APERÇU GLOBAL
# =====================================================

with st.expander("📋 Voir toutes les notes"):

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

# =====================================================
# EXPORT
# =====================================================

if st.button("📥 Exporter les notes"):

    df_export = df.copy()

    df_export["Statut"] = df_export["Note"].apply(
        lambda x: "Absent" if x == "-" else "Présent"
    )

    fichier = "notes_saisies.xlsx"

    df_export.to_excel(
        fichier,
        index=False
    )

    st.success("Export terminé")