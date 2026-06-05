from dataclasses import dataclass
from uuid import UUID
from typing import List
from application.dtos.automato import PassoDidaticoDTO, AutomatonOutputDTO

@dataclass(frozen=True)
class RegraProducaoDTO:
    esquerda: str
    direita: List[str]

@dataclass(frozen=True)
class GrammarOutputDTO:
    id: UUID
    linearidade: str
    simbolo_inicial: str
    variaveis: List[str]
    terminais: List[str]
    producoes: List[RegraProducaoDTO]

@dataclass(frozen=True)
class ConverterAFParaGRInputDTO:
    id_automato: UUID

@dataclass(frozen=True)
class ConverterAFParaGROutputDTO:
    id_gramatica: UUID
    gramatica_dto: GrammarOutputDTO
    passos_didaticos: List[PassoDidaticoDTO]

@dataclass(frozen=True)
class ConverterGRParaAFInputDTO:
    id_gramatica: UUID

@dataclass(frozen=True)
class ConverterGRParaAFOutputDTO:
    id_automato: UUID
    automato_dto: AutomatonOutputDTO
    passos_didaticos: List[PassoDidaticoDTO]
