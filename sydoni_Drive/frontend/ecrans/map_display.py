import tkinter as tk
import tkintermapview

class MapDisplayFrame(tk.Frame):
    """
    Cadre (Frame) pour afficher une carte interactive en utilisant TkinterMapView.
    Permet de centrer la carte, d'ajouter des marqueurs et de dessiner des chemins.
    """
    def __init__(self, parent, controller):
        """
        Initialise le cadre d'affichage de la carte.

        Args:
            parent (tk.Tk ou tk.Frame): Le widget parent.
            controller (object): L'objet contrôleur pour la navigation.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Création du widget de carte
        # width et height peuvent être ajustés en fonction de la taille souhaitée
        self.map_widget = tkintermapview.TkinterMapView(self, width=800, height=600, corner_radius=0)
        self.map_widget.pack(fill="both", expand=True)

        # Définir le centre de la carte par défaut (par exemple, Koudougou, Burkina Faso)
        self.map_widget.set_position(12.25, -2.36) # Coordonnées approximatives de Koudougou
        self.map_widget.set_zoom(12) # Niveau de zoom par défaut

    def set_map_center(self, latitude, longitude, zoom=12):
        """
        Centre la carte sur les coordonnées spécifiées avec un niveau de zoom donné.

        Args:
            latitude (float): Latitude du centre de la carte.
            longitude (float): Longitude du centre de la carte.
            zoom (int, optional): Niveau de zoom de la carte. Par défaut à 12.
        """
        self.map_widget.set_position(latitude, longitude)
        self.map_widget.set_zoom(zoom)

    def add_marker(self, latitude, longitude, text="", command=None):
        """
        Ajoute un marqueur sur la carte.

        Args:
            latitude (float): Latitude du marqueur.
            longitude (float): Longitude du marqueur.
            text (str, optional): Texte à afficher avec le marqueur. Par défaut vide.
            command (function, optional): Fonction à appeler lors du clic sur le marqueur. Par défaut None.

        Returns:
            tkintermapview.CanvasPositionMarker: L'objet marqueur créé.
        """
        return self.map_widget.set_marker(latitude, longitude, text=text, command=command)

    def draw_path(self, path_points, color="blue", width=5):
        """
        Dessine un chemin sur la carte.

        Args:
            path_points (list): Liste de tuples (latitude, longitude) représentant les points du chemin.
            color (str, optional): Couleur du chemin. Par défaut "blue".
            width (int, optional): Largeur du chemin. Par défaut 5.

        Returns:
            tkintermapview.CanvasPath: L'objet chemin créé.
        """
        return self.map_widget.set_path(path_points, color=color, width=width)

    def clear_all_markers_and_paths(self):
        """
        Efface tous les marqueurs et chemins de la carte.
        """
        self.map_widget.delete_all_marker()
        self.map_widget.delete_all_path()

    def show(self):
        """
        Affiche ce cadre.
        """
        self.tkraise()


