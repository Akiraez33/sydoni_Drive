import tkinter as tk
import datetime
from tkinter import ttk, messagebox
from backend.trajets import publier_trajet, terminer_trajet, get_historique_utilisateur
from backend.universites import charger_universites, get_coordonnees_universite
from backend.users import get_user_by_email, update_user_role
from backend.geolocalisation import get_current_location # Pour obtenir la position de l'automobiliste
from frontend.ecrans.map_display import MapDisplayFrame # Importation du module d'affichage de la carte

class InterfaceAutomobilisteFrame(tk.Frame):
    """
    Cadre (Frame) de l'interface pour les automobilistes.
    Permet de publier des annonces de covoiturage, de consulter l'historique des trajets,
    et de gérer les paramètres liés au rôle d'automobiliste.
    """
    def __init__(self, parent, controller):
        """
        Initialise le cadre de l'interface automobiliste.

        Args:
            parent (tk.Tk ou tk.Frame): Le widget parent (généralement la fenêtre principale de l'application).
            controller (object): L'objet contrôleur (SydoniDriveApp) pour la navigation entre les pages.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.user_email = None # L'email de l'utilisateur sera défini via set_user_email
        self.user = None # L'objet User sera chargé via set_user_email
        self.automobiliste_lat = None # Latitude actuelle de l'automobiliste
        self.automobiliste_lon = None # Longitude actuelle de l'automobiliste

        # Charger la liste des universités disponibles depuis le backend
        self.universites = [univ["nom"] for univ in charger_universites()]

        # Création d'un Notebook (système d'onglets) pour organiser l'interface
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # --- Onglet "Publier une annonce" ---
        self.publication_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.publication_frame, text="Publier une annonce")
        self.create_publication_tab(self.publication_frame)

        # --- Onglet "Carte du trajet" ---
        self.map_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.map_frame, text="Carte du trajet")
        self.map_display = MapDisplayFrame(self.map_frame, self.controller) # Instancier la carte
        self.map_display.pack(fill="both", expand=True)

        # --- Onglet "Historique des trajets" ---
        self.historique_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.historique_frame, text="Historique des trajets")
        self.create_historique_tab(self.historique_frame)

        # --- Onglet "Paramètres" ---
        self.parametres_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.parametres_frame, text="Paramètres")
        self.create_parametres_tab(self.parametres_frame)

        # Bouton de déconnexion (placé en bas du cadre principal)
        ttk.Button(self, text="Déconnexion", command=self.logout).pack(pady=5)

    def set_user_email(self, email):
        """
        Définit l'email de l'utilisateur pour cette frame et charge ses informations.
        Cette méthode est appelée par le contrôleur (SydoniDriveApp) lors de la navigation.

        Args:
            email (str): L'email de l'automobiliste connecté.
        """
        self.user_email = email
        self.user = get_user_by_email(email) # Charger l'objet User complet
        if not self.user:
            messagebox.showerror("Erreur", "Utilisateur non trouvé. Veuillez vous reconnecter.")
            self.controller.show_frame("LoginRegisterFrame")
            return
        
        # Tenter d'obtenir la position actuelle de l'automobiliste
        current_loc = get_current_location()
        if current_loc:
            self.automobiliste_lat, self.automobiliste_lon = current_loc
        else:
            # Coordonnées par défaut si la géolocalisation échoue (à remplacer par une vraie gestion d'erreur/saisie)
            self.automobiliste_lat = 12.3686 # Exemple de latitude
            self.automobiliste_lon = -1.5334 # Exemple de longitude
            messagebox.showwarning("Géolocalisation", "Impossible d'obtenir votre position actuelle. Utilisation de coordonnées par défaut.")

    def create_publication_tab(self, parent_frame):
        """
        Crée les widgets pour l'onglet "Publier une annonce".
        Permet à l'automobiliste de saisir les détails de son trajet.
        """
        # Configuration de la grille pour l'alignement des champs
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.columnconfigure(1, weight=2)

        # Champ Université de destination
        ttk.Label(parent_frame, text="Université de destination:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.pub_universite_var = tk.StringVar(parent_frame)
        self.pub_universite_dropdown = ttk.Combobox(parent_frame, textvariable=self.pub_universite_var, values=self.universites, state="readonly")
        self.pub_universite_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        if self.universites:
            self.pub_universite_dropdown.set(self.universites[0]) # Sélectionne la première université par défaut

        # Champ Heure de départ
        ttk.Label(parent_frame, text="Heure de départ (HH:MM):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.pub_heure_depart_entry = ttk.Entry(parent_frame)
        self.pub_heure_depart_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Champ Places disponibles
        ttk.Label(parent_frame, text="Places disponibles:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.pub_places_disponibles_entry = ttk.Entry(parent_frame)
        self.pub_places_disponibles_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Bouton Publier l'annonce
        ttk.Button(parent_frame, text="Publier l'annonce", command=self.handle_publication).grid(row=3, column=0, columnspan=2, pady=10)

    def handle_publication(self):
        """
        Gère la logique de publication d'une annonce de trajet.
        Collecte les données du formulaire et appelle la fonction de publication du backend.
        """
        universite = self.pub_universite_var.get()
        heure_depart = self.pub_heure_depart_entry.get()
        places_str = self.pub_places_disponibles_entry.get()

        # Validation des champs du formulaire
        if not all([universite, heure_depart, places_str]):
            messagebox.showerror("Erreur de publication", "Veuillez remplir tous les champs.")
            return

        try:
            places_disponibles = int(places_str)
            if places_disponibles <= 0:
                messagebox.showerror("Erreur de publication", "Le nombre de places doit être supérieur à 0.")
                return
        except ValueError:
            messagebox.showerror("Erreur de publication", "Veuillez entrer un nombre valide pour les places disponibles.")
            return
        
        try:
            # Valider le format de l'heure (HH:MM)
            datetime.strptime(heure_depart, "%H:%M")
        except ValueError:
            messagebox.showerror("Erreur de publication", "Format d'heure invalide. Utilisez HH:MM (ex: 14:30).")
            return

        # Utiliser la position actuelle de l'automobiliste
        latitude_depart = self.automobiliste_lat
        longitude_depart = self.automobiliste_lon

        # Appel de la fonction de publication du backend
        success, message = publier_trajet(self.user_email, universite, heure_depart, places_disponibles, latitude_depart, longitude_depart)

        if success:
            messagebox.showinfo("Publication réussie", message)
            # Effacer les champs après une publication réussie
            self.pub_heure_depart_entry.delete(0, tk.END)
            self.pub_places_disponibles_entry.delete(0, tk.END)
            self.update_historique_tab() # Mettre à jour l'historique après publication
            self.update_user_points_display() # Mettre à jour l'affichage des points
            
            # --- Affichage du trajet sur la carte après publication ---
            self.display_ride_on_map(universite, latitude_depart, longitude_depart)
            # Ici, déclencher l'affichage de la vidéo sponsorisée après publication
        else:
            messagebox.showerror("Erreur de publication", message)

    def display_ride_on_map(self, universite_destination, lat_depart, lon_depart):
        """
        Affiche le trajet de l'automobiliste sur la carte.
        """
        self.map_display.clear_all_markers_and_paths() # Effacer les anciens éléments

        # Ajouter un marqueur pour la position de départ de l'automobiliste
        self.map_display.add_marker(lat_depart, lon_depart, text="Votre position")

        # Récupérer les coordonnées de l'université de destination
        coords_univ = get_coordonnees_universite(universite_destination)
        if coords_univ:
            lat_univ, lon_univ = coords_univ
            self.map_display.add_marker(lat_univ, lon_univ, text=universite_destination)
            
            # Dessiner le chemin de l'automobiliste à l'université
            path_points = [(lat_depart, lon_depart), (lat_univ, lon_univ)]
            self.map_display.draw_path(path_points, color="blue", width=5)
            
            # Centrer la carte sur le trajet
            self.map_display.set_map_center((lat_depart + lat_univ) / 2, (lon_depart + lon_univ) / 2, zoom=10)
        else:
            messagebox.showwarning("Carte", "Impossible de trouver les coordonnées de l'université de destination.")

        self.notebook.select(self.map_frame) # Passer à l'onglet de la carte

    def create_historique_tab(self, parent_frame):
        """
        Crée les widgets pour l'onglet "Historique des trajets".
        Affiche la liste des trajets publiés par l'automobiliste et ses points.
        """
        # Affichage des points de l'utilisateur
        self.points_label = ttk.Label(parent_frame, text=f"Vos points: {self.user.points if self.user else 0}", font=("Helvetica", 12, "bold"))
        self.points_label.pack(pady=10)

        # Liste des trajets dans un Listbox
        self.historique_listbox = tk.Listbox(parent_frame, height=15, width=80)
        self.historique_listbox.pack(padx=10, pady=10, fill="both", expand=True)
        self.historique_listbox.bind("<<ListboxSelect>>", self.on_historique_select)

        # Boutons d'action pour l'historique
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(pady=5)

        self.terminer_trajet_button = ttk.Button(button_frame, text="Terminer le trajet sélectionné", command=self.handle_terminer_trajet, state=tk.DISABLED)
        self.terminer_trajet_button.pack(side=tk.LEFT, padx=5)

        self.refresh_historique_button = ttk.Button(button_frame, text="Actualiser l'historique", command=self.update_historique_tab)
        self.refresh_historique_button.pack(side=tk.LEFT, padx=5)

        self.update_historique_tab() # Charger l'historique au démarrage de l'onglet

    def update_historique_tab(self):
        """
        Met à jour la liste des trajets dans l'onglet "Historique des trajets".
        Récupère l'historique depuis le backend et l'affiche.
        """
        self.historique_listbox.delete(0, tk.END) # Efface les éléments précédents
        historique = get_historique_utilisateur(self.user_email) # Récupère l'historique pour l'utilisateur connecté
        if historique:
            for i, trajet in enumerate(historique):
                # Affichage des informations du trajet
                display_text = (
                    f"ID: {trajet['id']} | Dest: {trajet['universite']} | Heure: {trajet['heure_depart']} | "
                    f"État: {trajet['etat']} | Rôle: {trajet['role']} | Points: {trajet['points']} | "
                    f"Note Moy: {trajet['notes_moyenne']}"
                )
                self.historique_listbox.insert(tk.END, display_text)
        else:
            self.historique_listbox.insert(tk.END, "Aucun trajet dans l'historique.")
        self.terminer_trajet_button.config(state=tk.DISABLED) # Désactiver le bouton après l'actualisation
        self.update_user_points_display() # Mettre à jour l'affichage des points

    def on_historique_select(self, event):
        """
        Active le bouton "Terminer le trajet" si un trajet est sélectionné dans la liste.
        """
        if self.historique_listbox.curselection():
            self.terminer_trajet_button.config(state=tk.NORMAL)
        else:
            self.terminer_trajet_button.config(state=tk.DISABLED)

    def handle_terminer_trajet(self):
        """
        Gère la logique pour marquer un trajet comme terminé.
        Récupère l'ID du trajet sélectionné et appelle la fonction du backend.
        """
        selected_index = self.historique_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Attention", "Veuillez sélectionner un trajet à terminer.")
            return
        
        # Récupérer l'ID du trajet à partir du texte affiché dans la Listbox
        selected_text = self.historique_listbox.get(selected_index[0])
        try:
            # L'ID est extrait du début de la chaîne de caractères (ex: "ID: 123 | ...")
            trajet_id = selected_text.split("|")[0].split(":")[1].strip()
        except (ValueError, IndexError):
            messagebox.showerror("Erreur", "Impossible de récupérer l'ID du trajet sélectionné.")
            return

        # Appel de la fonction du backend pour terminer le trajet
        success, message = terminer_trajet(trajet_id)
        if success:
            messagebox.showinfo("Succès", message)
            self.update_historique_tab() # Actualiser l'historique après la terminaison
            self.update_user_points_display() # Mettre à jour l'affichage des points
            self.map_display.clear_all_markers_and_paths() # Effacer le trajet de la carte
            # Ici, déclencher l'affichage de la vidéo sponsorisée après réception de la note (si applicable)
            # self.controller.show_sponsored_video("apres_notation_automobiliste")
        else:
            messagebox.showerror("Erreur", message)

    def create_parametres_tab(self, parent_frame):
        """
        Crée les widgets pour l'onglet "Paramètres".
        Permet à l'automobiliste de basculer en mode passager et d'afficher ses points.
        """
        ttk.Label(parent_frame, text="Changer de rôle:", font=("Helvetica", 12, "bold")).pack(pady=10)

        # Bouton pour basculer en mode passager
        ttk.Button(parent_frame, text="Passer en mode Passager", command=self.switch_to_passager_role).pack(pady=5)

        # Affichage des points de l'utilisateur dans l'onglet Paramètres
        self.param_points_label = ttk.Label(parent_frame, text=f"Vos points: {self.user.points if self.user else 0}", font=("Helvetica", 12, "bold"))
        self.param_points_label.pack(pady=10)

    def switch_to_passager_role(self):
        """
        Gère le basculement du rôle de l'utilisateur vers "passager".
        Appelle la fonction du backend pour mettre à jour le rôle et navigue vers l'interface passager.
        """
        response = messagebox.askyesno("Changer de rôle", "Voulez-vous vraiment passer en mode Passager ?")
        if response:
            success, message = update_user_role(self.user_email, "passager")
            if success:
                messagebox.showinfo("Rôle mis à jour", message)
                # Naviguer vers l'interface passager en passant l'email de l'utilisateur
                self.controller.show_frame("InterfacePassagerFrame", user_email=self.user_email)
            else:
                messagebox.showerror("Erreur", message)

    def update_user_points_display(self):
        """
        Met à jour l'affichage des points de l'utilisateur dans les différents labels.
        Recharge les données de l'utilisateur pour obtenir les points les plus récents.
        """
        if self.user_email:
            self.user = get_user_by_email(self.user_email) # Recharger les données de l'utilisateur
            if self.user:
                # Mettre à jour les labels d'affichage des points
                self.points_label.config(text=f"Vos points: {self.user.points}")
                self.param_points_label.config(text=f"Vos points: {self.user.points}")

    def logout(self):
        """
        Gère la déconnexion de l'utilisateur.
        Demande confirmation et redirige vers la page de connexion/inscription.
        """
        if messagebox.askyesno("Déconnexion", "Voulez-vous vraiment vous déconnecter ?"):
            # Réinitialiser l'état de l'application et revenir à la page de connexion
            self.controller.show_frame("LoginRegisterFrame")

    def show(self):
        """
        Affiche ce cadre et s'assure qu'il est au premier plan.
        Cette méthode est appelée par le contrôleur chaque fois que cette frame doit être affichée.
        """
        # S'assurer que les informations de l'utilisateur et l'historique sont à jour à chaque affichage
        if self.user_email:
            self.set_user_email(self.user_email) # Recharger l'utilisateur et sa position
            self.update_user_points_display()
            self.update_historique_tab()
        self.tkraise()


