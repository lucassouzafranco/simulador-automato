from uuid import UUID
from typing import Optional, List, Dict
from threading import Lock
from application.ports.repositorio_gramatica import GrammarRepositoryPort
from core.entities.gramatica import GramaticaRegular

class InMemoryGrammarRepository(GrammarRepositoryPort):
    """Implementação em memória para persistência de gramáticas regulares (thread-safe)."""
    
    def __init__(self) -> None:
        self._db: Dict[UUID, GramaticaRegular] = {}
        self._lock = Lock()

    def save(self, gramatica: GramaticaRegular) -> None:
        with self._lock:
            self._db[gramatica.id] = gramatica

    def get_by_id(self, id_gramatica: UUID) -> Optional[GramaticaRegular]:
        with self._lock:
            return self._db.get(id_gramatica)

    def get_all(self) -> List[GramaticaRegular]:
        with self._lock:
            return list(self._db.values())
