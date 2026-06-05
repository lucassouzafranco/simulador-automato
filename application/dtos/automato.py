from dataclasses import dataclass
from uuid import UUID
from typing import Optional, List, Dict

@dataclass(frozen=True)
class PassoDidaticoDTO:
    indice: int
    descricao: str
    dados_calculo: Dict

@dataclass(frozen=True)
class TransicaoDTO:
    origem: str
    simbolo: str
    destino: str

@dataclass(frozen=True)
class CriarAFNInputDTO:
    nome: str
    alfabeto: List[str]
    estados: List[str]
    estado_inicial: str
    estados_finais: List[str]
    transicoes: List[Dict]  # lista de dicts contendo {"origem": ..., "simbolo": ..., "destino": ...}

@dataclass(frozen=True)
class CriarAFNOutputDTO:
    id_automato: Optional[UUID]
    nome: str
    sucesso: bool
    mensagem_erro: Optional[str] = None

@dataclass(frozen=True)
class AutomatonOutputDTO:
    id: UUID
    nome: str
    tipo: str
    alfabeto: List[str]
    estados: List[str]
    estado_inicial: str
    estados_finais: List[str]
    transicoes: List[TransicaoDTO]

@dataclass(frozen=True)
class ConverterAFNParaAFDInputDTO:
    id_automato: UUID

@dataclass(frozen=True)
class ConverterAFNParaAFDOutputDTO:
    id_afd: UUID
    passos_didaticos: List[PassoDidaticoDTO]
    automato_dto: AutomatonOutputDTO

@dataclass(frozen=True)
class MinimizarAFDInputDTO:
    id_automato: UUID

@dataclass(frozen=True)
class MinimizarAFDOutputDTO:
    id_afd_minimizado: UUID
    passos_didaticos: List[PassoDidaticoDTO]
    automato_dto: AutomatonOutputDTO
