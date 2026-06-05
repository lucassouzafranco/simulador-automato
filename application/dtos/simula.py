from dataclasses import dataclass
from uuid import UUID
from typing import List
from application.dtos.automato import PassoDidaticoDTO

@dataclass(frozen=True)
class SimularPalavraInputDTO:
    id_automato: UUID
    palavra: str

@dataclass(frozen=True)
class SimularPalavraOutputDTO:
    aceita: bool
    passos_didaticos: List[PassoDidaticoDTO]
