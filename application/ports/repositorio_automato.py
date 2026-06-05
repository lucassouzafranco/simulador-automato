from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List
from core.entities.automato import Automato

class AutomatonRepositoryPort(ABC):
    """Porta que define o contrato para persistência e recuperação de Autômatos Finitos."""
    
    @abstractmethod
    def save(self, automato: Automato) -> None:
        """Salva um autômato na persistência física ou em memória."""
        pass

    @abstractmethod
    def get_by_id(self, id_automato: UUID) -> Optional[Automato]:
        """Busca um autômato pelo seu UUID."""
        pass

    @abstractmethod
    def get_all(self) -> List[Automato]:
        """Recupera todos os autômatos registrados."""
        pass
