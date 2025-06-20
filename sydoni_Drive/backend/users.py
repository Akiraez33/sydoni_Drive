import json
import os
from backend.models.user import User
from stockage import load_data, save_data # Importation des fonctions génériques de stockage

# Chemin du fichier de stockage des utilisateurs
USERS_FILE = "data/users.json"

# Assurez-vous que le répertoire 'data' existe (déjà géré par stockage.py)
# os.makedirs("data", exist_ok=True)

def load_users():
    """
    Charge les données des utilisateurs depuis le fichier JSON.
    Retourne une liste d'objets User.
    """
    users_data = load_data(USERS_FILE, default_value=[])
    return [User.from_dict(data) for data in users_data]

def save_users(users):
    """
    Sauvegarde une liste d'objets User dans le fichier JSON.
    """
    users_data = [user.to_dict() for user in users]
    save_data(USERS_FILE, users_data)

def register_user(nom, prenom, telephone, email, universite, role, engin=None, places_disponibles=None, mot_de_passe=None):
    """
    Enregistre un nouvel utilisateur.

    Args:
        nom (str): Nom de l'utilisateur.
        prenom (str): Prénom de l'utilisateur.
        telephone (str): Numéro de téléphone de l'utilisateur.
        email (str): Email de l'utilisateur (doit être unique).
        universite (str): Université de l'utilisateur.
        role (str): Rôle de l'utilisateur ('automobiliste' ou 'passager').
        engin (str, optional): Type d'engin si l'utilisateur est automobiliste. Defaults to None.
        places_disponibles (int, optional): Nombre de places disponibles si l'utilisateur est automobiliste. Defaults to None.
        mot_de_passe (str, optional): Mot de passe de l'utilisateur. Defaults to None.

    Returns:
        tuple: (True, message) si l'enregistrement est réussi, (False, message) sinon.
    """
    users = load_users()

    # Vérifier si l'email existe déjà
    if any(user.email == email for user in users):
        return False, "Un compte avec cet email existe déjà."
    
    # Créer un nouvel objet User
    # Pour l'instant, le mot de passe n'est pas stocké/haché. C'est une amélioration future.
    new_user = User(nom, prenom, email, telephone, universite, role, engin, places_disponibles)
    
    users.append(new_user)
    save_users(users)
    return True, "Utilisateur enregistré avec succès."

def login_user(email, mot_de_passe=None):
    """
    Authentifie un utilisateur par email et mot de passe (actuellement juste l'email).
    
    Args:
        email (str): Email de l'utilisateur.
        mot_de_passe (str, optional): Mot de passe de l'utilisateur. Non utilisé pour l'instant.

    Returns:
        tuple: (True, User, message, role) si la connexion est réussie, (False, None, message, None) sinon.
    """
    users = load_users()
    for user in users:
        if user.email == email: # Pour l'instant, pas de vérification de mot de passe
            # TODO: Implémenter la vérification sécurisée du mot de passe (hachage)
            return True, user, "Connexion réussie !", user.role
    return False, None, "Email ou mot de passe incorrect.", None

def get_user_by_email(email):
    """
    Récupère un objet User par son email.

    Args:
        email (str): Email de l'utilisateur à rechercher.

    Returns:
        User or None: L'objet User si trouvé, sinon None.
    """
    users = load_users()
    for user in users:
        if user.email == email:
            return user
    return None

def update_user_role(email, new_role):
    """
    Met à jour le rôle d'un utilisateur.

    Args:
        email (str): Email de l'utilisateur.
        new_role (str): Nouveau rôle ('automobiliste' ou 'passager').

    Returns:
        tuple: (True, message) si la mise à jour est réussie, (False, message) sinon.
    """
    users = load_users()
    for user in users:
        if user.email == email:
            user.role = new_role
            save_users(users)
            return True, "Rôle mis à jour avec succès."
    return False, "Utilisateur non trouvé."

def update_user_points(email, points_to_add):
    """
    Met à jour les points d'un utilisateur.

    Args:
        email (str): Email de l'utilisateur.
        points_to_add (int): Nombre de points à ajouter (peut être négatif pour retirer des points).

    Returns:
        tuple: (True, message) si la mise à jour est réussie, (False, message) sinon.
    """
    users = load_users()
    for user in users:
        if user.email == email:
            user.points += points_to_add
            save_users(users)
            return True, f"Points de {email} mis à jour. Nouveau total: {user.points}"
    return False, "Utilisateur non trouvé."

def get_user_role(email):
    """
    Retourne le rôle de l'utilisateur identifié par son email.

    Args:
        email (str): Email de l'utilisateur.

    Returns:
        tuple: (True, role) si l'utilisateur est trouvé, (False, None) sinon.
    """
    user = get_user_by_email(email)
    if user:
        return True, user.role
    return False, None

def get_engin_utilisateur(email):
    """
    Récupère le type d'engin d'un automobiliste.

    Args:
        email (str): Email de l'automobiliste.

    Returns:
        str: Le type d'engin si trouvé, sinon une chaîne vide.
    """
    user = get_user_by_email(email)
    if user and user.role == 'automobiliste':
        return user.engin if user.engin else ""
    return "" # Retourne une chaîne vide si l'utilisateur n'est pas trouvé ou n'est pas automobiliste



