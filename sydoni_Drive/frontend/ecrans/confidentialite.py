import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

class ConfidentialiteFrame(tk.Frame):
    """
    Cadre (Frame) pour afficher la politique de confidentialité et les conditions d\"utilisation.
    L\"utilisateur doit accepter ces conditions pour continuer après l\"inscription.
    """
    def __init__(self, parent, controller):
        """
        Initialise le cadre de la page de confidentialité.

        Args:
            parent (tk.Tk ou tk.Frame): Le widget parent.
            controller (object): L\"objet contrôleur pour la navigation.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.user_email = None # Sera défini par le contrôleur

        # Configuration de la mise en page
        self.grid_rowconfigure(0, weight=0) # Titre
        self.grid_rowconfigure(1, weight=1) # Texte de confidentialité (extensible)
        self.grid_rowconfigure(2, weight=0) # Case à cocher
        self.grid_rowconfigure(3, weight=0) # Bouton Continuer
        self.grid_columnconfigure(0, weight=1)

        # Titre de la page
        label = ttk.Label(self, text="Politique de Confidentialité et Conditions d\"Utilisation", font=("Helvetica", 16, "bold"))
        label.grid(row=0, column=0, pady=(20, 10))

        # Zone de texte pour la politique de confidentialité (avec barre de défilement)
        self.privacy_text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=80, height=15, font=("Helvetica", 10))
        self.privacy_text_area.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # Contenu de la politique de confidentialité (vous pouvez l\"améliorer et l\"étendre)
        privacy_content = ("""
Le respect, la courtoisie et l\"entraide sont les principes clés de Sydoni\'Drive. Veuillez les respecter et vous respecter mutuellement sous peine de sanctions.

L\'entreprise ainsi que ses développeurs se désengagent de toute responsabilité liée aux différentes relations et contacts entre les automobilistes et les passagers en cas de problèmes survenant en dehors du fonctionnement direct de l\'application.

En cas de problème non directement lié au fonctionnement technique de l\'application (par exemple, désaccords personnels, incidents durant le trajet non causés par une défaillance de l\'application), l\'entreprise n\'est en aucun cas responsable.

En cas de panne de véhicule ou d\'accident durant un trajet organisé via Sydoni\'Drive, les utilisateurs (automobilistes et passagers) sont responsables de gérer eux-mêmes les problèmes qui en découlent. L\'automobiliste est entièrement responsable de son engin, de son entretien, de son assurance et du respect du code de la route.

Sydoni\'Drive est une plateforme de mise en relation et ne saurait être tenue responsable des actes ou omissions de ses utilisateurs.

En utilisant Sydoni\'Drive, vous acceptez ces conditions.
""")
        self.privacy_text_area.insert(tk.INSERT, privacy_content)
        self.privacy_text_area.config(state=tk.DISABLED) # Rendre le texte non modifiable

        # Case à cocher pour l\"acceptation
        self.accept_var = tk.BooleanVar()
        self.accept_checkbutton = ttk.Checkbutton(self, text="J\"ai lu et j\"accepte la politique de confidentialité et les conditions d\"utilisation.", variable=self.accept_var)
        self.accept_checkbutton.grid(row=2, column=0, pady=10)

        # Bouton pour continuer
        self.continue_button = ttk.Button(self, text="Continuer", command=self.handle_continue)
        self.continue_button.grid(row=3, column=0, pady=20)

    def set_user_email(self, email):
        """
        Définit l\"email de l\"utilisateur pour cette frame.
        """
        self.user_email = email

    def handle_continue(self):
        """
        Vérifie si l\"utilisateur a accepté les conditions et navigue vers la page de choix de rôle.
        """
        if self.accept_var.get():
            # Si l\"utilisateur a accepté, naviguer vers la page de choix de rôle
            # L\"email de l\"utilisateur est nécessaire pour la page de choix de rôle
            if self.user_email:
                self.controller.show_frame("ChoixRoleFrame", user_email=self.user_email)
            else:
                # Cela ne devrait pas arriver si le flux est correct
                messagebox.showerror("Erreur", "Email utilisateur non disponible. Veuillez vous reconnecter.")
                self.controller.show_frame("LoginRegisterFrame")
        else:
            messagebox.showwarning("Acceptation requise", "Veuillez accepter la politique de confidentialité et les conditions d\"utilisation pour continuer.")

    def show(self):
        """
        Affiche ce cadre.
        """
        self.tkraise()


