import os
import yaml
import pandas as pd
from yaml.loader import SafeLoader

# Charger la configuration
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# Récupérer tous les centres depuis le fichier YAML
centres = []
for user in config["credentials"]["usernames"].values():
    if "centre" in user and user["centre"] != "ALL":
        centres.append(user["centre"])

# Supprimer les doublons
centres = list(set(centres))

# Colonnes de base
colonnes_candidats = ["N° Table","Nom","Prénoms","Sexe","Ecole de provenance"]
colonnes_notes = [
    "N° Table","Nom","Prénoms","Sexe","Ecole de provenance",
    "Lecture","Exp écrite","Dictée","Math","EST","ES",
    "EA/Dessin/Couture","EA/Chant-Poésie","EPS",
    "Total","Moy 6/9","Moyenne","Rang","OBS"
]

# Création des dossiers et fichiers
for centre in centres:
    base_path = os.path.join("data", centre)
    os.makedirs(base_path, exist_ok=True)

    fichier_candidats = os.path.join(base_path, "candidats.xlsx")
    fichier_notes = os.path.join(base_path, "notes.xlsx")

    if not os.path.exists(fichier_candidats):
        pd.DataFrame(columns=colonnes_candidats).to_excel(fichier_candidats, index=False)

    if not os.path.exists(fichier_notes):
        pd.DataFrame(columns=colonnes_notes).to_excel(fichier_notes, index=False)

print("✅ Initialisation terminée : tous les centres ont leurs fichiers vides.")
