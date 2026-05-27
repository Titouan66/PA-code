"""Le Moteur de Simulation orchestre les personas de façon dynamique via un modèle JSON."""

import json
import os
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

from core.models import Configuration, Log
from core.journal import JournalIntern
from core_logic.personas import Persona, Créateur, Amplificateur

class MoteurSimulation:
    """Le moteur de simulation stochastique et piloté par les données (Data-Driven).

    Cette classe orchestre le déroulement de la campagne en fonction des séquences
    d'étapes définies de manière externe dans le fichier 'processModel.json'.
    """
    
    def __init__(self, config: Configuration) -> None:
        self.__config: Configuration = config
        self.__journal: JournalIntern = JournalIntern(config.scenario_name)
        self.__createurs: List[Créateur] = []
        self.__amplicateurs: List[Amplificateur] = []
        
        self.__t0: datetime = datetime.now()
        self.__subnet_coordonne: str = f"{random.randint(1, 255)}.{random.randint(1, 255)}"
        
        # Chargement dynamique du modèle de processus
        self.__modele_processus: Dict[str, List[str]] = self.__charger_modele_processus()

    @property
    def journal(self) -> JournalIntern:
        """Retourne le journal de bord interne."""
        return self.__journal

    def __charger_modele_processus(self) -> Dict[str, List[str]]:
        """Charge le fichier processModel.json ou applique une configuration par défaut."""
        # Calcul automatique du chemin absolu (remonte d'un dossier depuis 'engine')
        dossier_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        chemin_modele = os.path.join(dossier_base, "processModel.json")
        
        # Modèle de secours (Fallback) réglementaire si le fichier est absent
        modele_par_defaut = {
            "creator_sequence": ["init_account", "build_network", "diffuse"],
            "amplifier_sequence": ["init_account", "build_network", "retweet"]
        }
        
        if not os.path.exists(chemin_modele):
            print(f"[MOTEUR] Configuration '{chemin_modele}' absente. Utilisation du fallback interne.")
            return modele_par_defaut
            
        try:
            with open(chemin_modele, 'r', encoding='utf-8') as f:
                modele_charge = json.load(f)
                print(f"[MOTEUR] Modèle de processus '{chemin_modele}' chargé avec succès.")
                return modele_charge
        except (json.JSONDecodeError, IOError) as e:
            print(f"[MOTEUR] Erreur lors de la lecture du JSON ({e}). Utilisation du fallback interne.")
            return modele_par_defaut

    def __get_type_scenario(self) -> str:
        """Déduit la catégorie comportementale d'après le nom du scénario."""
        nom = self.__config.scenario_name.lower()
        if "humain" in nom: return "humain"
        if "bot" in nom: return "bot"
        if "demi" in nom: return "demi-coordonné"
        return "coordonné"

    def __generer_ip(self) -> str:
        """Génère une adresse IP stochastique selon le scénario."""
        scenario = self.__get_type_scenario()
        if scenario == "coordonné":
            return f"{self.__subnet_coordonne}.{random.randint(1, 254)}.{random.randint(1, 254)}"
        else:
            return f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"

    def __generer_date_creation(self) -> datetime:
        """Génère un horodatage d'origine pour le compte fictif."""
        scenario = self.__get_type_scenario()
        if scenario in ["humain", "bot"]:
            jours_ecoules = random.uniform(0, 7)
            return self.__t0 - timedelta(days=jours_ecoules)
        elif scenario == "demi-coordonné":
            if random.choice([True, False]):
                return self.__t0 - timedelta(days=random.uniform(1, 7))
            else:
                return self.__t0 + timedelta(minutes=random.uniform(0, 60))
        else:
            return self.__t0 + timedelta(minutes=random.uniform(0, 60))

    def __generer_delai(self) -> timedelta:
        """Calcule un intervalle d'attente probabiliste (Loi Gaussienne ou Exponentielle)."""
        scenario = self.__get_type_scenario()
        delai_moyen_minutes = 15.0
        if scenario == "humain":
            minutes = random.expovariate(1.0 / delai_moyen_minutes)
        else:
            minutes = random.gauss(delai_moyen_minutes, 3.0)
            minutes = max(1.0, minutes)
        return timedelta(minutes=minutes)

    def __initialiser_personas(self) -> None:
        """Instancie les entités de l'exercice algorithmique."""
        print("[MOTEUR] Initializing personas...")
        for i in range(self.__config.nb_createurs):
            creator = Créateur(
                account_id=f"acc_c_{i}",
                client_app_name=self.__config.plateforme_cible,
                login_ip=self.__generer_ip(),
                username=f"Creator_{i}"
            )
            self.__createurs.append(creator)
            
            for j in range(self.__config.nb_amplicateurs_par_createur):
                amp = Amplificateur(
                    account_id=f"acc_a_{i}_{j}",
                    client_app_name=self.__config.plateforme_cible,
                    login_ip=self.__generer_ip(),
                    username=f"Amplifier_{i}_{j}"
                )
                self.__amplicateurs.append(amp)
                creator.ajouter_amplificateur(amp)

    def lance_campagne(self) -> None:
        """Exécute les arbres comportementaux dictés dynamiquement par le fichier JSON."""
        print(f"[MOTEUR] Launching simulation campaign for: '{self.__config.scenario_name}'")
        self.__initialiser_personas()
        time.sleep(0.5)

        # Récupération des séquences configurées de manière externe
        seq_creator = self.__modele_processus.get("creator_sequence", [])
        seq_amplifier = self.__modele_processus.get("amplifier_sequence", [])

        for creator in self.__createurs:
            horloge_virtuelle = self.__t0
            post_id = f"post_{creator.account_id}"
            narratif = f"Récit original de {creator.username}"

            # --- INTERPRÉTEUR DYNAMIQUE POUR LE CRÉATEUR ---
            for etape in seq_creator:
                if etape == "init_account":
                    horloge_virtuelle = self.__generer_date_creation()
                    self.__journal.ajouter_log(Log(
                        _timestamp=horloge_virtuelle,
                        _nom_evenement="Création_Compte",
                        _source_disarm="T0008",
                        _ip_source=creator.login_ip,
                        _autres_donnees={"account_id": creator.account_id, "username": creator.username},
                        _fichier_cible="multiple"
                    ))
                    creator.execute_process()

                elif etape == "build_network":
                    horloge_virtuelle += self.__generer_delai()
                    self.__journal.ajouter_log(Log(
                        _timestamp=horloge_virtuelle,
                        _nom_evenement="Constituer_Reseau",
                        _source_disarm="T0092",
                        _ip_source=creator.login_ip,
                        _autres_donnees={"account_id": creator.account_id, "target_account_id": "target_alpha_123"},
                        _fichier_cible="following.js"
                    ))

                elif etape == "diffuse":
                    horloge_virtuelle += self.__generer_delai()
                    narratif = creator.produire_narratif()
                    creator.diffuser_narratif(narratif)
                    
                    self.__journal.ajouter_log(Log(
                        _timestamp=horloge_virtuelle,
                        _nom_evenement="Diffusion_Narratif",
                        _source_disarm="T0114.001",
                        _ip_source=creator.login_ip,
                        _autres_donnees={"narratif": narratif, "post_id": post_id, "account_id": creator.account_id},
                        _fichier_cible="tweets.js"
                    ))
            time.sleep(0.05)

            # --- INTERPRÉTEUR DYNAMIQUE POUR LES AMPLIFICATEURS ---
            for amp in creator.amplicateurs:
                horloge_virtuelle_amp = horloge_virtuelle
                creation_amp = horloge_virtuelle
                
                for etape in seq_amplifier:
                    if etape == "init_account":
                        creation_amp = self.__generer_date_creation()
                        self.__journal.ajouter_log(Log(
                            _timestamp=creation_amp,
                            _nom_evenement="Création_Compte",
                            _source_disarm="T0008",
                            _ip_source=amp.login_ip,
                            _autres_donnees={"account_id": amp.account_id, "username": amp.username},
                            _fichier_cible="multiple"
                        ))
                        amp.execute_process()

                    elif etape == "build_network":
                        horloge_virtuelle_amp = max(creation_amp, horloge_virtuelle) + self.__generer_delai()
                        self.__journal.ajouter_log(Log(
                            _timestamp=horloge_virtuelle_amp,
                            _nom_evenement="Constituer_Reseau",
                            _source_disarm="T0092",
                            _ip_source=amp.login_ip,
                            _autres_donnees={"account_id": amp.account_id, "target_account_id": creator.account_id},
                            _fichier_cible="following.js"
                        ))

                    elif etape == "retweet":
                        horloge_virtuelle_amp += self.__generer_delai()
                        amp.target_tweet_id = post_id
                        amp.retweeter(post_id)
                        
                        self.__journal.ajouter_log(Log(
                            _timestamp=horloge_virtuelle_amp,
                            _nom_evenement="Retweet",
                            _source_disarm="T0039",
                            _ip_source=amp.login_ip,
                            _autres_donnees={
                                "target_post_id": post_id,
                                "post_id": f"tweet_{amp.account_id}",
                                "account_id": amp.account_id,
                                "narratif": narratif
                            },
                            _fichier_cible="tweets.js"
                        ))
                time.sleep(0.05)
        
        print("[MOTEUR] Campaign simulation completed.")