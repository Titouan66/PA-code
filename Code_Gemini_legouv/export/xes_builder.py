"""Module de génération de fichiers XES à partir de traces JS."""

import os
import json
import re
from typing import Dict, List, Any, Optional

class GenerateurXES:
    """Génère un journal d'événements XES à partir des exports JS."""

    def __init__(self) -> None:
        self.__dossier_entree: str = "outputs"
        self.__fichier_sortie: str = os.path.join("outputs", "simulation_log.xes")
        
        # Dictionnaire pour regrouper les événements par "Trace" (accountId)
        self.__traces: Dict[str, Dict[str, Any]] = {}

    def __lire_fichier_js(self, nom_fichier: str) -> List[Dict[str, Any]]:
        """Lit un fichier JS, nettoie l'en-tête et retourne les données JSON parsées."""
        chemin = os.path.join(self.__dossier_entree, nom_fichier)
        if not os.path.exists(chemin):
            print(f"[XES] Attention : Le fichier {chemin} n'existe pas.")
            return []

        try:
            with open(chemin, 'r', encoding='utf-8') as f:
                contenu_brut = f.read()

            # Extraction du JSON pur (en ignorant la déclaration `window.YTD... = `)
            # On cherche le premier crochet '[' et le dernier ']'
            match = re.search(r'\[.*\]', contenu_brut, re.DOTALL)
            if match:
                contenu_json = match.group(0)
                return json.loads(contenu_json)
            else:
                print(f"[XES] Impossible d'extraire le JSON de {nom_fichier}.")
                return []
        except json.JSONDecodeError as e:
            print(f"[XES] Erreur de décodage JSON dans {nom_fichier}: {e}")
            return []
        except Exception as e:
            print(f"[XES] Erreur lors de la lecture de {nom_fichier}: {e}")
            return []

    def __initialiser_trace(self, account_id: str) -> None:
        """Initialise une nouvelle trace (Cas XES) si elle n'existe pas."""
        if account_id not in self.__traces:
            self.__traces[account_id] = {
                "events": [],
                "account_created": False # Flag pour la fusion T0008
            }

    def __traiter_creations_compte(self, data_account: List[Any], data_device: List[Any], data_ip: List[Any]) -> None:
        """Fusionne account, device, et ip en un seul événement T0008."""
        # On se base principalement sur account.js pour le timestamp et les infos de base
        for item in data_account:
            info = item.get("account", {})
            account_id = info.get("accountId")
            if not account_id: continue
            
            self.__initialiser_trace(account_id)
            
            # Création de l'événement T0008 fusionné
            evt = {
                "concept:name": "Créer compte fictif",
                "concept:instance": "T0008",
                "time:timestamp": info.get("createdAt"),
                "source_file": "account.js, device-token.js, ip-audit.js",
                "username": info.get("username")
            }
            
            # Note : Dans une implémentation plus poussée, on pourrait aller chercher 
            # l'IP dans data_ip et le token dans data_device pour enrichir cet événement.
            
            self.__traces[account_id]["events"].append(evt)
            self.__traces[account_id]["account_created"] = True

    def __traiter_reseaux(self, data_following: List[Any]) -> None:
        """Traite les événements de constitution de réseau (sans timestamp)."""
        for item in data_following:
            info = item.get("following", {})
            account_id = info.get("accountId")
            if not account_id: continue

            self.__initialiser_trace(account_id)
            
            # Création de l'événement T0092 (SANS timestamp)
            evt = {
                "concept:name": "Constituer réseau d'abonnés",
                "concept:instance": "T0092",
                "source_file": "following.js",
                "target_link": info.get("userLink")
            }
            self.__traces[account_id]["events"].append(evt)

    def __traiter_tweets(self, data_tweets: List[Any]) -> None:
        """Traite les tweets (Diffusion) et retweets (Amplification)."""
        for item in data_tweets:
            info = item.get("tweet", {})
            account_id = info.get("user_id")
            if not account_id: continue

            self.__initialiser_trace(account_id)
            
            is_retweet = "retweetOf" in info
            
            if is_retweet:
                # Événement T0039 : Amplifier narratif
                evt = {
                    "concept:name": "Amplifier narratif",
                    "concept:instance": "T0039",
                    "time:timestamp": info.get("created_at"),
                    "source_file": "tweets.js",
                    "tweet_id": info.get("id"),
                    "retweet_of": info.get("retweetOf")
                }
            else:
                # Événement T0114.001 : Diffuser narratif
                evt = {
                    "concept:name": "Diffuser narratif",
                    "concept:instance": "T0114.001",
                    "time:timestamp": info.get("created_at"),
                    "source_file": "tweets.js",
                    "tweet_id": info.get("id")
                }
            self.__traces[account_id]["events"].append(evt)

    def __generer_xml_xes(self) -> str:
        """Construit la chaîne de caractères XML au format XES."""
        lignes = []
        lignes.append('<?xml version="1.0" encoding="UTF-8" ?>')
        lignes.append('<log xes.version="1.0" xes.features="" openxes.version="1.0RC7" xmlns="http://www.xes-standard.org/">')
        lignes.append('    <extension name="Concept" prefix="concept" uri="http://www.xes-standard.org/concept.xesext"/>')
        lignes.append('    <extension name="Time" prefix="time" uri="http://www.xes-standard.org/time.xesext"/>')
        
        for account_id, trace_data in self.__traces.items():
            lignes.append('    <trace>')
            lignes.append(f'        <string key="concept:name" value="{account_id}"/>')
            
            for evt in trace_data["events"]:
                lignes.append('        <event>')
                
                # Attributs standards
                concept_name = evt.get("concept:name", "")
                lignes.append(f'            <string key="concept:name" value="{concept_name}"/>')
                
                concept_instance = evt.get("concept:instance", "")
                lignes.append(f'            <string key="concept:instance" value="{concept_instance}"/>')
                
                # Gestion du "trou structurel" (T0092 n'a pas de timestamp)
                timestamp = evt.get("time:timestamp")
                if timestamp:
                    lignes.append(f'            <date key="time:timestamp" value="{timestamp}"/>')
                
                # Attributs personnalisés
                for key, value in evt.items():
                    if key not in ["concept:name", "concept:instance", "time:timestamp"] and value is not None:
                        # Échappement basique des caractères spéciaux XML si besoin
                        val_str = str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
                        lignes.append(f'            <string key="{key}" value="{val_str}"/>')
                
                lignes.append('        </event>')
                
            lignes.append('    </trace>')
            
        lignes.append('</log>')
        return "\n".join(lignes)

    def construire_xes(self) -> None:
        """Orchestre la lecture, le mapping et l'écriture du XES."""
        print("\n--- RECONSTRUCTION XES (Process Mining) ---")
        
        # 1. Lecture
        print("[XES] Lecture des fichiers JS...")
        d_acc = self.__lire_fichier_js("account.js")
        d_dev = self.__lire_fichier_js("device-token.js")
        d_ip = self.__lire_fichier_js("ip-audit.js")
        d_fol = self.__lire_fichier_js("following.js")
        d_twe = self.__lire_fichier_js("tweets.js")
        
        # 2. Mapping Inverse
        print("[XES] Application du mapping inverse DISARM...")
        self.__traiter_creations_compte(d_acc, d_dev, d_ip)
        self.__traiter_reseaux(d_fol)
        self.__traiter_tweets(d_twe)
        
        # 3. Écriture XML
        print("[XES] Génération du fichier XML...")
        contenu_xml = self.__generer_xml_xes()
        
        with open(self.__fichier_sortie, 'w', encoding='utf-8') as f:
            f.write(contenu_xml)
            
        print(f"[XES] Succès : Fichier {self.__fichier_sortie} généré.")
        print("--- RECONSTRUCTION TERMINÉE ---\n")