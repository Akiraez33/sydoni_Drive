import json
import os
from backend.models.reservation import Reservation
from backend.models.annonce import get_annonce_by_id, update_annonce # Importation de update_annonce
from stockage import load_data, save_data # Importation des fonctions génériques de stockage

# Chemin du fichier de stockage des réservations
RESERVATION_FILE = os.path.join("data", "reservations.json")

# Assurez-vous que le répertoire 'data' existe (déjà géré par stockage.py)
# os.makedirs("data", exist_ok=True)

def charger_reservations():
    """
    Charge les données des réservations depuis le fichier JSON.
    Retourne une liste d'objets Reservation.
    """
    reservations_data = load_data(RESERVATION_FILE, default_value=[])
    return [Reservation.from_dict(data) for data in reservations_data]

def sauvegarder_reservations(reservations):
    """
    Sauvegarde les données des réservations dans le fichier JSON.
    Prend une liste d'objets Reservation.
    """
    reservations_data = [res.to_dict() for res in reservations]
    save_data(RESERVATION_FILE, reservations_data)

def creer_reservation(id_passager, id_annonce):
    """
    Crée une nouvelle réservation pour une annonce donnée.

    Args:
        id_passager (str): L'ID de l'utilisateur passager.
        id_annonce (str): L'ID de l'annonce de covoiturage.

    Returns:
        tuple: (True, Reservation) si la réservation est réussie, (False, str) sinon.
    """
    annonce = get_annonce_by_id(id_annonce)
    if not annonce:
        return False, "Annonce introuvable."

    if annonce.places_disponibles <= 0:
        return False, "Aucune place disponible sur cette annonce."

    # Créer la réservation
    # L'heure de départ et le statut initial sont tirés de l'annonce
    nouvelle_reservation = Reservation(
        id_automobiliste=annonce.id_automobiliste,
        id_passager=id_passager,
        heure_depart=annonce.heure_depart,
        statut="en_attente" # Statut initial de la réservation
    )

    reservations = charger_reservations()
    reservations.append(nouvelle_reservation)
    sauvegarder_reservations(reservations)

    # Mettre à jour le nombre de places disponibles dans l'annonce
    annonce.places_disponibles -= 1
    # Ajouter le passager à la liste des passagers réservés pour cette annonce
    annonce.passagers_reserves.append(id_passager)
    annonce.has_reservations = True # Marquer l'annonce comme ayant eu au moins une réservation
    update_annonce(annonce) # Utiliser update_annonce

    return True, nouvelle_reservation

def get_reservations_by_user(user_id, is_automobiliste=False):
    """
    Récupère les réservations associées à un utilisateur, soit en tant qu'automobiliste, soit en tant que passager.

    Args:
        user_id (str): L'ID de l'utilisateur.
        is_automobiliste (bool): True si l'utilisateur est un automobiliste, False s'il est un passager.

    Returns:
        list: Une liste d'objets Reservation.
    """
    reservations = charger_reservations()
    if is_automobiliste:
        return [res for res in reservations if res.id_automobiliste == user_id]
    else:
        return [res for res in reservations if res.id_passager == user_id]

def mettre_a_jour_statut_reservation(reservation_id, nouveau_statut):
    """
    Met à jour le statut d'une réservation.

    Args:
        reservation_id (str): L'ID de la réservation à mettre à jour.
        nouveau_statut (str): Le nouveau statut (ex: 'confirmee', 'annulee', 'terminee').

    Returns:
        bool: True si la mise à jour est réussie, False sinon.
    """
    reservations = charger_reservations()
    for i, res in enumerate(reservations):
        # Assurez-vous d'avoir un moyen d'identifier une réservation de manière unique, ex: un ID unique
        # Pour l'instant, nous allons utiliser une combinaison d'IDs pour l'exemple
        # Dans une vraie application, la classe Reservation devrait avoir un ID unique.
        # Ici, nous allons simuler la recherche par id_automobiliste et id_passager pour l'exemple.
        # Il faudra adapter cela une fois que la classe Reservation aura un ID unique.
        if str(res.id_automobiliste) + str(res.id_passager) == reservation_id: # Ceci est un un placeholder, à remplacer par un vrai ID
            reservations[i].statut = nouveau_statut
            sauvegarder_reservations(reservations)
            return True
    return False


