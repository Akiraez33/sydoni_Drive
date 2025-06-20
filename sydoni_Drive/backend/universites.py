import json
import os
from stockage import load_data, save_data # Importation des fonctions génériques de stockage

# Chemin du fichier de stockage des universités
UNIVERSITES_FILE = "data/universites.json"

# Assurez-vous que le répertoire 'data' existe (déjà géré par stockage.py)
# os.makedirs("data", exist_ok=True)

def charger_universites():
    """
    Charge les données des universités depuis le fichier JSON.
    Utilise la fonction générique load_data du module stockage.

    Returns:
        list: Une liste de dictionnaires représentant les universités.
    """
    # Si le fichier universites.json est vide ou n'existe pas, on peut initialiser avec des données par défaut
    # ou s'assurer que le fichier est créé avec les universités initiales.
    # Pour l'instant, nous allons charger ce qui est dans le fichier.
    return load_data(UNIVERSITES_FILE, default_value=[])

def sauvegarder_universites(universites):
    """
    Sauvegarde les données des universités dans le fichier JSON.
    Utilise la fonction générique save_data du module stockage.

    Args:
        universites (list): Une liste de dictionnaires représentant les universités.
    """
    save_data(UNIVERSITES_FILE, universites)

def get_coordonnees_universite(nom_universite):
    """
    Récupère les coordonnées (latitude, longitude) d'une université par son nom.

    Args:
        nom_universite (str): Le nom de l'université à rechercher.

    Returns:
        tuple: Un tuple (latitude, longitude) si l'université est trouvée, sinon (None, None).
    """
    universites = charger_universites()
    for univ in universites:
        if univ["nom"].lower() == nom_universite.lower():
            return univ["latitude"], univ["longitude"]
    return None, None

# Les universités initiales peuvent être stockées directement dans le fichier JSON
# ou utilisées pour initialiser le fichier si celui-ci est vide.
# Il est préférable de ne pas avoir une liste hardcodée ici si elle est aussi dans le JSON.
# Pour l'exemple, si le fichier est vide, nous pourrions l'initialiser:
# if not os.path.exists(UNIVERSITES_FILE) or os.path.getsize(UNIVERSITES_FILE) == 0:
#     initial_universites = [
#         {
#             "nom": "Burkina Institut of Technology(BIT)",
#             "latitude": 12.2419,
#             "longitude": -2.4083
#         },
#         {
#             "nom": "Université Norbert Zongo (UNZ)",
#             "latitude": 12.2400,
#             "longitude": -2.3990
#         },
#         {
#             "nom": "Institut Supérieur de Management de Koudougou (ISMK)",
#             "latitude": 12.2526,
#             "longitude": -2.3627
#         }
#     ]
#     sauvegarder_universites(initial_universites)

# Note: La liste UNIVERSITES hardcodée dans le fichier original n'est pas utilisée
# si les données sont chargées depuis un fichier. Il est recommandé de la supprimer
# ou de l'utiliser uniquement pour l'initialisation du fichier JSON.




# Initialisation du fichier universites.json si vide ou inexistant
if not os.path.exists(UNIVERSITES_FILE) or os.path.getsize(UNIVERSITES_FILE) == 0:
    initial_universites = [
        {
            "nom": "Burkina Institut of Technology(BIT)",
            "latitude": 12.2419,
            "longitude": -2.4083
        },
        {
            "nom": "Université Norbert Zongo (UNZ)",
            "latitude": 12.2400,
            "longitude": -2.3990
        },
        {
            "nom": "Institut Supérieur de Management de Koudougou (ISMK)",
            "latitude": 12.2526,
            "longitude": -2.3627
        }
    ]
    sauvegarder_universites(initial_universites)


