"""Le Moteur de Simulation orchestre les personas et le journal de bord interne."""

import random
import time
from datetime import datetime, timedelta
from typing import List

from core.models import Configuration, Log
from core.journal import JournalIntern
from core_logic.personas import Persona, Créateur, Amplificateur

class MoteurSimulation:
    """Le moteur de simulation orchestre le déroulement de la campagne."""
    
    def __init__(self, config: Configuration) -> None:
        self.__config: Configuration = config
        self.__journal: JournalIntern = JournalIntern(config.scenario_name)
        self.__createurs: List[Créateur] = []
        self.__amplicateurs: List[Amplificateur] = []
        
        self.__t0: datetime = datetime.now()
        self.__subnet_coordonne: str = f"{random.randint(1, 255)}.{random.randint(1, 255)}"

    @property
    def journal(self) -> JournalIntern:
        return self.__journal

    def __get_type_scenario(self) -> str:
        nom = self.__config.scenario_name.lower()
        if "humain" in nom: return "humain"
        if "bot" in nom: return "bot"
        if "demi" in nom: return "demi-coordonné"
        return "coordonné"

    def __generer_ip(self) -> str:
        scenario = self.__get_type_scenario()
        if scenario == "coordonné":
            return f"{self.__subnet_coordonne}.{random.randint(1, 254)}.{random.randint(1, 254)}"
        else:
            return f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"

    def __generer_date_creation(self) -> datetime:
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
        scenario = self.__get_type_scenario()
        delai_moyen_minutes = 15.0
        if scenario == "humain":
            minutes = random.expovariate(1.0 / delai_moyen_minutes)
        else:
            minutes = random.gauss(delai_moyen_minutes, 3.0)
            minutes = max(1.0, minutes)
        return timedelta(minutes=minutes)

    def __initialiser_personas(self) -> None:
        """Crée et lie les personas de la simulation, et logue leur création."""
        print("[MOTEUR] Initializing personas...")
        for i in range(self.__config.nb_createurs):
            ip_creator = self.__generer_ip()
            creator = Créateur(
                account_id=f"acc_c_{i}",
                client_app_name=self.__config.plateforme_cible,
                login_ip=ip_creator,
                username=f"Creator_{i}"
            )
            self.__createurs.append(creator)
            
            for j in range(self.__config.nb_amplicateurs_par_createur):
                ip_amp = self.__generer_ip()
                amp = Amplificateur(
                    account_id=f"acc_a_{i}_{j}",
                    client_app_name=self.__config.plateforme_cible,
                    login_ip=ip_amp,
                    username=f"Amplifier_{i}_{j}"
                )
                self.__amplicateurs.append(amp)
                creator.ajouter_amplificateur(amp)

    def lance_campagne(self) -> None:
        """Implémente la boucle principale en manipulant le temps virtuel stochastique."""
        print(f"[MOTEUR] Launching simulation campaign for: '{self.__config.scenario_name}'")
        self.__initialiser_personas()
        time.sleep(0.5)

        for creator in self.__createurs:
            # --- 1. Temps de création du compte ---
            horloge_virtuelle = self.__generer_date_creation()
            
            # ---> NOUVEAU LOG : Création de compte <---
            self.__journal.ajouter_log(Log(
                _timestamp=horloge_virtuelle,
                _nom_evenement="Création_Compte",
                _source_disarm="T0008",
                _ip_source=creator.login_ip,
                _autres_donnees={"account_id": creator.account_id, "username": creator.username},
                _fichier_cible="multiple"
            ))

            creator.execute_process()
            
            # --- 2. Temps de constitution du réseau ---
            horloge_virtuelle += self.__generer_delai()
            
            # ---> NOUVEAU LOG : Constitution du réseau <---
            # Le target_account_id est simulé ici
            self.__journal.ajouter_log(Log(
                _timestamp=horloge_virtuelle, # Sera ignoré par l'exportateur pour ce type de log
                _nom_evenement="Constituer_Reseau",
                _source_disarm="T0092",
                _ip_source=creator.login_ip,
                _autres_donnees={"account_id": creator.account_id, "target_account_id": "target_alpha_123"},
                _fichier_cible="following.js"
            ))
            
            # --- 3. Temps de diffusion du narratif ---
            horloge_virtuelle += self.__generer_delai()
            
            narratif = creator.produire_narratif()
            post_id = f"post_{creator.account_id}"
            creator.diffuser_narratif(narratif)
            
            # LOG EXISTANT : Diffusion Narratif
            self.__journal.ajouter_log(Log(
                _timestamp=horloge_virtuelle,
                _nom_evenement="Diffusion_Narratif",
                _source_disarm="T0114.001",
                _ip_source=creator.login_ip,
                _autres_donnees={"narratif": narratif, "post_id": post_id, "account_id": creator.account_id},
                _fichier_cible="tweets.js"
            ))
            time.sleep(0.1)

            for amp in creator.amplicateurs:
                # --- 1. Temps de création du compte Amplificateur ---
                creation_amp = self.__generer_date_creation()
                
                # ---> NOUVEAU LOG : Création de compte <---
                self.__journal.ajouter_log(Log(
                    _timestamp=creation_amp,
                    _nom_evenement="Création_Compte",
                    _source_disarm="T0008",
                    _ip_source=amp.login_ip,
                    _autres_donnees={"account_id": amp.account_id, "username": amp.username},
                    _fichier_cible="multiple"
                ))
                
                # --- 2. Temps de constitution du réseau Amplificateur ---
                horloge_virtuelle_amp = max(creation_amp, horloge_virtuelle) + self.__generer_delai()
                amp.execute_process()
                
                # ---> NOUVEAU LOG : Constitution du réseau <---
                self.__journal.ajouter_log(Log(
                    _timestamp=horloge_virtuelle_amp,
                    _nom_evenement="Constituer_Reseau",
                    _source_disarm="T0092",
                    _ip_source=amp.login_ip,
                    _autres_donnees={"account_id": amp.account_id, "target_account_id": creator.account_id},
                    _fichier_cible="following.js"
                ))
                
                # --- 3. Temps de retweet Amplificateur ---
                horloge_virtuelle_amp += self.__generer_delai()
                amp.target_tweet_id = post_id
                amp.retweeter(post_id)
                
                # LOG EXISTANT : Retweet
                self.__journal.ajouter_log(Log(
                    _timestamp=horloge_virtuelle_amp,
                    _nom_evenement="Retweet",
                    _source_disarm="T0039",
                    _ip_source=amp.login_ip,
                    _autres_donnees={"target_post_id": post_id, "post_id": f"tweet_{amp.account_id}", "account_id": amp.account_id, "narratif": narratif},
                    _fichier_cible="tweets.js"
                ))
                time.sleep(0.1)
        
        print("[MOTEUR] Campaign simulation completed.")