import json
import os

# Définition des chemins de fichiers pour le stockage des données
USERS_FILE = "data/users.json"
TRAJETS_FILE = "data/trajets.json"
RESERVATIONS_FILE = "data/reservations.json"
HISTORIQUES_FILE = "data/historiques.json"
ANNONCES_FILE = "data/annonces.json" # Nouveau fichier pour les annonces si elles sont séparées des trajets

# Assurez-vous que le répertoire 'data' existe
# os.makedirs("data", exist_ok=True) # Cette ligne est déplacée dans save_data pour garantir la création avant écriture

def load_data(file_path, default_value=None):
    """
    Charge les données depuis un fichier JSON.

    Args:
        file_path (str): Le chemin du fichier JSON.
        default_value (any): La valeur à retourner si le fichier n'existe pas ou est vide.

    Returns:
        any: Les données chargées ou la valeur par défaut.
    """
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return default_value if default_value is not None else []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Erreur de décodage JSON dans {file_path}. Le fichier est peut-être corrompu.")
        return default_value if default_value is not None else []

def save_data(file_path, data):
    """
    Sauvegarde les données dans un fichier JSON.

    Args:
        file_path (str): Le chemin du fichier JSON.
        data (any): Les données à sauvegarder.
    """
    # Assurez-vous que le répertoire existe avant d'écrire le fichier
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# Fonctions spécifiques pour charger/sauvegarder chaque type de données

def load_users():
    return load_data(USERS_FILE, default_value=[])

def save_users(users):
    save_data(USERS_FILE, users)

def load_trajets():
    return load_data(TRAJETS_FILE, default_value=[])

def save_trajets(trajets):
    save_data(TRAJETS_FILE, trajets)

def load_reservations():
    return load_data(RESERVATIONS_FILE, default_value=[])

def save_reservations(reservations):
    save_data(RESERVATIONS_FILE, reservations)

def load_historiques():
    return load_data(HISTORIQUES_FILE, default_value={})

def save_historiques(historiques):
    save_data(HISTORIQUES_FILE, historiques)

def load_annonces():
    return load_data(ANNONCES_FILE, default_value=[])

def save_annonces(annonces):
    save_data(ANNONCES_FILE, annonces)


def clear_all_data():
    """
    Supprime tous les fichiers de données pour réinitialiser l'état du système.
    Utilisé principalement pour les tests.
    """
    for file_path in [USERS_FILE, TRAJETS_FILE, RESERVATIONS_FILE, HISTORIQUES_FILE, ANNONCES_FILE]:
        if os.path.exists(file_path):
            os.remove(file_path)
    # Supprimer le répertoire data s'il est vide après suppression des fichiers
    if os.path.exists("data") and not os.listdir("data"):
        os.rmdir("data")


