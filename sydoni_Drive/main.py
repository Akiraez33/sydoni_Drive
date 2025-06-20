import tkinter as tk
from frontend.ecrans.login_register import LoginRegisterFrame
from frontend.ecrans.choix_role import ChoixRoleFrame
from frontend.ecrans.inscription import InscriptionFrame
from frontend.ecrans.confidentialite import ConfidentialiteFrame
from frontend.ecrans.interface_automoboliste import InterfaceAutomobilisteFrame
from frontend.ecrans.interface_passager import InterfacePassagerFrame
from frontend.historique import HistoriqueFrame


class SydoniDriveApp(tk.Tk):
    """
    Classe principale de l'application Sydoni'Drive.
    Gère la fenêtre principale et la navigation entre les différents écrans (frames).
    """
    def __init__(self, *args, **kwargs):
        """
        Initialise l'application Sydoni'Drive.
        """
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Sydoni'Drive")
        self.geometry("800x600") # Taille de fenêtre par défaut
        self.resizable(False, False) # Empêche le redimensionnement de la fenêtre

        # Conteneur pour les frames
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Initialisation de tous les écrans (frames) de l'application
        # Chaque écran est une instance d'une classe de frame et est stocké dans le dictionnaire self.frames
        for F in (LoginRegisterFrame, ChoixRoleFrame, InscriptionFrame, ConfidentialiteFrame, InterfaceAutomobilisteFrame, InterfacePassagerFrame, HistoriqueFrame):
            page_name = F.__name__
            frame = F(parent=container, controller=self) # Passe le contrôleur (cette instance) à chaque frame
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Afficher la première page (LoginRegisterFrame)
        self.show_frame("LoginRegisterFrame")

    def show_frame(self, page_name, user_email=None):
        """
        Affiche la frame spécifiée par son nom.

        Args:
            page_name (str): Le nom de la classe de la frame à afficher (ex: "LoginRegisterFrame").
            user_email (str, optional): L'email de l'utilisateur connecté, passé aux frames nécessitant cette information.
        """
        frame = self.frames[page_name]
        # Si la frame a une méthode "set_user_email" ou "show" qui prend user_email, l'appeler
        if hasattr(frame, "set_user_email") and user_email:
            frame.set_user_email(user_email)
        if hasattr(frame, "show"):
            frame.show() # Appelle la méthode show() de la frame pour s'assurer qu'elle est bien affichée et mise à jour
        else:
            frame.tkraise() # Met la frame au premier plan



# Point d'entrée de l'application
if __name__ == "__main__":
    app = SydoniDriveApp()
    app.mainloop()


#§§§§