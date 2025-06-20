import unittest
import os
import shutil
from datetime import datetime, timedelta

# Ajuster le chemin pour les imports du backend
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.users import register_user, login_user, get_user_by_email, update_user_role, update_user_points
from backend.trajets import publier_trajet, reserver_trajet, noter_trajet, get_historique_utilisateur, get_annonces_disponibles, terminer_trajet
from backend.models.annonce import get_all_annonces, delete_annonce
from stockage import clear_all_data

class TestBackend(unittest.TestCase):

    def setUp(self):
        """
        Préparer l'environnement de test avant chaque test.
        Supprime les fichiers de données existants pour assurer un état propre.
        """
        clear_all_data() # Nettoie tous les fichiers de données

    def tearDown(self):
        """
        Nettoyer après chaque test.
        """
        clear_all_data() # Nettoie tous les fichiers de données

    def test_user_registration_and_login(self):
        """
        Teste l'enregistrement et la connexion d'un utilisateur.
        """
        success, message = register_user("John", "Doe", "123456789", "john.doe@example.com", "Université A", "passager")
        self.assertTrue(success, message)
        self.assertEqual(message, "Utilisateur enregistré avec succès.")

        success, user, message, role = login_user("john.doe@example.com")
        self.assertTrue(success, message)
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "john.doe@example.com")
        self.assertEqual(role, "passager")

        # Teste l'enregistrement d'un utilisateur existant
        success, message = register_user("John", "Doe", "123456789", "john.doe@example.com", "Université A", "passager")
        self.assertFalse(success)
        self.assertEqual(message, "Un compte avec cet email existe déjà.")

        # Teste la connexion avec un email incorrect
        success, user, message, role = login_user("wrong.email@example.com")
        self.assertFalse(success)
        self.assertIsNone(user)
        self.assertEqual(message, "Email ou mot de passe incorrect.")

    def test_automobiliste_registration(self):
        """
        Teste l'enregistrement d'un automobiliste avec engin et places disponibles.
        """
        success, message = register_user("Jane", "Doe", "987654321", "jane.doe@example.com", "Université B", "automobiliste", engin="voiture", places_disponibles=3)
        self.assertTrue(success, message)
        self.assertEqual(message, "Utilisateur enregistré avec succès.")

        user = get_user_by_email("jane.doe@example.com")
        self.assertIsNotNone(user)
        self.assertEqual(user.role, "automobiliste")
        self.assertEqual(user.engin, "voiture")
        self.assertEqual(user.places_disponibles, 3)

    def test_update_user_role(self):
        """
        Teste la mise à jour du rôle d'un utilisateur.
        """
        register_user("Test", "User", "111222333", "test.user@example.com", "Université C", "passager")
        success, message = update_user_role("test.user@example.com", "automobiliste")
        self.assertTrue(success, message)
        self.assertEqual(message, "Rôle mis à jour avec succès.")

        user = get_user_by_email("test.user@example.com")
        self.assertEqual(user.role, "automobiliste")

    def test_update_user_points(self):
        """
        Teste la mise à jour des points d'un utilisateur.
        """
        register_user("Point", "User", "444555666", "point.user@example.com", "Université A", "automobiliste")
        user = get_user_by_email("point.user@example.com")
        self.assertEqual(user.points, 0)

        success, message = update_user_points("point.user@example.com", 10)
        self.assertTrue(success, message)

        user = get_user_by_email("point.user@example.com")
        self.assertEqual(user.points, 10)

        success, message = update_user_points("point.user@example.com", -5)
        self.assertTrue(success, message)

        user = get_user_by_email("point.user@example.com")
        self.assertEqual(user.points, 5)

    def test_publier_trajet(self):
        """
        Teste la publication d'un trajet par un automobiliste.
        """
        register_user("Auto", "Mobile", "123123123", "auto@example.com", "Université A", "automobiliste", engin="moto", places_disponibles=1)
        
        # Définir une heure de départ dans le futur pour le test
        heure_depart = (datetime.now() + timedelta(minutes=30)).strftime("%H:%M")
        
        success, message, annonce_id = publier_trajet("auto@example.com", "Université A", heure_depart, 1, 48.8566, 2.3522)
        self.assertTrue(success, message)
        self.assertIsNotNone(annonce_id)

        annonces = get_all_annonces()
        self.assertEqual(len(annonces), 1)
        self.assertEqual(annonces[0].id_automobiliste, "auto@example.com")
        self.assertEqual(annonces[0].universite_destination, "Université A")
        self.assertEqual(annonces[0].places_offertes, 1)
        self.assertEqual(annonces[0].places_disponibles, 1)

    def test_reserver_trajet(self):
        """
        Teste la réservation d'un trajet par un passager.
        """
        register_user("Auto", "Mobile", "123123123", "auto@example.com", "Université A", "automobiliste", engin="voiture", places_disponibles=2)
        register_user("Passager", "Un", "999888777", "passager1@example.com", "Université A", "passager")

        heure_depart = (datetime.now() + timedelta(minutes=30)).strftime("%H:%M")
        success, msg, annonce_id = publier_trajet("auto@example.com", "Université A", heure_depart, 2, 48.8566, 2.3522)
        self.assertTrue(success, msg)
        self.assertIsNotNone(annonce_id)

        # Récupérer l'annonce publiée pour s'assurer qu'elle existe
        annonces_disponibles = get_annonces_disponibles()
        self.assertEqual(len(annonces_disponibles), 1)
        annonce = annonces_disponibles[0]

        success, message = reserver_trajet(annonce.id_annonce, "passager1@example.com", 48.8570, 2.3530)
        self.assertTrue(success, message)
        self.assertEqual(message, "Réservation effectuée avec succès.")

        # Vérifier que les places disponibles ont diminué
        annonce_apres_res = get_annonces_disponibles()[0] # Recharger l'annonce
        self.assertEqual(annonce_apres_res.places_disponibles, 1)
        self.assertIn("passager1@example.com", annonce_apres_res.passagers_reserves)

        # Tenter de réserver à nouveau (devrait échouer)
        success, message = reserver_trajet(annonce.id_annonce, "passager1@example.com", 48.8570, 2.3530)
        self.assertFalse(success)
        self.assertEqual(message, "Vous avez déjà réservé ce trajet.")

        # Tenter de réserver une annonce sans places
        register_user("Passager", "Deux", "111222333", "passager2@example.com", "Université A", "passager")
        success, message = reserver_trajet(annonce.id_annonce, "passager2@example.com", 48.8570, 2.3530)
        self.assertTrue(success, message) # Une place restante, donc ça devrait marcher

        # Après cette réservation, places_disponibles devrait être 0, donc get_annonces_disponibles() devrait retourner une liste vide
        annonces_apres_tout_reserve = get_annonces_disponibles()
        self.assertEqual(len(annonces_apres_tout_reserve), 0) # Assert that no announcements are available

        register_user("Passager", "Trois", "444555666", "passager3@example.com", "Université A", "passager")
        success, message = reserver_trajet(annonce.id_annonce, "passager3@example.com", 48.8570, 2.3530)
        self.assertFalse(success)
        self.assertEqual(message, "Plus de places disponibles sur cette annonce.")

    def test_noter_trajet(self):
        """
        Teste la notation d'un trajet par un passager.
        """
        register_user("Auto", "Note", "123456789", "auto.note@example.com", "Université A", "automobiliste", engin="voiture", places_disponibles=1)
        register_user("Passager", "Note", "987654321", "passager.note@example.com", "Université A", "passager")

        heure_depart = (datetime.now() + timedelta(minutes=30)).strftime("%H:%M")
        success, msg, annonce_id = publier_trajet("auto.note@example.com", "Université A", heure_depart, 1, 48.8566, 2.3522)
        self.assertTrue(success, msg)

        reserver_trajet(annonce_id, "passager.note@example.com", 48.8570, 2.3530)
        
        # Terminer le trajet avant de le noter
        success, message = terminer_trajet(annonce_id)
        self.assertTrue(success, message)

        # Noter le trajet
        success, message = noter_trajet(annonce_id, "passager.note@example.com", 5)
        self.assertTrue(success, f"Échec de la notation: {message}")
        self.assertEqual(message, "Trajet noté avec succès. L'automobiliste a gagné 10 points.")

        # Vérifier les points de l'automobiliste
        automobiliste = get_user_by_email("auto.note@example.com")
        # Les points devraient être 10 (pour avoir conduit le passager) + 10 (pour la note de 5 étoiles)
        # La logique de 5 points pour publication sans réservation est gérée dans terminer_trajet
        # Si un passager a réservé, les 5 points ne sont pas attribués.
        # Donc, si un passager a réservé et a été conduit, l'automobiliste gagne 10 points pour le trajet + points de la note.
        # Ici, on a 10 points pour le trajet + 10 points pour la note = 20 points.
        self.assertEqual(automobiliste.points, 20)

        # Tenter de noter à nouveau (devrait échouer)
        success, message = noter_trajet(annonce_id, "passager.note@example.com", 3)
        self.assertFalse(success)
        self.assertEqual(message, "Vous avez déjà noté ce trajet.")

    def test_get_historique_utilisateur(self):
        """
        Teste la récupération de l'historique des trajets d'un utilisateur.
        """
        register_user("Auto", "Hist", "123456789", "auto.hist@example.com", "Université A", "automobiliste", engin="voiture", places_disponibles=1)
        register_user("Passager", "Hist", "987654321", "passager.hist@example.com", "Université A", "passager")

        heure_depart = (datetime.now() + timedelta(minutes=30)).strftime("%H:%M")
        success, msg, annonce_id = publier_trajet("auto.hist@example.com", "Université A", heure_depart, 1, 48.8566, 2.3522)
        self.assertTrue(success, msg)

        reserver_trajet(annonce_id, "passager.hist@example.com", 48.8570, 2.3530)

        historique_auto = get_historique_utilisateur("auto.hist@example.com")
        self.assertEqual(len(historique_auto), 1)
        self.assertEqual(historique_auto[0]["role"], "automobiliste")
        self.assertEqual(historique_auto[0]["id"], annonce_id)

        historique_passager = get_historique_utilisateur("passager.hist@example.com")
        self.assertEqual(len(historique_passager), 1)
        self.assertEqual(historique_passager[0]["role"], "passager")
        self.assertEqual(historique_passager[0]["id"], annonce_id)

    def test_get_annonces_disponibles(self):
        """
        Teste la récupération des annonces disponibles.
        """
        register_user("Auto", "Dispo", "123456789", "auto.dispo@example.com", "Université A", "automobiliste", engin="voiture", places_disponibles=1)
        
        heure_depart_future = (datetime.now() + timedelta(minutes=30)).strftime("%H:%M")
        publier_trajet("auto.dispo@example.com", "Université A", heure_depart_future, 1, 48.8566, 2.3522)

        annonces = get_annonces_disponibles()
        self.assertEqual(len(annonces), 1)
        self.assertEqual(annonces[0].id_automobiliste, "auto.dispo@example.com")

        # Tester avec une annonce passée
        heure_depart_passee = (datetime.now() - timedelta(minutes=30)).strftime("%H:%M")
        publier_trajet("auto.dispo@example.com", "Université B", heure_depart_passee, 1, 48.8566, 2.3522)
        annonces_apres = get_annonces_disponibles()
        self.assertEqual(len(annonces_apres), 1) # Seule l'annonce future devrait être là

if __name__ == '__main__':
    unittest.main()


