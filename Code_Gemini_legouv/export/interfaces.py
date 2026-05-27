"""Définition de l'interface d'exportateur."""

from abc import ABC, abstractmethod
from core.journal import JournalIntern

class IExportateur(ABC):
    """Interface abstraite pour les exportateurs selon le diagramme `image_2.png`."""

    @abstractmethod
    def exporter_journal(self, journal: JournalIntern) -> None:
        """Prend le journal interne et l'exporte au format spécifique."""
        pass