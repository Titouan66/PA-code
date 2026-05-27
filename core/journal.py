"""Gestion du journal de bord interne."""

from typing import List, Optional
from core.models import Log

class JournalIntern:
    """Journal de bord interne agrégeant les logs selon le diagramme `image_2.png`.

    Cette classe respecte la relation d'agrégation entre `JournalIntern` et `Log` :
    le journal 'use' des logs.
    """
    def __init__(self, scenario_name: str) -> None:
        self.__scenario_name: str = scenario_name
        self.__logs: List[Log] = []

    @property
    def scenario_name(self) -> str:
        """Nom du scénario du journal."""
        return self.__scenario_name

    def ajouter_log(self, log: Log) -> None:
        """Ajoute une entrée de log unitaire au journal interne."""
        self.__logs.append(log)

    def get_logs(self) -> List[Log]:
        """Retourne la liste complète des logs."""
        return self.__logs

    def get_events_by_persona(self, persona_id: str) -> List[Log]:
        """Exemple de méthode de filtrage basée sur la signature du diagramme `image_0.png`."""
        return [log for log in self.__logs if log.ip_source == persona_id]
