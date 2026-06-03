import streamlit as st
import pandas as pd
import os

# =====================================================
# CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Saisie Rapide PRO",
    page_icon="⚡",
    layout="centered"
)

# =====================================================
# SECURITE
# =====================================================

if "authentication_status" not in st.session_state:
    st.error("Veuillez vous connecter")
    st.stop()

if st.session_state["authentication_status"] is not True:
    st.error("Accès refusé")
    st.stop()

# =====================================================
# FICHIERS
# =====================================================

FICHIER_NOTES = "data/notes.xlsx"

if not os.path.exists(FICHIER_NOTES):
    st.error("Fichier notes introuvable")
    st.stop()

# =====================================================
# CHARGEMENT
# =====================================================

df = pd.read_excel(FICHIER_NOTES)

if len(df) == 0:
    st.warning("Aucun candidat trouvé.")
    st.stop()

df = df.sort_values("N° Table").reset_index(drop=True)

# =====================================================
# INDEX COURANT
# =====================================================

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

index = st.session_state.current_index

if index >= len(df):
    st.session_state.current_index = 0
    index = 0

total = len(df)

# =====================================================
# TITRE
# =====================================================

st.title("⚡ Saisie Rapide PRO")

# =====================================================
# CHOIX MATIERE
# =====================================================

matiere = st.selectbox(
    "📚 Matière",
    [
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
)

# =====================================================
# PROGRESSION
# =====================================================

st.progress((index + 1) / total)

st.caption(f"Candidat {index + 1} sur {total}")

# =====================================================
# CANDIDAT
# =====================================================

candidat = df.iloc[index]

nom_complet = f"{candidat['Nom']} {candidat['Prénoms']}"

st.markdown(
    f"""
    <div style="
        padding:20px;
        border-radius:15px;
        background:#f5f5f5;
        text-align:center;
        margin-bottom:15px;
    ">
        <h2>N° TABLE : {candidat['N° Table']}</h2>
        <h3>{nom_complet}</h3>
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================
# STATUT
# =====================================================

note_actuelle = candidat[matiere]

if pd.notna(note_actuelle) and note_actuelle == -1:
    st.error("🚫 ABSENT")

elif pd.notna(note_actuelle):
    st.success(f"✅ Note actuelle : {note_actuelle}")

else:
    st.warning("⏳ Non saisi")

# =====================================================
# SAISIE
# =====================================================

note = st.text_input(
    "Note",
    value=""
    if pd.isna(note_actuelle) or note_actuelle == -1
    else str(note_actuelle),
    placeholder="Exemple : 15",
    key=f"note_{index}_{matiere}"
)

# =====================================================
# ACTIONS
# =====================================================

col1, col2 = st.columns(2)

with col1:

    if st.button(
        "💾 Enregistrer",
        use_container_width=True
    ):

        try:

            valeur = float(note)

            if valeur < 0 or valeur > 20:
                st.error("La note doit être comprise entre 0 et 20")

            else:

                df.loc[index, matiere] = valeur

                df.to_excel(FICHIER_NOTES, index=False)

                if index < total - 1:
                    st.session_state.current_index += 1

                st.rerun()

        except:
            st.error("Entrez une note valide")

with col2:

    if st.button(
        "🚫 ABSENT",
        use_container_width=True
    ):

        df.loc[index, matiere] = -1

        df.to_excel(FICHIER_NOTES, index=False)

        if index < total - 1:
            st.session_state.current_index += 1

        st.rerun()

# =====================================================
# NAVIGATION
# =====================================================

st.markdown("---")

col1, col2 = st.columns(2)

with col1:

    if st.button(
        "⬅ Précédent",
        disabled=index == 0,
        use_container_width=True
    ):
        st.session_state.current_index -= 1
        st.rerun()

with col2:

    if st.button(
        "Suivant ➡",
        disabled=index == total - 1,
        use_container_width=True
    ):
        st.session_state.current_index += 1
        st.rerun()

# =====================================================
# STATISTIQUES
# =====================================================

st.markdown("---")

absents = (df[matiere] == -1).sum()

saisis = (
    df[matiere].notna()
    & (df[matiere] != -1)
).sum()

restants = total - absents - saisis

c1, c2, c3 = st.columns(3)

c1.metric("✅ Saisis", int(saisis))
c2.metric("🚫 Absents", int(absents))
c3.metric("⏳ Restants", int(restants))

# =====================================================
# APERCU
# =====================================================

with st.expander("📋 Voir les notes de la matière"):

    df_affichage = df.copy()

    df_affichage[matiere] = df_affichage[matiere].replace(-1, "ABS")

    st.dataframe(
        df_affichage[
            [
                "N° Table",
                "Nom",
                "Prénoms",
                matiere
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

# =====================================================
# RETOUR
# =====================================================

if st.button("🏠 Accueil"):
    st.switch_page("app.py")