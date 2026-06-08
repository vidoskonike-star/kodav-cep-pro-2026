import pandas as pd
import os

# Charger les anciens fichiers globaux
df_candidats = pd.read_excel("data/candidats.xlsx")
df_notes = pd.read_excel("data/notes.xlsx")

# Liste des centres connus
centres = [
    "CENTRE_DE_DOKO",
    "CENTRE_DE_HOUEDOGLI",
    "CENTRE_DE_MISSINKO",
    "CENTRE_DE_TANNOU_GOLA",
    "CENTRE_DE_TOHOUNHOUE",
    "CENTRE_DE_TOVIKLIN"
]

# Boucle sur chaque centre
for centre in centres:
    dossier = f"data/{centre}/"
    os.makedirs(dossier, exist_ok=True)

    # ⚠️ Ici, il faut savoir comment distinguer les candidats de chaque centre
    # Si ton ancien fichier n’a pas de colonne "Centre", il faut que tu ajoutes manuellement
    # une information (par exemple une feuille Excel par centre, ou un fichier par centre).
    # Sinon, le script ne peut pas deviner à quel centre appartient chaque candidat.

    # Pour l’instant, on copie tout le fichier dans chaque centre (à adapter ensuite)
    df_candidats.to_excel(os.path.join(dossier, "candidats.xlsx"), index=False)
    df_notes.to_excel(os.path.join(dossier, "notes.xlsx"), index=False)

print("✅ Migration terminée : fichiers copiés dans chaque centre.")
