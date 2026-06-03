# =====================================================
# FORMULAIRE NOTES
# =====================================================

st.markdown("### ✍️ Saisie des notes")

def valeur_note(valeur, min_val=0.0, max_val=20.0):
    """
    Nettoie la valeur pour st.number_input :
    - Si NaN → retourne min_val (0.0)
    - Si < min_val → retourne min_val (mais conserve l'info brute dans df_notes)
    - Si > max_val → retourne max_val
    """
    try:
        v = float(valeur)
    except (ValueError, TypeError):
        return min_val

    if pd.isna(v):
        return min_val
    if v < min_val:
        return min_val   # affichage sûr, mais valeur brute reste négative dans df_notes
    if v > max_val:
        return max_val
    return v

with st.form("notes_form"):
    valeurs_saisies = {}
    for col in colonnes_notes:
        valeurs_saisies[col] = st.number_input(
            col,
            0.0,
            20.0,
            valeur_note(df_notes.loc[ligne, col])
        )

    submit = st.form_submit_button("💾 Enregistrer")

# =====================================================
# SAUVEGARDE
# =====================================================

if submit:
    # On enregistre les valeurs saisies
    for col in colonnes_notes:
        df_notes.loc[ligne, col] = valeurs_saisies[col]

    # TOTAL
    df_notes["Total"] = df_notes[colonnes_notes].sum(axis=1)

    # MOYENNE
    df_notes["Moyenne"] = (df_notes["Total"] / len(colonnes_notes)).round(2)

    # MOY 6/9
    df_notes["Moy 6/9"] = (df_notes["Total"] / 6).round(2)

    # OBS
    df_notes["OBS"] = df_notes["Moyenne"].apply(
        lambda x: "Admis" if x >= 10 else "Ajourné"
    )

    # RANG
    df_notes["Rang"] = df_notes["Total"].rank(ascending=False).astype(int)

    df_notes.to_excel(FICHIER_NOTES, index=False)

    st.success("✅ Notes enregistrées")
    st.rerun()
