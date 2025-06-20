from math import radians, sin, cos, sqrt, atan2

def calculer_distance_km(lat1, lon1, lat2, lon2):
    """
    Calcule la distance en kilomètres entre deux points géographiques
    (donnés par leurs latitudes et longitudes) en utilisant la formule de Haversine.

    Args:
        lat1 (float): Latitude du premier point en degrés.
        lon1 (float): Longitude du premier point en degrés.
        lat2 (float): Latitude du deuxième point en degrés.
        lon2 (float): Longitude du deuxième point en degrés.

    Returns:
        float: La distance entre les deux points en kilomètres.
    """
    # Rayon moyen de la Terre en kilomètres
    R = 6371.0

    # Conversion des coordonnées de degrés en radians
    lat1_rad, lon1_rad = radians(lat1), radians(lon1)
    lat2_rad, lon2_rad = radians(lat2), radians(lon2)

    # Différences de latitude et de longitude
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Formule de Haversine
    # a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    # c = 2 * atan2(√a, √(1-a))
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Distance = R * c
    distance = R * c
    return distance



