import json

class User:
    def __init__(self, nom, prenom, email, telephone, universite, role, engin=None, places_disponibles=None):
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.telephone = telephone
        self.universite = universite
        self.role = role
        self.engin = engin
        self.places_disponibles = places_disponibles
        self.points = 0  # Initialisation des points à 0
        self.historique_trajets = []

    def to_dict(self):
        return {
            "nom": self.nom,
            "prenom": self.prenom,
            "email": self.email,
            "telephone": self.telephone,
            "universite": self.universite,
            "role": self.role,
            "engin": self.engin,
            "places_disponibles": self.places_disponibles,
            "points": self.points,
            "historique_trajets": self.historique_trajets
        }

    @classmethod
    def from_dict(cls, data):
        user = cls(
            data["nom"],
            data["prenom"],
            data["email"],
            data["telephone"],
            data["universite"],
            data["role"],
            data.get("engin"),
            data.get("places_disponibles"), # Assurer que places_disponibles est chargé
        )
        user.points = data.get("points", 0) # Assurer que les points sont chargés
        user.historique_trajets = data.get("historique_trajets", []) # Assurer que l'historique est chargé
        return user


   