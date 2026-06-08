import pandas as pd

# Charger les fichiers globaux
df_candidats = pd.read_excel("data/candidats.xlsx")
df_notes = pd.read_excel("data/notes.xlsx")

# Ajouter une colonne 'Centre' vide si elle n'existe pas déjà
if "Centre" not in df_candidats.columns:
    df_candidats["Centre"] = ""
if "Centre" not in df_notes.columns:
    df_notes["Centre"] = ""

# Sauvegarder les fichiers modifiés
df_candidats.to_excel("data/candidats.xlsx", index=False)
df_notes.to_excel("data/notes.xlsx", index=False)

print("✅ Colonne 'Centre' ajoutée aux fichiers candidats.xlsx et notes.xlsx")
