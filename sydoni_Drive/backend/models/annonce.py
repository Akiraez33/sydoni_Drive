import json
import uuid
from datetime import datetime # Importation de datetime
from stockage import load_annonces, save_annonces # Importation des fonctions génériques de stockage

class Annonce:
    """
    Représente une annonce de covoiturage publiée par un automobiliste.
    Cette classe modélise les données d'une offre de trajet.
    """
    def __init__(self, id_automobiliste, universite_destination, heure_depart, places_offertes, engin, 
                 id_annonce=None, statut='active', passagers_reserves=None, position_depart=None, date_publication=None, has_reservations=False):
        """
        Initialise une nouvelle instance d'Annonce.

        Args:
            id_automobiliste (str): L'identifiant (email) de l'automobiliste.
            universite_destination (str): Le nom de l'université de destination.
            heure_depart (str): L'heure de départ prévue du trajet (ex: "HH:MM").
            places_offertes (int): Le nombre total de places offertes par l'automobiliste.
            engin (str): Le type de véhicule de l'automobiliste (ex: "moto", "voiture", "vélo").
            id_annonce (str, optional): L'identifiant unique de l'annonce. Généré si None. Defaults to None.
            statut (str, optional): Le statut de l'annonce (ex: 'active', 'complete', 'annulee'). Defaults to 'active'.
            passagers_reserves (list, optional): Liste des identifiants des passagers ayant réservé. Defaults to None.
            position_depart (dict, optional): Dictionnaire contenant la latitude et longitude du point de départ de l'automobiliste. Defaults to None.
            date_publication (str, optional): La date et l'heure de publication de l'annonce au format ISO. Defaults to None.
            has_reservations (bool, optional): Indique si l'annonce a eu au moins une réservation. Defaults to False.
        """
        self.id_annonce = id_annonce if id_annonce else str(uuid.uuid4()) # Générer un ID unique si non fourni
        self.id_automobiliste = id_automobiliste
        self.universite_destination = universite_destination
        self.heure_depart = heure_depart
        self.places_offertes = places_offertes
        self.places_disponibles = places_offertes # Au début, places disponibles = places offertes
        self.engin = engin
        self.statut = statut 
        self.passagers_reserves = passagers_reserves if passagers_reserves is not None else [] # S'assurer que c'est une liste
        self.position_depart = position_depart # Ajout de la position de départ à l'annonce
        # Enregistrer la date et l'heure de publication au format ISO pour faciliter la comparaison
        self.date_publication = date_publication if date_publication else datetime.now().isoformat()
        self.has_reservations = has_reservations # Ajout du flag pour les réservations

    def to_dict(self):
        """
        Convertit l'objet Annonce en un dictionnaire pour la sérialisation JSON.
        """
        return {
            "id_annonce": self.id_annonce,
            "id_automobiliste": self.id_automobiliste,
            "universite_destination": self.universite_destination,
            "heure_depart": self.heure_depart,
            "places_offertes": self.places_offertes,
            "places_disponibles": self.places_disponibles,
            "engin": self.engin,
            "statut": self.statut,
            "passagers_reserves": self.passagers_reserves,
            "position_depart": self.position_depart,
            "date_publication": self.date_publication,
            "has_reservations": self.has_reservations # Ajout de la date de publication
        }

    @classmethod
    def from_dict(cls, data):
        """
        Crée un objet Annonce à partir d'un dictionnaire (désérialisation JSON).
        """
        annonce = cls(
            data["id_automobiliste"],
            data["universite_destination"],
            data["heure_depart"],
            data["places_offertes"],
            data["engin"],
            data.get("id_annonce"),
            data.get("statut", 'active'),
            data.get("passagers_reserves"),
            data.get("position_depart"),
            data.get("date_publication"),
            data.get("has_reservations", False) # Charger le flag has_reservations
        )
        # Assurer que places_disponibles est correctement chargé ou réinitialisé
        annonce.places_disponibles = data.get("places_disponibles", data["places_offertes"])
        return annonce

# --- Fonctions de gestion des annonces (CRUD) ---

def get_all_annonces():
    """
    Charge toutes les annonces depuis le fichier de stockage.
    Returns une liste d'objets Annonce.
    """
    annonces_data = load_annonces()
    return [Annonce.from_dict(data) for data in annonces_data]

def save_all_annonces(annonces):
    """
    Sauvegarde une liste d'objets Annonce dans le fichier de stockage.
    """
    annonces_data = [annonce.to_dict() for annonce in annonces]
    save_annonces(annonces_data)

def add_annonce(annonce: Annonce):
    """
    Ajoute une nouvelle annonce au système.
    """
    annonces = get_all_annonces()
    annonces.append(annonce)
    save_all_annonces(annonces)

def get_annonce_by_id(annonce_id: str):
    """
    Récupère une annonce par son identifiant unique.
    """
    annonces = get_all_annonces()
    for annonce in annonces:
        if annonce.id_annonce == annonce_id:
            return annonce
    return None

def update_annonce(updated_annonce: Annonce):
    """
    Met à jour une annonce existante.
    """
    annonces = get_all_annonces()
    for i, annonce in enumerate(annonces):
        if annonce.id_annonce == updated_annonce.id_annonce:
            annonces[i] = updated_annonce
            save_all_annonces(annonces)
            return True
    return False

def delete_annonce(annonce_id: str):
    """
    Supprime une annonce par son identifiant unique.
    """
    annonces = get_all_annonces()
    initial_len = len(annonces)
    annonces = [annonce for annonce in annonces if annonce.id_annonce != annonce_id]
    if len(annonces) < initial_len:
        save_all_annonces(annonces)
        return True
    return False

def get_active_annonces():
    """
    Récupère toutes les annonces actives (statut 'active').
    """
    annonces = get_all_annonces()
    return [annonce for annonce in annonces if annonce.statut == 'active']


