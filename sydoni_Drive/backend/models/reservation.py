import json
import uuid # Importation du module uuid pour générer des identifiants uniques

class Reservation:
    """
    Représente une réservation de trajet effectuée par un passager.
    """
    def __init__(self, id_automobiliste, id_passager, heure_depart, statut, id_reservation=None, points_attribues=0):
        """
        Initialise une nouvelle instance de réservation.

        Args:
            id_automobiliste (str): L'identifiant (email) de l'automobiliste.
            id_passager (str): L'identifiant (email) du passager.
            heure_depart (str): L'heure de départ prévue du trajet (ex: "HH:MM").
            statut (str): Le statut de la réservation (ex: 'en_attente', 'confirmee', 'annulee', 'terminee').
            id_reservation (str, optional): L'identifiant unique de la réservation. Généré si None.
            points_attribues (int, optional): Points attribués à l'automobiliste pour cette réservation. Defaults to 0.
        """
        self.id_reservation = id_reservation if id_reservation else str(uuid.uuid4()) # Générer un ID unique
        self.id_automobiliste = id_automobiliste
        self.id_passager = id_passager
        self.heure_depart = heure_depart
        self.statut = statut  
        self.points_attribues = points_attribues

    def to_dict(self):
        """
        Convertit l'objet Reservation en un dictionnaire pour la sérialisation JSON.
        """
        return {
            "id_reservation": self.id_reservation,
            "id_automobiliste": self.id_automobiliste,
            "id_passager": self.id_passager,
            "heure_depart": self.heure_depart,
            "statut": self.statut,
            "points_attribues": self.points_attribues
        }

    @classmethod
    def from_dict(cls, data):
        """
        Crée un objet Reservation à partir d'un dictionnaire (désérialisation JSON).
        """
        return cls(
            data["id_automobiliste"],
            data["id_passager"],
            data["heure_depart"],
            data["statut"],
            data.get("id_reservation"), # Récupérer l'ID si présent
            data.get("points_attribues", 0)
        )


