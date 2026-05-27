"""Cœur du système : Définitions de base et modèles de données."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from datetime import datetime

class Caractéristique(Enum):
    """Représente les caractéristiques des personas selon le diagramme `image_2.png`."""
    HUMAIN = "Humain"
    BOT = "Bot"
    DEMI_COORDONNE = "Demi-coordonné"
    COORDONNE = "Coordonné"

@dataclass
class Configuration:
    """Structure de configuration de la simulation selon le diagramme `image_0.png`."""
    _theme: str
    _plateforme_cible: str
    _scenario_name: str
    _nb_createurs: int
    _nb_amplicateurs_par_createur: int

    @property
    def theme(self) -> str: return self._theme
    
    @property
    def plateforme_cible(self) -> str: return self._plateforme_cible
    
    @property
    def scenario_name(self) -> str: return self._scenario_name
    
    @property
    def nb_createurs(self) -> int: return self._nb_createurs
    
    @property
    def nb_amplicateurs_par_createur(self) -> int: return self._nb_amplicateurs_par_createur

    def get_scenario_config(self) -> dict[str, object]:
        """Exemple de méthode basée sur la signature du diagramme image_0.png."""
        return {
            "theme": self.theme,
            "platform": self.plateforme_cible,
            "scenario_name": self.scenario_name,
            "creators_count": self.nb_createurs,
            "amplifiers_per_creator": self.nb_amplicateurs_par_createur
        }

@dataclass
class Log:
    """Représente une entrée de log unitaire selon le diagramme `image_2.png`."""
    _timestamp: datetime
    _nom_evenement: str
    _source_disarm: str
    _ip_source: str
    _autres_donnees: dict[str, str] = field(default_factory=dict)
    _fichier_cible: Optional[str] = None

    @property
    def timestamp(self) -> datetime: return self._timestamp
    
    @property
    def nom_evenement(self) -> str: return self._nom_evenement
    
    @property
    def source_disarm(self) -> str: return self._source_disarm
    
    @property
    def ip_source(self) -> str: return self._ip_source
    
    @property
    def autres_donnees(self) -> dict[str, str]: return self._autres_donnees
    
    @property
    def fichier_cible(self) -> Optional[str]: return self._fichier_cible