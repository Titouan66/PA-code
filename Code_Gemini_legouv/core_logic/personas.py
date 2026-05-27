"""Définition des entités de simulation : la hiérarchie Persona."""

from abc import ABC, abstractmethod
from typing import List, Optional, Union
from core.models import Caractéristique

class Persona(ABC):
    """Classe abstraite représentant l'infrastructure commune d'un Persona.

    Inspirée des diagrammes `image_0.png` et `image_2.png`.
    """
    def __init__(self, account_id: str, client_app_name: str, login_ip: str, username: str) -> None:
        self._account_id: str = account_id
        self._client_app_name: str = client_app_name
        self._login_ip: str = login_ip
        self._username: str = username
        
    @property
    def account_id(self) -> str: return self._account_id
    
    @property
    def client_app_name(self) -> str: return self._client_app_name
    
    @property
    def login_ip(self) -> str: return self._login_ip
    
    @property
    def username(self) -> str: return self._username
    
    def login(self) -> None:
        """Concrete common action : Login to the social network application."""
        print(f"[PERSONA: {self.username} ({self.login_ip})] Logging in...")
        
    def update_social_network(self) -> None:
        """Concrete common action : Update the network of friends/followers."""
        print(f"[PERSONA: {self.username} ({self.login_ip})] Updating social network...")

    @abstractmethod
    def get_role(self) -> str:
        """Returns the specific role name of the Persona."""
        pass

    @abstractmethod
    def execute_process(self) -> None:
        """Point d'entrée abstrait pour l'exécution d'un processus simulé.

        Cette méthode sera implémentée de manière spécifique par les sous-classes.
        """
        pass

class Créateur(Persona):
    """Un Persona de type Créateur selon le diagramme `image_0.png`.

    Cette classe respecte la relation d'agrégation forte (composition de fait pour la simulation)
    avec une liste d'objets `Amplificateur`.
    """
    def __init__(self, account_id: str, client_app_name: str, login_ip: str, username: str) -> None:
        super().__init__(account_id, client_app_name, login_ip, username)
        self.__amplicateurs: List['Amplificateur'] = [] # Forward referencing with ' '

    @property
    def amplicateurs(self) -> List['Amplificateur']:
        """La liste des amplicateurs rattachés à ce créateur."""
        return self.__amplicateurs

    def ajouter_amplificateur(self, amplificateur: 'Amplificateur') -> None:
        """Associe un nouvel amplificateur à ce créateur."""
        self.__amplicateurs.append(amplificateur)

    def get_role(self) -> str:
        """Retourne le rôle."""
        return "Créateur"

    def produire_narratif(self) -> str:
        """Action métier : Crée un narratif."""
        print(f"[CRÉATEUR: {self.username}] Producing new narrative content.")
        return f"Récit original de {self.username}"

    def diffuser_narratif(self, narratif: str) -> None:
        """Action métier : Diffuse le narratif (crée un post)."""
        print(f"[CRÉATEUR: {self.username}] Diffusing narrative: '{narratif}'.")

    def execute_process(self) -> None:
        """Exécute les actions du Créateur selon le diagramme d'activité `image_1.png`."""
        self.login()
        self.update_social_network()
        # Le reste du processus est orchestré par le Moteur
        # et n'est pas codé en dur ici.

class Amplificateur(Persona):
    """Un Persona de type Amplificateur selon le diagramme `image_0.png`."""
    
    def __init__(self, account_id: str, client_app_name: str, login_ip: str, username: str) -> None:
        super().__init__(account_id, client_app_name, login_ip, username)
        self.__target_tweet_id: Optional[str] = None

    @property
    def target_tweet_id(self) -> Optional[str]:
        """L'ID du tweet cible à retweeter."""
        return self.__target_tweet_id
        
    @target_tweet_id.setter
    def target_tweet_id(self, tweet_id: str) -> None:
        """Définit l'ID du tweet cible."""
        self.__target_tweet_id = tweet_id

    def get_role(self) -> str:
        """Retourne le rôle."""
        return "Amplificateur"

    def retweeter(self, post_id: str) -> None:
        """Action métier : Retweeter le post du créateur."""
        print(f"[AMPLIFICATEUR: {self.username} ({self.login_ip})] Retweeting post ID: {post_id}.")

    def execute_process(self) -> None:
        """Exécute les actions de l'Amplificateur selon le diagramme d'activité `image_1.png`."""
        self.login()
        self.update_social_network()
        # Le reste du processus est orchestré par le Moteur