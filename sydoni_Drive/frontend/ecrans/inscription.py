import tkinter as tk
from tkinter import ttk, messagebox
from backend.users import register_user # Importation de la fonction d\'enregistrement d\'utilisateur
from backend.universites import charger_universites # Pour charger la liste des universités

class InscriptionFrame(tk.Frame):
    """
    Cadre (Frame) pour la page d\'inscription de l\'application Sydoni\'Drive.
    Permet aux nouveaux utilisateurs de s\'enregistrer en tant qu\'automobiliste ou passager.
    """
    def __init__(self, parent, controller):
        """
        Initialise le cadre de la page d\'inscription.

        Args:
            parent (tk.Tk ou tk.Frame): Le widget parent (généralement la fenêtre principale de l\'application).
            controller (object): L\'objet contrôleur (SydoniDriveApp) pour la navigation entre les pages.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Charger la liste des universités disponibles depuis le backend
        self.universites = [univ["nom"] for univ in charger_universites()]

        # Configuration de la mise en page en grille pour un alignement propre
        # Les colonnes 0 et 1 auront des poids pour s\'adapter à la taille de la fenêtre
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)

        # --- Widgets pour les informations communes à tous les utilisateurs ---

        # Champ Nom
        ttk.Label(self, text="Nom:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nom_entry = ttk.Entry(self)
        self.nom_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Champ Prénom
        ttk.Label(self, text="Prénom:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.prenom_entry = ttk.Entry(self)
        self.prenom_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Champ Email
        ttk.Label(self, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.email_entry = ttk.Entry(self)
        self.email_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Champ Mot de passe (NOUVEAU)
        ttk.Label(self, text="Mot de passe:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.password_entry = ttk.Entry(self, show="*") # \'show=\'*\' masque le texte pour la sécurité
        self.password_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Champ Numéro de téléphone
        ttk.Label(self, text="Téléphone:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.telephone_entry = ttk.Entry(self)
        self.telephone_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        # Champ Université (liste déroulante)
        ttk.Label(self, text="Université:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.universite_var = tk.StringVar(self)
        self.universite_dropdown = ttk.Combobox(self, textvariable=self.universite_var, values=self.universites, state="readonly")
        self.universite_dropdown.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        if self.universites: # Sélectionne la première université par défaut si la liste n\'est pas vide
            self.universite_dropdown.set(self.universites[0])

        # --- Choix du rôle (Radio buttons) ---
        ttk.Label(self, text="Rôle:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.role_var = tk.StringVar(self)
        self.role_var.set("passager") # Rôle par défaut au démarrage
        
        # Radio button pour Passager
        self.role_radio_passager = ttk.Radiobutton(self, text="Passager", variable=self.role_var, value="passager", command=self.toggle_automobiliste_fields)
        self.role_radio_passager.grid(row=6, column=1, padx=5, pady=5, sticky="w")
        
        # Radio button pour Automobiliste
        self.role_radio_automobiliste = ttk.Radiobutton(self, text="Automobiliste", variable=self.role_var, value="automobiliste", command=self.toggle_automobiliste_fields)
        self.role_radio_automobiliste.grid(row=7, column=1, padx=5, pady=5, sticky="w")

        # --- Champs spécifiques à l\'automobiliste (initialement masqués) ---
        # Ces widgets sont créés mais leur affichage est géré par toggle_automobiliste_fields
        self.engin_label = ttk.Label(self, text="Engin:")
        self.engin_var = tk.StringVar(self)
        self.engin_dropdown = ttk.Combobox(self, textvariable=self.engin_var, values=["moto", "voiture", "vélo"], state="readonly")
        self.engin_dropdown.set("moto") # Engin par défaut

        self.places_label = ttk.Label(self, text="Places disponibles:")
        self.places_entry = ttk.Entry(self)

        # Appelle cette fonction une fois pour initialiser l\'état correct des champs
        self.toggle_automobiliste_fields()

        # --- Boutons d\'action ---

        # Bouton d\'inscription
        ttk.Button(self, text="S\'inscrire", command=self.inscrire_utilisateur).grid(row=10, column=0, columnspan=2, pady=10)

        # Bouton de retour à la page de connexion/inscription
        ttk.Button(self, text="Retour", command=lambda: self.controller.show_frame("LoginRegisterFrame")).grid(row=11, column=0, columnspan=2, pady=5)

    def toggle_automobiliste_fields(self):
        """
        Affiche ou masque les champs spécifiques à l\'automobiliste (engin, places disponibles)
        en fonction du rôle sélectionné (Automobiliste ou Passager).
        """
        if self.role_var.get() == "automobiliste":
            # Si le rôle est automobiliste, afficher les champs
            self.engin_label.grid(row=8, column=0, padx=5, pady=5, sticky="w")
            self.engin_dropdown.grid(row=8, column=1, padx=5, pady=5, sticky="ew")
            self.places_label.grid(row=9, column=0, padx=5, pady=5, sticky="w")
            self.places_entry.grid(row=9, column=1, padx=5, pady=5, sticky="ew")
        else:
            # Si le rôle est passager, masquer les champs
            self.engin_label.grid_forget()
            self.engin_dropdown.grid_forget()
            self.places_label.grid_forget()
            self.places_entry.grid_forget()

    def inscrire_utilisateur(self):
        """
        Collecte les informations du formulaire et tente d\'inscrire le nouvel utilisateur
        en appelant la fonction d\'enregistrement du backend.
        """
        nom = self.nom_entry.get().strip()
        prenom = self.prenom_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip() # Récupération du mot de passe
        telephone = self.telephone_entry.get().strip()
        universite = self.universite_var.get()
        role = self.role_var.get()

        engin = None
        places_disponibles = None

        # Validation des champs communs
        if not all([nom, prenom, email, password, telephone, universite]):
            messagebox.showerror("Erreur d\'inscription", "Veuillez remplir tous les champs obligatoires.")
            return
        
        # Validation spécifique pour l\'email (format basique)
        if "@" not in email or "." not in email:
            messagebox.showerror("Erreur d\'inscription", "Veuillez entrer une adresse email valide.")
            return

        # Validation spécifique pour l\'automobiliste
        if role == "automobiliste":
            engin = self.engin_var.get()
            places_str = self.places_entry.get().strip()
            if not engin or not places_str:
                messagebox.showerror("Erreur d\'inscription", "Veuillez spécifier l\'engin et le nombre de places disponibles.")
                return
            try:
                places_disponibles = int(places_str)
                if places_disponibles < 0:
                    messagebox.showerror("Erreur d\'inscription", "Le nombre de places disponibles doit être positif.")
                    return
            except ValueError:
                messagebox.showerror("Erreur d\'inscription", "Veuillez entrer un nombre valide pour les places disponibles.")
                return

        # Appel à la fonction d\'enregistrement du backend
        # Note: La fonction register_user du backend a été mise à jour pour accepter le mot de passe.
        success, message = register_user(nom, prenom, telephone, email, password, universite, role, engin, places_disponibles)

        if success:
            messagebox.showinfo("Inscription réussie", message)
            # Après une inscription réussie, naviguer vers la page de confidentialité
            self.controller.show_frame("ConfidentialiteFrame") 
        else:
            messagebox.showerror("Erreur d\'inscription", message)

    def show(self):
        """
        Affiche ce cadre et s\'assure qu\'il est au premier plan.
        """
        self.tkraise()

