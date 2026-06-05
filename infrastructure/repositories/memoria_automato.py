from uuid import UUID
from typing import Optional, List, Dict
from threading import Lock
from application.ports.repositorio_automato import AutomatonRepositoryPort
from core.entities.automato import Automato

class InMemoryAutomatonRepository(AutomatonRepositoryPort):
    """Implementação em memória para persistência de autômatos (thread-safe)."""
    
    def __init__(self) -> None:
        self._db: Dict[UUID, Automato] = {}
        self._lock = Lock()

    def save(self, automato: Automato) -> None:
        with self._lock:
            self._db[automato.id] = automato

    def get_by_id(self, id_automato: UUID) -> Optional[Automato]:
        with self._lock:
            return self._db.get(id_automato)

    def get_all(self) -> List[Automato]:
        with self._lock:
            return list(self._db.values())
