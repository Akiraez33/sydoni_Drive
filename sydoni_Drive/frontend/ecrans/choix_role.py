import tkinter as tk
from tkinter import ttk, messagebox
from backend.users import update_user_role # Importation de la fonction de mise à jour du rôle

class ChoixRoleFrame(tk.Frame):
    """
    Cadre (Frame) pour le choix du rôle de l\'utilisateur (automobiliste ou passager).
    Cette page est affichée après une connexion réussie ou lors du changement de rôle.
    """
    def __init__(self, parent, controller):
        """
        Initialise le cadre de choix du rôle.

        Args:
            parent (tk.Tk ou tk.Frame): Le widget parent (généralement la fenêtre principale de l\'application).
            controller (object): L\'objet contrôleur (SydoniDriveApp) pour la navigation entre les pages.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.user_email = None # L\'email de l\'utilisateur sera défini via set_user_email

        # Configuration de la mise en page (layout) pour centrer les éléments
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Titre de la page
        label = ttk.Label(self, text="Choisissez votre rôle", font=("Helvetica", 18, "bold"))
        label.grid(row=0, column=0, pady=20)

        # Bouton pour choisir le rôle d\'automobiliste
        automobiliste_button = ttk.Button(self, text="Automobiliste",
                                          command=lambda: self.set_role_and_navigate("automobiliste"))
        automobiliste_button.grid(row=1, column=0, pady=10, ipadx=20, ipady=10)

        # Bouton pour choisir le rôle de passager
        passager_button = ttk.Button(self, text="Passager",
                                     command=lambda: self.set_role_and_navigate("passager"))
        passager_button.grid(row=2, column=0, pady=10, ipadx=20, ipady=10)

    def set_user_email(self, email):
        """
        Définit l\'email de l\'utilisateur pour cette frame.
        Cette méthode est appelée par le contrôleur (SydoniDriveApp) lors de la navigation.
        Args:
            email (str): L\'email de l\'utilisateur connecté.
        """
        self.user_email = email

    def set_role_and_navigate(self, role):
        """
        Définit le rôle de l\'utilisateur dans le backend et navigue vers l\'interface correspondante.

        Args:
            role (str): Le rôle à attribuer à l\'utilisateur (\"automobiliste\" ou \"passager\").
        """
        if not self.user_email:
            messagebox.showerror("Erreur", "Email utilisateur non défini. Veuillez vous reconnecter.")
            self.controller.show_frame("LoginRegisterFrame") # Retour à la page de connexion
            return

        # Appel de la fonction du backend pour mettre à jour le rôle de l\'utilisateur
        success, message = update_user_role(self.user_email, role)
        
        if success:
            messagebox.showinfo("Rôle mis à jour", message)
            if role == "automobiliste":
                # Naviguer vers l\'interface automobiliste en passant l\'email de l\'utilisateur
                self.controller.show_frame("InterfaceAutomobilisteFrame", user_email=self.user_email)
            else:
                # Naviguer vers l\'interface passager en passant l\'email de l\'utilisateur
                self.controller.show_frame("InterfacePassagerFrame", user_email=self.user_email)
        else:
            messagebox.showerror("Erreur", f"Erreur lors de la mise à jour du rôle: {message}")

    def show(self):
        """
        Affiche ce cadre et s\'assure qu\'il est au premier plan.
        """
        self.tkraise()


