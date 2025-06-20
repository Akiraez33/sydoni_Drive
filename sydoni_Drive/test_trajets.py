from backend.trajets import publier_trajet, reserver_trajet, noter_trajet, terminer_trajet, load_trajets

#1. Publier un trajet 
res, msg = publier_trajet("auteur@example.com","Université A","Université B","2025-05-30 08:00",3)
print("Publication :", msg)

#2. Réserver une place
res , msg =reserver_trajet(0,"passager1@example.com")
print("Réservation :",msg)

#3. Ajouter une note de 4 étoiles
res, msg = noter_trajet(0,4)
print("Note:", msg)


#4. Terminer le trajet
res, msg = terminer_trajet(0)
print("Fin de trajet :",msg)

#5. Afficher le trajet avec ses points
trajets = load_trajets()
print("Trajet final enregistré:", trajets[0])

