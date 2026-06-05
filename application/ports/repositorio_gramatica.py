from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List
from core.entities.gramatica import GramaticaRegular

class GrammarRepositoryPort(ABC):
    """Porta que define o contrato para persistência e recuperação de Gramáticas Regulares."""
    
    @abstractmethod
    def save(self, gramatica: GramaticaRegular) -> None:
        """Salva uma gramática regular na persistência."""
        pass

    @abstractmethod
    def get_by_id(self, id_gramatica: UUID) -> Optional[GramaticaRegular]:
        """Busca uma gramática pelo seu UUID."""
        pass

    @abstractmethod
    def get_all(self) -> List[GramaticaRegular]:
        """Recupera todas as gramáticas registradas."""
        pass
