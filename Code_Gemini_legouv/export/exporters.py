"""Implémentations concrètes des exportateurs avec écriture de fichiers physiques."""

import os
import json
from typing import List, Dict, Any

from export.interfaces import IExportateur
from core.journal import JournalIntern
from core.models import Log

class ExportateurX(IExportateur):
    """Implémentation concrète d'un exportateur pour la plateforme X."""

    def __init__(self) -> None:
        self.__dossier_sortie: str = "outputs"

    def exporter_journal(self, journal: JournalIntern) -> None:
        """Méthode principale qui orchestre le mapping et l'exportation."""
        print(f"\n--- EXPORTING TO PLATFORM X (FormatX) ---")
        print(f"Scenario: '{journal.scenario_name}'")
        
        # 1. Initialisation des 5 listes en mémoire (qui deviendront les 5 fichiers)
        data_account: List[Dict[str, Any]] = []
        data_device: List[Dict[str, Any]] = []
        data_ip: List[Dict[str, Any]] = []
        data_following: List[Dict[str, Any]] = []
        data_tweets: List[Dict[str, Any]] = []

        # 2. Routage et Mapping un-à-plusieurs
        for log in journal.get_logs():
            evt = log.nom_evenement
            donnees = log.autres_donnees
            
            # Formatage du timestamp ISO (ex: 2024-04-01T14:04:00Z)
            timestamp_iso = log.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            # Extraction sécurisée des données (avec fallbacks pour éviter les crashs)
            account_id = donnees.get("account_id", f"acc_{log.ip_source}")
            username = donnees.get("username", "unknown_user")

            # -- ACTION 1 : Créer un compte fictif (Génère 3 traces) --
            if evt in ["Création_Compte", "Créer compte fictif"]:
                # Fichier 1 : account.js
                data_account.append({
                    "account": {
                        "accountId": account_id,
                        "username": username,
                        "email": f"{username}@gmail.com",
                        "createdVia": "web",
                        "createdAt": timestamp_iso
                    }
                })
                
                # Fichier 2 : device-token.js
                data_device.append({
                    "deviceToken": {
                        "accountId": account_id,
                        "clientApplicationId": "3033300",
                        "clientApplicationName": "Twitter Web App",
                        "token": donnees.get("token", "a3f8b2c1d9e4f5"),
                        "createdAt": timestamp_iso,
                        "lastSeenAt": timestamp_iso
                    }
                })
                
                # Fichier 3 : ip-audit.js
                data_ip.append({
                    "ipAudit": {
                        "accountId": account_id,
                        "loginIp": log.ip_source,
                        "createdAt": timestamp_iso
                    }
                })

            # -- ACTION 2 : Constituer un réseau (Génère 1 trace) --
            elif evt in ["Constituer_Reseau", "Constituer réseau"]:
                target_id = donnees.get("target_account_id", "783214")
                # Fichier 4 : following.js -> /!\ RÈGLE STRICTE : AUCUN TIMESTAMP
                data_following.append({
                    "following": {
                        "accountId": account_id,
                        "userLink": f"twitter.com/intent/user?user_id={target_id}"
                    }
                })

            # -- ACTION 3 : Diffuser narratif (Génère 1 trace) --
            elif evt == "Diffusion_Narratif":
                # Fichier 5 : tweets.js (Original)
                data_tweets.append({
                    "tweet": {
                        "id": donnees.get("post_id", "0000000000"),
                        "full_text": donnees.get("narratif", ""),
                        "created_at": timestamp_iso,
                        "user_id": account_id
                    }
                })

            # -- ACTION 4 : Amplifier narratif (Génère 1 trace) --
            elif evt == "Retweet":
                # Fichier 5 : tweets.js (Retweet)
                data_tweets.append({
                    "tweet": {
                        "id": donnees.get("post_id", "0000000000"),
                        "full_text": f"RT : {donnees.get('narratif', '...')}",
                        "created_at": timestamp_iso,
                        "user_id": account_id,
                        "retweetOf": donnees.get("target_post_id", "0000000000")
                    }
                })

        # 3. Écriture physique des 5 fichiers avec leur syntaxe JavaScript d'encapsulation
        self.__ecrire_fichier("account.js", "window.YTD.account.part0", data_account)
        self.__ecrire_fichier("device-token.js", "window.YTD.device_token.part0", data_device)
        self.__ecrire_fichier("ip-audit.js", "window.YTD.ip_audit.part0", data_ip)
        self.__ecrire_fichier("following.js", "window.YTD.following.part0", data_following)
        self.__ecrire_fichier("tweets.js", "window.YTD.tweets.part0", data_tweets)

        print("--- FORMAT X EXPORT COMPLETE ---\n")

    def __ecrire_fichier(self, nom_fichier: str, nom_variable: str, donnees: List[Dict[str, Any]]) -> None:
        """Formate la liste en JSON, l'encapsule en JS et crée le fichier."""
        # Sécurité : Créer le dossier s'il n'existe pas
        os.makedirs(self.__dossier_sortie, exist_ok=True)
        
        chemin_complet = os.path.join(self.__dossier_sortie, nom_fichier)
        
        # Formatage JSON avec indentation propre
        contenu_json = json.dumps(donnees, indent=4, ensure_ascii=False)
        
        # Encapsulation JavaScript
        contenu_final = f"{nom_variable} = {contenu_json};\n"
        
        # Écriture
        with open(chemin_complet, 'w', encoding='utf-8') as fichier:
            fichier.write(contenu_final)
            
        print(f"[EXPORT] {nom_fichier} généré ({len(donnees)} entrées).")


class ExportateurFacebook(IExportateur):
    """Implémentation concrète d'un exportateur pour la plateforme Facebook.
    
    Traduit les logs d'une campagne de désinformation au format JSON natif
    propre aux archives d'utilisateurs de Facebook.
    """

    def __init__(self) -> None:
        self.__dossier_sortie: str = "outputs"

    def exporter_journal(self, journal: JournalIntern) -> None:
        """Méthode principale qui extrait les logs, applique le mapping Facebook

        et écrit les fichiers JSON sur le disque.
        """
        print(f"\n--- EXPORTING TO PLATFORM FACEBOOK ---")
        print(f"Scenario: '{journal.scenario_name}'")

        # Initialisation des structures de données en mémoire pour Facebook
        # profile_information.json a un dictionnaire maître racine
        data_profile: Dict[str, Any] = {"profile_v2": {}}
        
        # friends_and_followers.json contient un dictionnaire avec une liste
        data_friends: Dict[str, Any] = {"friends_v2": []}
        
        # your_posts.json est historiquement une liste de publications sous Facebook
        data_posts: List[Dict[str, Any]] = []

        # Parcours et routage de chaque log du journal interne
        for log in journal.get_logs():
            evt = log.nom_evenement
            donnees = log.autres_donnees
            
            # Conversion du timestamp au format texte ISO standard
            timestamp_iso = log.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            # Extraction sécurisée des informations avec valeurs par défaut
            account_id = donnees.get("account_id", f"acc_{log.ip_source}")
            username = donnees.get("username", "unknown_facebook_user")
            narratif = donnees.get("narratif", "")

            # -- ACTION 1 : Création de compte fictif --
            if evt in ["Création_Compte", "Créer compte fictif"]:
                # Note : Les archives FB structurent souvent le profil autour du dernier compte traité
                data_profile["profile_v2"] = {
                    "name": {
                        "full_name": username
                    },
                    "registration_timestamp": timestamp_iso,
                    "ip_address": log.ip_source
                }

            # -- ACTION 2 : Constituer un réseau --
            elif evt in ["Constituer_Reseau", "Constituer réseau"]:
                target_id = donnees.get("target_account_id", "unknown_target")
                data_friends["friends_v2"].append({
                    "name": target_id,
                    "timestamp": timestamp_iso
                })

            # -- ACTION 3 : Diffuser narratif --
            elif evt == "Diffusion_Narratif":
                data_posts.append({
                    "timestamp": timestamp_iso,
                    "data": [
                        {"post": narratif}
                    ],
                    "title": f"{username} updated their status.",
                    "status_type": "original"
                })

            # -- ACTION 4 : Amplifier narratif (Partage de publication) --
            elif evt == "Retweet":
                data_posts.append({
                    "timestamp": timestamp_iso,
                    "data": [
                        {"post": narratif}
                    ],
                    "title": f"{username} shared a link.",
                    "status_type": "shared_post"
                })

        # Écriture physique des 3 fichiers JSON natifs
        self.__ecrire_fichier_json("profile_information.json", data_profile)
        self.__ecrire_fichier_json("friends_and_followers.json", data_friends)
        self.__ecrire_fichier_json("your_posts.json", data_posts)

        print("--- FACEBOOK EXPORT COMPLETE ---\n")

    def __ecrire_fichier_json(self, nom_fichier: str, donnees: Any) -> None:
        """Formate et écrit les données reçues au format JSON strict."""
        # Sécurité : S'assurer que le dossier outputs existe
        os.makedirs(self.__dossier_sortie, exist_ok=True)
        
        chemin_complet = os.path.join(self.__dossier_sortie, nom_fichier)
        
        # Sérialisation en JSON pur (indenté à 4 espaces et encodage UTF-8)
        with open(chemin_complet, 'w', encoding='utf-8') as fichier:
            json.dump(donnees, fichier, indent=4, ensure_ascii=False)
            
        # Comptage dynamique des entrées selon la structure pour le log de console
        nb_elements = 0
        if isinstance(donnees, list):
            nb_elements = len(donnees)
        elif isinstance(donnees, dict):
            # Regarde la taille de la liste interne principale si elle existe
            cle_principale = list(donnees.keys())[0] if donnees.keys() else ""
            if cle_principale and isinstance(donnees[cle_principale], list):
                nb_elements = len(donnees[cle_principale])
            elif donnees.get(cle_principale):
                nb_elements = 1

        print(f"[EXPORT FB] {nom_fichier} généré ({nb_elements} entrées/mises à jour).")