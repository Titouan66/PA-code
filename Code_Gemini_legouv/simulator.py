"""Point d'entrée principal : La classe Simulateur avec Interface Opérateur."""

import sys
from typing import Tuple

from core.models import Configuration
from engine.moteur import MoteurSimulation
from export.interfaces import IExportateur
from export.exporters import ExportateurX, ExportateurFacebook
from export.xes_builder import GenerateurXES

class Simulateur:
    """La classe principale qui intègre et orchestre le système de simulation."""
    def __init__(self, config: Configuration, exportateur: IExportateur) -> None:
        self.__config: Configuration = config
        self.__moteur: MoteurSimulation = MoteurSimulation(config)
        self.__exportateur: IExportateur = exportateur

    @property
    def moteur(self) -> MoteurSimulation:
        return self.__moteur

    def start(self) -> None:
        """Point d'entrée de la simulation."""
        print("\n=== SOCIAL MEDIA SIMULATOR STARTING ===\n")
        self.__moteur.lance_campagne()
        self.__exportateur.exporter_journal(self.__moteur.journal)
        print("=== SIMULATION COMPLETED ===\n")

def menu_operateur() -> Tuple[Configuration, IExportateur]:
    """Interface interactive en ligne de commande pour configurer la simulation."""
    print("==================================================")
    print("    SIMULATEUR DE CAMPAGNE DE DÉSINFORMATION")
    print("==================================================\n")

    # 1. Thème de la campagne
    theme = ""
    while not theme.strip():
        theme = input("1. Entrez le thème de la campagne (ex: 'Désinformation Santé') : ")

    # 2. Plateforme Cible
    plateforme = ""
    exportateur = None
    while True:
        print("\n2. Choisissez la plateforme cible :")
        print("   [1] X (Twitter)")
        print("   [2] Facebook")
        choix_plat = input("   Votre choix (1 ou 2) : ")
        
        if choix_plat == '1':
            plateforme = "X"
            exportateur = ExportateurX()
            break
        elif choix_plat == '2':
            plateforme = "Facebook"
            exportateur = ExportateurFacebook()
            break
        else:
            print("   Erreur : Veuillez saisir 1 ou 2.")

    # 3. Scénario
    scenario = ""
    scenarios_map = {
        '1': 'Humain normal',
        '2': 'Bot simple',
        '3': 'Demi-coordonné',
        '4': 'Coordonné'
    }
    while True:
        print("\n3. Choisissez le scénario de comportement :")
        for key, val in scenarios_map.items():
            print(f"   [{key}] {val}")
        choix_scen = input("   Votre choix (1 à 4) : ")
        
        if choix_scen in scenarios_map:
            scenario = scenarios_map[choix_scen]
            break
        else:
            print("   Erreur : Veuillez saisir un chiffre entre 1 et 4.")

    # 4. Nombre de Créateurs
    nb_createurs = 0
    while True:
        try:
            nb_createurs = int(input("\n4. Nombre de personas Créateurs (entier > 0) : "))
            if nb_createurs > 0:
                break
            else:
                print("   Erreur : Le nombre doit être supérieur à 0.")
        except ValueError:
            print("   Erreur : Veuillez saisir un nombre entier valide.")

    # 5. Nombre d'Amplificateurs par Créateur
    nb_amplificateurs = -1
    while True:
        try:
            nb_amplificateurs = int(input("\n5. Nombre d'Amplificateurs par créateur (entier >= 0) : "))
            if nb_amplificateurs >= 0:
                break
            else:
                print("   Erreur : Le nombre ne peut pas être négatif.")
        except ValueError:
            print("   Erreur : Veuillez saisir un nombre entier valide.")

    print("\n--- Configuration validée ---")
    
    # Création de l'objet Configuration
    config = Configuration(
        _theme=theme,
        _plateforme_cible=plateforme,
        _scenario_name=scenario,
        _nb_createurs=nb_createurs,
        _nb_amplicateurs_par_createur=nb_amplificateurs
    )
    
    return config, exportateur

if __name__ == "__main__":
    try:
        # Lancement du menu interactif
        sim_config, sim_exporter = menu_operateur()

        # Instanciation et lancement du Simulateur
        simulator = Simulateur(config=sim_config, exportateur=sim_exporter)
        simulator.start()

        # Si la plateforme est X, on génère le fichier XES pour le Process Mining
        if sim_config.plateforme_cible == "X":
            generateur_xes = GenerateurXES()
            generateur_xes.construire_xes()
        else:
            print("Note: La génération XES n'est implémentée que pour la plateforme X.")
            
    except KeyboardInterrupt:
        print("\n\nSimulation annulée par l'utilisateur. Au revoir !")
        sys.exit(0)