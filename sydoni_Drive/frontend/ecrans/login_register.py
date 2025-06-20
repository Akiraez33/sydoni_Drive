import tkinter as tk
from tkinter import ttk, messagebox
from backend.users import login_user # Importation de la fonction d'authentification

class LoginRegisterFrame(tk.Frame):
    """
    Cadre (Frame) de la page de connexion et d'inscription de l'application Sydoni'Drive.
    Cette page permet à l'utilisateur de se connecter avec son email et mot de passe,
    ou de naviguer vers la page d'inscription.
    """
    def __init__(self, parent, controller):
        """
        Initialise le cadre de la page de connexion/inscription.

        Args:
            parent (tk.Tk ou tk.Frame): Le widget parent (généralement la fenêtre principale).
            controller (object): L'objet contrôleur qui gère la navigation entre les pages.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Configuration de la mise en page (layout)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)

        # Titre de la page
        ttk.Label(self, text="Connexion / Inscription", font=("Helvetica", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=20)

        # Champ Email
        ttk.Label(self, text="Email:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.email_entry = ttk.Entry(self)
        self.email_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Champ Mot de passe
        ttk.Label(self, text="Mot de passe:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.password_entry = ttk.Entry(self, show="*") # show='*' masque le mot de passe
        self.password_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Bouton de connexion
        ttk.Button(self, text="Se connecter", command=self.handle_login).grid(row=3, column=0, columnspan=2, pady=10)

        # Bouton pour naviguer vers la page d'inscription
        ttk.Button(self, text="S'inscrire", command=self.go_to_register).grid(row=4, column=0, columnspan=2, pady=10)

    def handle_login(self):
        """
        Gère la logique de connexion de l'utilisateur.
        Récupère l'email et le mot de passe, appelle la fonction d'authentification du backend.
        """
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            messagebox.showerror("Erreur de connexion", "Veuillez entrer votre email et votre mot de passe.")
            return

        success, user, message, role = login_user(email, password)

        if success:
            messagebox.showinfo("Connexion réussie", message)
            # Naviguer vers la page de choix de rôle en passant l'email de l'utilisateur
            self.controller.show_frame("ChoixRoleFrame", user_email=email)
        else:
            messagebox.showerror("Erreur de connexion", message)

    def show(self):
        """
        Affiche ce cadre et s'assure qu'il est au premier plan.
        """
        self.tkraise()

        # Effacer les champs de saisie à chaque fois que la page est affichée
        self.email_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def go_to_register(self):
        """
        Navigue vers la page d'inscription.
        """
        self.controller.show_frame("InscriptionFrame")
