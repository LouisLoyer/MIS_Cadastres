# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 20:39:11 2023

@author: Loyer Louis
"""

import requests
import folium
import webbrowser
import tkinter as tk
from tkinter import ttk

class Modele:
    def __init__(self):
        self.cadastres = []  # Une liste de cadastres

    def telecharger_donnees(self, url_api):
        self.cadastres = []  # Réinitialisez la liste des 
        tryToConnect = 1
        start = 0 # Penser à mettre cette valeur à 0 pour récupérer toutes les données
        iterationchargemnt = 0
        while True:
            try:
                response = requests.get(f"{url_api}&_start={start}")
                if response.status_code == 200:
                    print(f"[API Cadastres] - récupération des données en cours... {iterationchargemnt}/38 ")
                    iterationchargemnt = iterationchargemnt + 1
                    geojson_data = response.json()
                    features = geojson_data["features"]
                    if not features:
                        print("[API Cadastres] - récupération des données terminée")
                        break  # Aucune donnée supplémentaire à récupérer
                    self.cadastres.extend(features)
                    start += len(features)
                else:
                    print("[API Cadastres] - Erreur lors de la récupération des données en cours...")
                    break  # Une erreur s'est produite, arrêtez la récupération
            except requests.exceptions.ConnectionError:
                
                print(f"[API Cadastres] - Connexion refusée au serveur API_cadastres pour {iterationchargemnt}/38")
                
class Vue:
    def __init__(self, modele):
        self.modele = modele  # Référence au modèle

        self.root = tk.Tk()
        self.root.title("Visualisation de Cadastres")
        self.root.geometry("800x600")

        self.contenance_label = ttk.Label(self.root, text="Contenance recherchée:")
        self.contenance_label.pack()
        self.contenance_entry = ttk.Entry(self.root)
        self.contenance_entry.pack()
        self.rechercher_button = ttk.Button(self.root, text="Rechercher par Contenance", command=self.rechercher_par_contenance)
        self.rechercher_button.pack()

        self.m = folium.Map(location=[47.283329 , -2.2], zoom_start=10)

    def afficher_cadastres(self, cadastres, contenance_recherchee):
        for cadastre in cadastres:
            geometry = cadastre["geometry"]
            print(geometry)
            contenance = None  # Initialisation avec une valeur par défaut
            feuille = "N/A"
            #if self.est_geometrie_valide(geometry):
            properties = cadastre["properties"]
            contenance = properties.get("contenance", "N/A")
            feuille = properties.get("feuille", "N/A")
            
            # Convertir contenance en str pour la comparaison
            """if contenance_recherchee is not None:
                contenance_recherchee = int(contenance_recherchee)
                
            if contenance is not None:
                contenance = int(contenance)"""
            
            
            
            # Déterminer la couleur en fonction de la contenance recherchée
            color = 'blue' if contenance_recherchee is None else ('pink' if contenance == contenance_recherchee else 'blue')
            
                # Créer un GeoJson et ajouter au modèle
            geojson = folium.GeoJson(geometry, name=f"Contenance: {contenance}, Feuille: {feuille}", style_function=lambda x: {"fillColor": color})
            geojson.add_child(folium.Popup(f"Contenance: {contenance}, Feuille: {feuille}"))  # Ajouter une popup
            geojson.add_to(self.m)
            
            if contenance == contenance_recherchee:
                lat, lon = self.obtenir_coordonnees_centrales(geometry)
                folium.Marker([lat, lon], popup=f"Contenance: {contenance}, Feuille: {feuille}", icon=folium.Icon(color='pink')).add_to(self.m)
                
        
    def obtenir_coordonnees_centrales(self, geometry):
        """
        Obtenir les coordonnées centrales de la géométrie.
        """
        # Accéder aux coordonnées des polygones
        polygons = geometry["coordinates"]
    
        # Initialiser des listes pour les latitudes et longitudes
        latitudes = []
        longitudes = []
    
        # Parcourir les polygones (Cette partie peut peut etre s'ameliorer en accedant directement aux ring plutot que coordinates)
        for polygon in polygons:
            # Parcourir les anneaux extérieurs de chaque polygone
            for ring in polygon:
                # Parcourir les points du ring
                for point in ring:
                    # Extraire les coordonnées et les ajouter aux listes
                    latitudes.append(point[1])
                    longitudes.append(point[0])
    
        # Calculer les coordonnées centrales en prenant la moyenne
        lat_central = sum(latitudes) / len(latitudes)
        lon_central = sum(longitudes) / len(longitudes)
    
        return lat_central, lon_central
       
    def est_geometrie_valide(self, geometry):
       """
       Vérifie que la géométrie est valide en vérifiant si elle a au moins 3 points.
       """
       return len(geometry) >= 3

    def afficher_carte(self):
        self.m.save('carte_cadastres.html')
        webbrowser.open('carte_cadastres.html')  # Ouvrir la carte dans un navigateur externe

    def afficher_interface_utilisateur(self):
        self.root.mainloop()

    def get_contenance_recherchee(self):
        return int(self.contenance_entry.get())

    def rechercher_par_contenance(self):
        contenance_recherchee = self.get_contenance_recherchee()
        self.afficher_cadastres(self.modele.cadastres, contenance_recherchee)
        self.afficher_carte()

class Controleur:
    def __init__(self, modele, vue):
        self.modele = modele
        self.vue = vue

    def bouton_telecharger_cadastres(self, url_api):
        self.modele.telecharger_donnees(url_api)

if __name__ == "__main__":
    url_api = "https://apicarto.ign.fr/api/cadastre/parcelle?code_insee=44184"

    modele = Modele()
    vue = Vue(modele)  # Transmettez le modèle à la classe Vue
    controleur = Controleur(modele, vue)

    controleur.bouton_telecharger_cadastres(url_api)
    vue.afficher_interface_utilisateur()