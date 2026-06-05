from dataclasses import dataclass, field
import uuid
from enum import Enum
from typing import Optional
from core.value_objects.estado import Estado
from core.value_objects.simbolo import Simbolo
from core.value_objects.transicao import Transicao
from core.value_objects.alfabeto import Alfabeto
from core.exceptions.validacao import (
    EstadoInvalidoException,
    SimboloInvalidoException,
    NaoDeterminismoException,
)

class TipoAutomato(Enum):
    DFA = "DFA"
    NFA = "NFA"
    E_NFA = "E_NFA"


@dataclass(kw_only=True)
class Automato:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    nome: str
    tipo: Optional[TipoAutomato] = None
    alfabeto: Alfabeto
    estados: frozenset[Estado]
    estado_inicial: Estado
    estados_finais: frozenset[Estado]
    transicoes: frozenset[Transicao]

    def __post_init__(self) -> None:
        self.validar()

    def validar(self) -> None:
        # 1. Estado inicial deve pertencer a estados
        if self.estado_inicial not in self.estados:
            raise EstadoInvalidoException(
                f"O estado inicial {self.estado_inicial} deve pertencer ao conjunto de estados."
            )
        
        # 2. Estados finais devem ser subconjunto de estados
        if not self.estados_finais.issubset(self.estados):
            invalidos = self.estados_finais - self.estados
            raise EstadoInvalidoException(
                f"Os seguintes estados finais não pertencem ao autômato: {invalidos}."
            )

        # 3. Transições devem usar estados e símbolos válidos
        for t in self.transicoes:
            if t.origem not in self.estados:
                raise EstadoInvalidoException(
                    f"A transição {t} contém um estado de origem inválido: {t.origem}."
                )
            if t.destino not in self.estados:
                raise EstadoInvalidoException(
                    f"A transição {t} contém um estado de destino inválido: {t.destino}."
                )
            if not t.eh_epsilon and not self.alfabeto.contem(t.simbolo):
                raise SimboloInvalidoException(
                    f"A transição {t} contém um símbolo não presente no alfabeto: {t.simbolo}."
                )

    def obter_transicoes_partindo_de(self, origem: Estado, simbolo: Simbolo) -> frozenset[Estado]:
        destinos = set()
        for t in self.transicoes:
            if t.origem == origem and t.simbolo == simbolo:
                destinos.add(t.destino)
        return frozenset(destinos)

    def obter_estados_alcancaveis(self) -> frozenset[Estado]:
        from collections import deque
        alcancaveis = {self.estado_inicial}
        fila = deque([self.estado_inicial])
        
        while fila:
            curr = fila.popleft()
            # Símbolos do alfabeto mais o epsilon
            simbolos = list(self.alfabeto.simbolos) + [Simbolo.epsilon()]
            for s in simbolos:
                destinos = self.obter_transicoes_partindo_de(curr, s)
                for dest in destinos:
                    if dest not in alcancaveis:
                        alcancaveis.add(dest)
                        fila.append(dest)
        return frozenset(alcancaveis)


@dataclass(kw_only=True)
class AFD(Automato):
    def __post_init__(self) -> None:
        self.tipo = TipoAutomato.DFA
        super().__post_init__()
        self._validar_determinismo()

    def _validar_determinismo(self) -> None:
        for t in self.transicoes:
            if t.eh_epsilon:
                raise NaoDeterminismoException(
                    f"Um AFD não pode conter transições epsilon: {t}."
                )
        
        visitados = set()
        for t in self.transicoes:
            chave = (t.origem, t.simbolo)
            if chave in visitados:
                raise NaoDeterminismoException(
                    f"Um AFD não pode conter transições paralelas para ({t.origem}, {t.simbolo})."
                )
            visitados.add(chave)

    def obter_transicao_determinista(self, origem: Estado, simbolo: Simbolo) -> Optional[Estado]:
        for t in self.transicoes:
            if t.origem == origem and t.simbolo == simbolo:
                return t.destino
        return None


@dataclass(kw_only=True)
class AFN(Automato):
    def __post_init__(self) -> None:
        tem_epsilon = any(t.eh_epsilon for t in self.transicoes)
        self.tipo = TipoAutomato.E_NFA if tem_epsilon else TipoAutomato.NFA
        super().__post_init__()

    def calcular_fecho_epsilon(self, estados: frozenset[Estado]) -> frozenset[Estado]:
        fecho = set(estados)
        pilha = list(estados)
        eps = Simbolo.epsilon()

        while list(pilha):
            curr = pilha.pop()
            destinos = self.obter_transicoes_partindo_de(curr, eps)
            for dest in destinos:
                if dest not in fecho:
                    fecho.add(dest)
                    pilha.append(dest)
        return frozenset(fecho)
