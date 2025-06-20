import json
import os
from datetime import datetime, timedelta
from backend.distance import calculer_distance_km
from backend.universites import get_coordonnees_universite
from backend.users import get_user_by_email, update_user_points
from backend.models.annonce import Annonce, get_all_annonces, add_annonce, update_annonce, delete_annonce, get_annonce_by_id
from stockage import load_historiques, save_historiques

# Constantes pour les états de trajet
EN_ATTENTE = "en_attente"
EN_COURS = "en_cours"
TERMINE = "termine"
ANNULE = "annule"

# --- Fonctions de gestion de l\"historique utilisateur (agrégé) ---


# --- Fonctions de gestion des trajets (basées sur les Annonces) ---

def publier_trajet(email_automobiliste, universite, heure_depart_str, places_disponibles, latitude_depart, longitude_depart):
    """
    Permet à un automobiliste de publier une nouvelle annonce de trajet.
    Cette fonction crée une nouvelle instance de la classe Annonce et la sauvegarde.

    Args:
        email_automobiliste (str): L\"email de l\"automobiliste qui publie le trajet.
        universite (str): Le nom de l\"université de destination.
        heure_depart_str (str): L\"heure de départ prévue du trajet au format "HH:MM".
        places_disponibles (int): Le nombre de places offertes par l\"automobiliste.
        latitude_depart (float): Latitude du point de départ de l\"automobiliste.
        longitude_depart (float): Longitude du point de départ de l\"automobiliste.

    Returns:
        tuple: (bool, str, str) - True si la publication est réussie, False sinon, avec un message et l\"ID de l\"annonce.
    """
    try:
        # Récupérer l\"utilisateur pour obtenir le type d\"engin
        automobiliste = get_user_by_email(email_automobiliste)
        if not automobiliste or automobiliste.role != "automobiliste":
            return False, "Seul un automobiliste peut publier un trajet.", None

        # Création de l\"objet Annonce
        nouvelle_annonce = Annonce(
            id_automobiliste=email_automobiliste,
            universite_destination=universite,
            heure_depart=heure_depart_str,
            places_offertes=places_disponibles,
            engin=automobiliste.engin, # Récupérer l\"engin de l\"automobiliste
            position_depart={"latitude": latitude_depart, "longitude": longitude_depart},
            statut=EN_ATTENTE # Définir explicitement le statut à EN_ATTENTE
        )
        add_annonce(nouvelle_annonce)

        # Attribution des 5 points si l\"annonce est publiée au moins 20 minutes avant le départ
        # et qu\"elle n\"a pas eu de réservations (vérifié plus tard lors de la terminaison ou annulation)
        # Pour l\"instant, on ne donne pas les points ici, car la condition
        return True, "Annonce publiée avec succès.", nouvelle_annonce.id_annonce
    except Exception as e:
        return False, f"Erreur lors de la publication de l\"annonce: {e}", None

def reserver_trajet(annonce_id, email_passager, lat_passager, lon_passager):
    """
    Permet à un passager de réserver une place sur une annonce de trajet.

    Args:
        annonce_id (str): L\"ID de l\"annonce à réserver.
        email_passager (str): L\"email du passager qui réserve.
        lat_passager (float): Latitude actuelle du passager.
        lon_passager (float): Longitude actuelle du passager.

    Returns:
        tuple: (bool, str) - True si la réservation est réussie, False sinon, avec un message.
    """
    annonce = get_annonce_by_id(annonce_id)
    if not annonce:
        return False, "Annonce non trouvée."

    if annonce.places_disponibles <= 0:
        return False, "Plus de places disponibles sur cette annonce."

    # Vérifier si le passager a déjà réservé cette annonce
    if email_passager in annonce.passagers_reserves:
        return False, "Vous avez déjà réservé ce trajet."

    # Mettre à jour l\"annonce
    annonce.places_disponibles -= 1
    annonce.passagers_reserves.append(email_passager)
    annonce.has_reservations = True # Marquer l\"annonce comme ayant eu au moins une réservation
    update_annonce(annonce)

    # Enregistrer la réservation dans l\"historique du passager
    historiques = load_historiques()
    if email_passager not in historiques:
        historiques[email_passager] = {}
    
    # Ajouter le trajet à l\"historique du passager
    historiques[email_passager][annonce.id_annonce] = {
        "id": annonce.id_annonce,
        "role": "passager",
        "universite": annonce.universite_destination,
        "heure_depart": annonce.heure_depart,
        "etat": EN_ATTENTE, # Le trajet est en attente de confirmation par l\"automobiliste
        "points": 0, # Les passagers ne gagnent pas de points
        "notes_moyenne": "N/A",
        "automobiliste_email": annonce.id_automobiliste,
        "position_passager": {"latitude": lat_passager, "longitude": lon_passager}
    }
    save_historiques(historiques)

    # Mettre à jour l\"historique de l\"automobiliste pour refléter la réservation
    historiques_automobiliste = load_historiques()
    if annonce.id_automobiliste not in historiques_automobiliste:
        historiques_automobiliste[annonce.id_automobiliste] = {}
    
    # Trouver l\"annonce correspondante dans l\"historique de l\"automobiliste et la mettre à jour
    # Si l\"annonce n\"est pas encore dans l\"historique de l\"automobiliste (ce qui ne devrait pas arriver si publier_trajet l\"ajoute)
    # Nous allons la créer ou la mettre à jour.
    historiques_automobiliste[annonce.id_automobiliste][annonce.id_annonce] = {
        "id": annonce.id_annonce,
        "role": "automobiliste",
        "universite": annonce.universite_destination,
        "heure_depart": annonce.heure_depart,
        "etat": EN_ATTENTE,
        "places_offertes": annonce.places_offertes,
        "places_disponibles": annonce.places_disponibles,
        "passagers_reserves": annonce.passagers_reserves,
        "has_reservations": annonce.has_reservations,
        "points": 0, # Les points seront attribués à la fin du trajet
        "notes_moyenne": "N/A",
        "position_depart": annonce.position_depart
    }

    save_historiques(historiques_automobiliste)

    return True, "Réservation effectuée avec succès."

def terminer_trajet(trajet_id):
    """
    Marque un trajet comme terminé et attribue les points à l\"automobiliste.

    Args:
        trajet_id (str): L\"ID du trajet à terminer.

    Returns:
        tuple: (bool, str) - True si le trajet est terminé avec succès, False sinon.
    """
    annonce = get_annonce_by_id(trajet_id)
    if not annonce:
        return False, "Trajet non trouvé."

    if annonce.statut == TERMINE:
        return False, "Ce trajet est déjà terminé."

    # Mettre à jour le statut de l\"annonce
    annonce.statut = TERMINE
    update_annonce(annonce)

    # Attribution des points à l\"automobiliste
    points_gagnes = 0
    message_points = []

    # 1. Points pour la publication (5 points si aucune réservation et publié 20min avant)
    # Cette logique est déplacée ici car on a besoin de savoir s\"il y a eu des réservations
    # et de comparer l\"heure de publication avec l\"heure de départ réelle (ou l\"heure actuelle si le trajet est terminé)
    # On doit s\"assurer que la date_publication est bien un objet datetime pour la comparaison
    date_publication_dt = datetime.fromisoformat(annonce.date_publication)
    heure_depart_dt = datetime.strptime(annonce.heure_depart, "%H:%M").replace(year=date_publication_dt.year, month=date_publication_dt.month, day=date_publication_dt.day)

    # Si l\"heure de départ est déjà passée par rapport à l\"heure actuelle, on utilise l\"heure actuelle pour le calcul
    if heure_depart_dt < datetime.now():
        heure_depart_dt = datetime.now()

    if not annonce.has_reservations and (heure_depart_dt - date_publication_dt).total_seconds() >= (20 * 60):
        points_gagnes += 5
        message_points.append("5 points pour publication sans réservation et à temps.")

    # 2. Points si un passager a été sélectionné et rejoint (10 points au lieu de 5)
    # Cette logique est déjà couverte par la condition ci-dessus. Si has_reservations est True, on ne donne pas les 5 points.
    # Si un passager a été réservé, les points sont gérés différemment.

    # 3. Points pour l\"arrivée à destination (10 points par passager conduit à destination)
    # On attribue 10 points par passager qui a effectivement réservé et a été conduit.
    # Pour simplifier, on considère que tous les passagers réservés ont été conduits à destination.
    if annonce.passagers_reserves:
        points_gagnes += len(annonce.passagers_reserves) * 10
        message_points.append(f"{len(annonce.passagers_reserves) * 10} points pour avoir conduit des passagers.")

    # Mettre à jour les points de l\"automobiliste
    if points_gagnes > 0:
        update_user_points(annonce.id_automobiliste, points_gagnes)

    # Mettre à jour l\"historique de l\"automobiliste et des passagers
    historiques = load_historiques()
    
    # Pour l\"automobiliste
    if annonce.id_automobiliste in historiques and annonce.id_annonce in historiques[annonce.id_automobiliste]:
        historiques[annonce.id_automobiliste][annonce.id_annonce]["etat"] = TERMINE
        historiques[annonce.id_automobiliste][annonce.id_annonce]["points"] += points_gagnes # Ajouter les points gagnés
    
    # Pour les passagers réservés
    for passager_email in annonce.passagers_reserves:
        if passager_email in historiques and annonce.id_annonce in historiques[passager_email]:
            historiques[passager_email][annonce.id_annonce]["etat"] = TERMINE
    save_historiques(historiques)

    message_combined = ". ".join(message_points)
    return True, f"Trajet terminé avec succès. {message_combined}"

def noter_trajet(trajet_id, email_passager, note):
    """
    Permet à un passager de noter un trajet terminé.

    Args:
        trajet_id (str): L\"ID du trajet à noter.
        email_passager (str): L\"email du passager qui note.
        note (int): La note attribuée (entre 0 et 5).

    Returns:
        tuple: (bool, str) - True si la notation est réussie, False sinon.
    """
    annonce = get_annonce_by_id(trajet_id)
    if not annonce:
        return False, "Trajet non trouvé."

    if annonce.statut != TERMINE:
        return False, "Ce trajet n\"est pas encore terminé et ne peut pas être noté."

    if email_passager not in annonce.passagers_reserves:
        return False, "Vous ne pouvez noter que les trajets que vous avez réservés."

    # Vérifier si le passager a déjà noté ce trajet (pour éviter les notes multiples)
    historiques = load_historiques()
    if email_passager in historiques and trajet_id in historiques[email_passager]:
        if "note_donnee" in historiques[email_passager][trajet_id] and historiques[email_passager][trajet_id]["note_donnee"]:
            return False, "Vous avez déjà noté ce trajet."

    # Attribution des points à l\"automobiliste en fonction de la note
    points_note = note * 2
    update_user_points(annonce.id_automobiliste, points_note)

    # Mettre à jour l\"historique du passager pour marquer la note donnée
    if email_passager in historiques and trajet_id in historiques[email_passager]:
        historiques[email_passager][trajet_id]["note_donnee"] = True # Marquer que la note a été donnée
    save_historiques(historiques)

    # Mettre à jour la note moyenne de l\"automobiliste pour ce trajet (dans l\"historique de l\"automobiliste)
    # Pour une implémentation plus robuste, il faudrait stocker toutes les notes et calculer la moyenne.
    # Pour l\"instant, nous allons simplement mettre à jour la note moyenne dans l\"historique de l\"automobiliste.
    if annonce.id_automobiliste in historiques and trajet_id in historiques[annonce.id_automobiliste]:
        # Pour simplifier, on met à jour la note moyenne directement avec la dernière note reçue.
        # Dans une vraie application, il faudrait calculer une moyenne pondérée de toutes les notes.
        historiques[annonce.id_automobiliste][trajet_id]["notes_moyenne"] = note
    save_historiques(historiques)

    return True, f"Trajet noté avec succès. L\'automobiliste a gagné {points_note} points."

def get_annonces_disponibles():
    """
    Récupère toutes les annonces actives qui ont encore des places disponibles.

    Returns:
        list: Une liste d\"objets Annonce disponibles.
    """
    annonces = get_all_annonces()
    # Filtrer les annonces pour ne garder que celles qui sont actives et ont des places disponibles
    # et dont l\"heure de départ n\"est pas passée
    annonces_filtrees = []
    now = datetime.now()
    for annonce in annonces:
        try:
            # Combiner la date d\"aujourd\"hui avec l\"heure de départ de l\"annonce
            # Assurez-vous que l\"année, le mois et le jour sont corrects pour la comparaison
            heure_depart_dt = datetime.strptime(annonce.heure_depart, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
            
            # Réactiver la condition de temps
            if annonce.statut == EN_ATTENTE and annonce.places_disponibles > 0 and heure_depart_dt > now:
                annonces_filtrees.append(annonce)
        except ValueError: # Gérer les erreurs si le format de l\"heure est incorrect
            print(f"Erreur de format d\"heure pour l\"annonce {annonce.id_annonce}: {annonce.heure_depart}")
            continue
    return annonces_filtrees

def get_historique_utilisateur(email):
    """
    Récupère l\"historique complet des trajets pour un utilisateur donné.

    Args:
        email (str): L\"email de l\"utilisateur.

    Returns:
        list: Une liste de dictionnaires représentant les trajets de l\"utilisateur.
    """
    historiques = load_historiques()
    # Retourne une liste des valeurs du dictionnaire, car chaque trajet est stocké avec son ID comme clé
    return list(historiques.get(email, {}).values())


