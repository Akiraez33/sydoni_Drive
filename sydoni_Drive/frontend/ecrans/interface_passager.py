import tkinter as tk
from tkinter import ttk, messagebox
from backend.trajets import get_annonces_disponibles, reserver_trajet, noter_trajet, get_historique_utilisateur
from backend.universites import charger_universites, get_coordonnees_universite
from backend.users import get_user_by_email, update_user_role
from backend.distance import calculer_distance_km
from backend.geolocalisation import get_current_location # Pour obtenir la position du passager
from frontend.ecrans.map_display import MapDisplayFrame # Importation du module d'affichage de la carte

class InterfacePassagerFrame(tk.Frame):
    """
    Cadre (Frame) de l'interface pour les passagers.
    Permet de rechercher et réserver des trajets, noter des automobilistes, voir l'historique, etc.
    """
    def __init__(self, parent, controller):
        """
        Initialise le cadre de l'interface passager.

        Args:
            parent (tk.Tk ou tk.Frame): Le widget parent (généralement la fenêtre principale de l'application).
            controller (object): L'objet contrôleur (SydoniDriveApp) pour la navigation entre les pages.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.user_email = None # L'email de l'utilisateur sera défini via set_user_email
        self.user = None # L'objet User sera chargé via set_user_email
        self.passager_lat = None # Latitude actuelle du passager
        self.passager_lon = None # Longitude actuelle du passager

        # Charger la liste des universités disponibles depuis le backend
        self.universites = [univ["nom"] for univ in charger_universites()]

        # Onglets pour organiser l'interface
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # --- Onglet "Rechercher un trajet" ---
        self.recherche_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.recherche_frame, text="Rechercher un trajet")
        self.create_recherche_tab(self.recherche_frame)

        # --- Onglet "Carte du trajet" ---
        self.map_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.map_frame, text="Carte du trajet")
        self.map_display = MapDisplayFrame(self.map_frame, self.controller) # Instancier la carte
        self.map_display.pack(fill="both", expand=True)

        # --- Onglet "Mes réservations" ---
        self.reservations_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reservations_frame, text="Mes réservations")
        self.create_reservations_tab(self.reservations_frame)

        # --- Onglet "Historique des trajets" ---
        self.historique_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.historique_frame, text="Historique des trajets")
        self.create_historique_tab(self.historique_frame)

        # --- Onglet "Paramètres" ---
        self.parametres_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.parametres_frame, text="Paramètres")
        self.create_parametres_tab(self.parametres_frame)

        # Bouton de déconnexion
        ttk.Button(self, text="Déconnexion", command=self.logout).pack(pady=5)

    def set_user_email(self, email):
        """
        Définit l'email de l'utilisateur pour cette frame et charge ses informations.
        Cette méthode est appelée par le contrôleur (SydoniDriveApp) lors de la navigation.

        Args:
            email (str): L'email du passager connecté.
        """
        self.user_email = email
        self.user = get_user_by_email(email) # Charger l'objet User complet
        if not self.user:
            messagebox.showerror("Erreur", "Utilisateur non trouvé. Veuillez vous reconnecter.")
            self.controller.show_frame("LoginRegisterFrame")
            return
        
        # Tenter d'obtenir la position actuelle du passager
        # Pour la démo, si get_current_location() retourne None, utiliser des coordonnées par défaut
        current_loc = get_current_location()
        if current_loc:
            self.passager_lat, self.passager_lon = current_loc
        else:
            # Coordonnées par défaut si la géolocalisation échoue (à remplacer par une vraie gestion d'erreur/saisie)
            self.passager_lat = 12.3686 # Exemple de latitude
            self.passager_lon = -1.5334 # Exemple de longitude
            messagebox.showwarning("Géolocalisation", "Impossible d'obtenir votre position actuelle. Utilisation de coordonnées par défaut.")

    def create_recherche_tab(self, parent_frame):
        """
        Crée les widgets pour l'onglet "Rechercher un trajet".
        Permet au passager de rechercher des annonces de covoiturage.
        """
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.columnconfigure(1, weight=2)

        # Champ pour la sélection de l'université de destination
        ttk.Label(parent_frame, text="Université de destination:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.search_universite_var = tk.StringVar(parent_frame)
        self.search_universite_dropdown = ttk.Combobox(parent_frame, textvariable=self.search_universite_var, values=self.universites, state="readonly")
        self.search_universite_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        if self.universites:
            self.search_universite_dropdown.set(self.universites[0])

        # Bouton de recherche
        ttk.Button(parent_frame, text="Rechercher", command=self.search_rides).grid(row=1, column=0, columnspan=2, pady=10)

        # Liste des trajets trouvés
        self.rides_listbox = tk.Listbox(parent_frame, height=15, width=80)
        self.rides_listbox.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.rides_listbox.bind("<<ListboxSelect>>", self.on_ride_select)

        # Bouton de réservation (initialement désactivé)
        self.reserve_button = ttk.Button(parent_frame, text="Réserver le trajet sélectionné", command=self.handle_reservation, state=tk.DISABLED)
        self.reserve_button.grid(row=3, column=0, columnspan=2, pady=5)

        # Stockage des annonces disponibles pour faciliter la récupération lors de la sélection
        self.available_annonces = [] 

    def search_rides(self):
        """
        Recherche les annonces de trajets disponibles en fonction de l'université de destination
        et des critères de proximité (passager plus proche de l'université que l'automobiliste).
        """
        self.rides_listbox.delete(0, tk.END)
        self.available_annonces = [] # Réinitialiser la liste des annonces disponibles
        self.map_display.clear_all_markers_and_paths() # Effacer les éléments de la carte

        destination_universite = self.search_universite_var.get()
        if not destination_universite:
            messagebox.showwarning("Recherche", "Veuillez sélectionner une université de destination.")
            return

        # Récupérer les coordonnées de l'université de destination
        coords_univ = get_coordonnees_universite(destination_universite)
        if coords_univ is None:
            messagebox.showerror("Erreur", "Coordonnées de l'université de destination inconnues.")
            return
        latitude_univ, longitude_univ = coords_univ

        # Ajouter un marqueur pour la position du passager
        self.map_display.add_marker(self.passager_lat, self.passager_lon, text="Votre position")
        self.map_display.add_marker(latitude_univ, longitude_univ, text=destination_universite)
        self.map_display.set_map_center((self.passager_lat + latitude_univ) / 2, (self.passager_lon + longitude_univ) / 2, zoom=10)

        # Récupérer toutes les annonces disponibles
        all_annonces = get_annonces_disponibles()
        
        # Filtrer et évaluer les annonces
        for annonce in all_annonces:
            # Vérifier que l'annonce est pour la même université de destination
            if annonce.universite_destination.lower() != destination_universite.lower():
                continue

            # Vérifier s'il reste des places disponibles
            if annonce.places_disponibles <= 0:
                continue

            # Récupérer les coordonnées de départ de l'automobiliste pour cette annonce
            # Note: annonce.position_depart est un dictionnaire {latitude, longitude}
            lat_auto_depart = annonce.position_depart["latitude"]
            lon_auto_depart = annonce.position_depart["longitude"]

            # Calculer la distance du passager à l'université de destination
            distance_passager_univ = calculer_distance_km(self.passager_lat, self.passager_lon, latitude_univ, longitude_univ)
            
            # Calculer la distance de l'automobiliste (point de départ de l'annonce) à l'université de destination
            distance_automobiliste_univ = calculer_distance_km(lat_auto_depart, lon_auto_depart, latitude_univ, longitude_univ)

            # Condition de réservation: passager plus proche de l'université que l'automobiliste
            if distance_passager_univ < distance_automobiliste_univ:
                # L'annonce est éligible, l'ajouter à la liste affichée
                automobiliste_user = get_user_by_email(annonce.id_automobiliste)
                automobiliste_name = automobiliste_user.prenom if automobiliste_user else "Inconnu"
                
                # Calculer la distance du passager à l'automobiliste (pour affichage)
                distance_passager_automobiliste = calculer_distance_km(self.passager_lat, self.passager_lon, lat_auto_depart, lon_auto_depart)

                display_text = (
                    f"ID: {annonce.id_annonce[:8]}... | Automobiliste: {automobiliste_name} | Engin: {annonce.engin} | "
                    f"Heure: {annonce.heure_depart} | Places: {annonce.places_disponibles} | "
                    f"Distance à l'auto: {distance_passager_automobiliste:.2f} km"
                )
                self.rides_listbox.insert(tk.END, display_text)
                self.available_annonces.append(annonce) # Stocker l'objet Annonce complet

                # Dessiner le trajet de l'automobiliste en bleu
                path_points_auto = [(lat_auto_depart, lon_auto_depart), (latitude_univ, longitude_univ)]
                self.map_display.draw_path(path_points_auto, color="blue", width=3)

        if not self.available_annonces:
            self.rides_listbox.insert(tk.END, "Aucun trajet disponible correspondant à vos critères.")

    def on_ride_select(self, event):
        """
        Active le bouton de réservation si un trajet est sélectionné dans la liste.
        Affiche le trajet sélectionné sur la carte.
        """
        self.map_display.clear_all_markers_and_paths() # Effacer les anciens éléments

        if self.rides_listbox.curselection():
            self.reserve_button.config(state=tk.NORMAL)
            selected_annonce = self.available_annonces[self.rides_listbox.curselection()[0]]

            # Afficher la position du passager et de l'université
            destination_universite = self.search_universite_var.get()
            coords_univ = get_coordonnees_universite(destination_universite)
            latitude_univ, longitude_univ = coords_univ

            self.map_display.add_marker(self.passager_lat, self.passager_lon, text="Votre position")
            self.map_display.add_marker(latitude_univ, longitude_univ, text=destination_universite)

            # Afficher le trajet de l'automobiliste sélectionné en bleu
            lat_auto_depart = selected_annonce.position_depart["latitude"]
            lon_auto_depart = selected_annonce.position_depart["longitude"]
            self.map_display.add_marker(lat_auto_depart, lon_auto_depart, text=f"Départ {selected_annonce.engin}")
            path_points_auto = [(lat_auto_depart, lon_auto_depart), (latitude_univ, longitude_univ)]
            self.map_display.draw_path(path_points_auto, color="blue", width=3)

            # Centrer la carte sur le trajet sélectionné
            self.map_display.set_map_center(
                (self.passager_lat + lat_auto_depart + latitude_univ) / 3,
                (self.passager_lon + lon_auto_depart + longitude_univ) / 3,
                zoom=10
            )
            self.notebook.select(self.map_frame) # Passer à l'onglet de la carte
        else:
            self.reserve_button.config(state=tk.DISABLED)

    def handle_reservation(self):
        """
        Gère la logique de réservation d'un trajet sélectionné.
        Appelle la fonction de réservation du backend et gère les retours.
        """
        selected_index = self.rides_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Attention", "Veuillez sélectionner un trajet à réserver.")
            return
        
        # Récupérer l'objet Annonce complet à partir de la liste stockée
        selected_annonce = self.available_annonces[selected_index[0]]
        annonce_id = selected_annonce.id_annonce

        # Appeler la fonction de réservation du backend
        success, message = reserver_trajet(annonce_id, self.user_email, self.passager_lat, self.passager_lon)

        if success:
            messagebox.showinfo("Réservation réussie", message)
            self.search_rides() # Actualiser la liste des trajets disponibles
            self.update_reservations_tab() # Mettre à jour l'onglet des réservations
            
            # --- Mettre à jour la carte avec le trajet réservé (orange) ---
            self.map_display.clear_all_markers_and_paths() # Effacer les anciens éléments

            destination_universite = self.search_universite_var.get()
            coords_univ = get_coordonnees_universite(destination_universite)
            latitude_univ, longitude_univ = coords_univ

            # Marqueurs
            self.map_display.add_marker(self.passager_lat, self.passager_lon, text="Votre point de prise en charge")
            self.map_display.add_marker(latitude_univ, longitude_univ, text=destination_universite)
            lat_auto_depart = selected_annonce.position_depart["latitude"]
            lon_auto_depart = selected_annonce.position_depart["longitude"]
            self.map_display.add_marker(lat_auto_depart, lon_auto_depart, text=f"Départ {selected_annonce.engin}")

            # Dessiner le trajet mis à jour en orange (passager -> automobiliste -> université)
            path_points_reserved = [
                (self.passager_lat, self.passager_lon),
                (lat_auto_depart, lon_auto_depart),
                (latitude_univ, longitude_univ)
            ]
            self.map_display.draw_path(path_points_reserved, color="orange", width=5)
            self.map_display.set_map_center(
                (self.passager_lat + lat_auto_depart + latitude_univ) / 3,
                (self.passager_lon + lon_auto_depart + longitude_univ) / 3,
                zoom=10
            )
            self.notebook.select(self.map_frame) # Passer à l'onglet de la carte

            # Ici, déclencher l'affichage de la vidéo sponsorisée après réservation
        else:
            messagebox.showerror("Erreur de réservation", message)

    def create_reservations_tab(self, parent_frame):
        """
        Crée les widgets pour l'onglet "Mes réservations".
        Affiche les trajets que le passager a réservés et permet de les noter.
        """
        self.my_reservations_listbox = tk.Listbox(parent_frame, height=15, width=80)
        self.my_reservations_listbox.pack(padx=10, pady=10, fill="both", expand=True)
        self.my_reservations_listbox.bind("<<ListboxSelect>>", self.on_my_reservation_select)

        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(pady=5)

        # Champ de saisie pour la note
        ttk.Label(button_frame, text="Note (0-5):").pack(side=tk.LEFT, padx=5)
        self.note_entry = ttk.Entry(button_frame, width=5)
        self.note_entry.pack(side=tk.LEFT, padx=5)

        self.note_button = ttk.Button(button_frame, text="Noter le trajet", command=self.handle_notation, state=tk.DISABLED)
        self.note_button.pack(side=tk.LEFT, padx=5)

    def update_reservations_tab(self):
        """
        Met à jour la liste des réservations du passager.
        """
        self.my_reservations_listbox.delete(0, tk.END)
        historique = get_historique_utilisateur(self.user_email)
        if historique:
            for trajet in historique:
                if trajet["role"] == "passager":
                    display_text = (
                        f"ID: {trajet['id'][:8]}... | Automobiliste: {trajet['automobiliste_email']} | "
                        f"Dest: {trajet['universite']} | Heure: {trajet['heure_depart']} | "
                        f"État: {trajet['etat']} | Note: {trajet.get('notes_moyenne', 'N/A')}"
                    )
                    self.my_reservations_listbox.insert(tk.END, display_text)
        else:
            self.my_reservations_listbox.insert(tk.END, "Aucune réservation.")
        self.note_button.config(state=tk.DISABLED)

    def on_my_reservation_select(self, event):
        """
        Active le bouton de notation si une réservation est sélectionnée.
        """
        if self.my_reservations_listbox.curselection():
            selected_index = self.my_reservations_listbox.curselection()[0]
            historique = get_historique_utilisateur(self.user_email)
            selected_trajet = None
            current_passager_reservations = [t for t in historique if t["role"] == "passager"]
            if selected_index < len(current_passager_reservations):
                selected_trajet = current_passager_reservations[selected_index]

            if selected_trajet and selected_trajet["etat"] == "termine" and not selected_trajet.get("note_donnee", False):
                self.note_button.config(state=tk.NORMAL)
            else:
                self.note_button.config(state=tk.DISABLED)
        else:
            self.note_button.config(state=tk.DISABLED)

    def handle_notation(self):
        """
        Gère la logique de notation d'un trajet.
        """
        selected_index = self.my_reservations_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Attention", "Veuillez sélectionner un trajet à noter.")
            return

        historique = get_historique_utilisateur(self.user_email)
        selected_trajet = None
        current_passager_reservations = [t for t in historique if t["role"] == "passager"]
        if selected_index[0] < len(current_passager_reservations):
            selected_trajet = current_passager_reservations[selected_index[0]]

        if not selected_trajet:
            messagebox.showerror("Erreur", "Trajet sélectionné introuvable.")
            return

        try:
            note = int(self.note_entry.get())
            if not (0 <= note <= 5):
                raise ValueError("Note hors de portée")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer une note valide entre 0 et 5.")
            return

        success, message = noter_trajet(selected_trajet["id"], self.user_email, note)

        if success:
            messagebox.showinfo("Notation réussie", message)
            self.update_reservations_tab() # Actualiser la liste des réservations
            # Ici, déclencher l'affichage de la vidéo sponsorisée après notation
        else:
            messagebox.showerror("Erreur de notation", message)

    def create_historique_tab(self, parent_frame):
        """
        Crée les widgets pour l'onglet "Historique des trajets".
        """
        self.historique_listbox = tk.Listbox(parent_frame, height=20, width=100)
        self.historique_listbox.pack(padx=10, pady=10, fill="both", expand=True)

        # Bouton pour actualiser l'historique
        ttk.Button(parent_frame, text="Actualiser l'historique", command=self.update_historique_tab).pack(pady=5)

    def update_historique_tab(self):
        """
        Met à jour la liste de l'historique des trajets du passager.
        """
        self.historique_listbox.delete(0, tk.END)
        historique = get_historique_utilisateur(self.user_email)
        if historique:
            for trajet in historique:
                display_text = (
                    f"ID: {trajet['id'][:8]}... | Rôle: {trajet['role']} | Dest: {trajet['universite']} | "
                    f"Heure: {trajet['heure_depart']} | État: {trajet['etat']} | "
                    f"Points: {trajet.get('points', 0)} | Note: {trajet.get('notes_moyenne', 'N/A')}"
                )
                self.historique_listbox.insert(tk.END, display_text)
        else:
            self.historique_listbox.insert(tk.END, "Aucun trajet dans l'historique.")

    def create_parametres_tab(self, parent_frame):
        """
        Crée les widgets pour l'onglet "Paramètres".
        Permet de basculer le rôle de l'utilisateur.
        """
        ttk.Label(parent_frame, text="Basculer mon rôle:").pack(pady=10)
        ttk.Button(parent_frame, text="Devenir Automobiliste", command=self.switch_to_automobiliste_role).pack(pady=5)

    def switch_to_automobiliste_role(self):
        """
        Change le rôle de l'utilisateur en 'automobiliste' et navigue vers l'interface automobiliste.
        """
        if self.user.role == "automobiliste":
            messagebox.showinfo("Rôle", "Vous êtes déjà un automobiliste.")
            self.controller.show_frame("InterfaceAutomobilisteFrame", self.user_email)
            return

        # Demander confirmation
        confirm = messagebox.askyesno("Confirmation", "Voulez-vous vraiment devenir automobiliste ?")
        if confirm:
            # Mettre à jour le rôle dans le backend
            success, message = update_user_role(self.user_email, "automobiliste")
            if success:
                messagebox.showinfo("Succès", message)
                # Naviguer vers l'interface automobiliste
                self.controller.show_frame("InterfaceAutomobilisteFrame", self.user_email)
            else:
                messagebox.showerror("Erreur", message)

    def logout(self):
        """
        Déconnecte l'utilisateur et retourne à la page de connexion.
        """
        confirm = messagebox.askyesno("Déconnexion", "Voulez-vous vraiment vous déconnecter ?")
        if confirm:
            self.controller.show_frame("LoginRegisterFrame")

    def show(self):
        """
        Méthode appelée lorsque cette frame est affichée.
        """
        self.tkraise()
        self.update_reservations_tab()
        self.update_historique_tab()
        # Mettre à jour la position du passager à chaque fois que la frame est affichée
        current_loc = get_current_location()
        if current_loc:
            self.passager_lat, self.passager_lon = current_loc
        else:
            # Coordonnées par défaut si la géolocalisation échoue (à remplacer par une vraie gestion d'erreur/saisie)
            self.passager_lat = 12.3686 # Exemple de latitude
            self.passager_lon = -1.5334 # Exemple de longitude
            # messagebox.showwarning("Géolocalisation", "Impossible d'obtenir votre position actuelle. Utilisation de coordonnées par défaut.")
        self.search_rides() # Actualiser les annonces disponibles à chaque affichage


