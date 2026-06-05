from dataclasses import dataclass
from typing import Union
from enum import Enum

class TipoProducao(Enum):
    TERMINAL = "TERMINAL"                     # A -> a
    TERMINAL_VARIAVEL = "TERMINAL_VARIAVEL"   # A -> aB
    VARIAVEL_TERMINAL = "VARIAVEL_TERMINAL"   # A -> Ba
    VAZIA = "VAZIA"                           # A -> ε


@dataclass(frozen=True, slots=True)
class Variavel:
    rotulo: str

    def __post_init__(self) -> None:
        if not self.rotulo:
            raise ValueError("O rótulo da variável não pode ser vazio.")

    def __str__(self) -> str:
        return self.rotulo


@dataclass(frozen=True, slots=True)
class Terminal:
    caractere: str

    def __post_init__(self) -> None:
        if not self.caractere:
            raise ValueError("O caractere do terminal não pode ser vazio.")
        if len(self.caractere) != 1:
            raise ValueError("O símbolo terminal deve conter exatamente 1 caractere.")

    def __str__(self) -> str:
        return self.caractere


@dataclass(frozen=True, slots=True)
class RegraProducao:
    esquerda: Variavel
    direita: tuple[Union[Variavel, Terminal], ...]

    def __post_init__(self) -> None:
        if not self.esquerda:
            raise ValueError("O lado esquerdo da produção não pode ser nulo.")
        if len(self.direita) > 2:
            raise ValueError("Uma gramática regular não permite produções com mais de 2 elementos no lado direito.")

    def eh_vazia(self) -> bool:
        return len(self.direita) == 0 or (
            len(self.direita) == 1 
            and isinstance(self.direita[0], Terminal) 
            and self.direita[0].caractere in ("epsilon", "ε", "&")
        )

    def obter_tipo(self) -> TipoProducao:
        if self.eh_vazia():
            return TipoProducao.VAZIA
        if len(self.direita) == 1:
            if isinstance(self.direita[0], Terminal):
                return TipoProducao.TERMINAL
            else:
                raise ValueError("Regra inválida para gramática regular: A -> B não é permitido.")
        if len(self.direita) == 2:
            first, second = self.direita
            if isinstance(first, Terminal) and isinstance(second, Variavel):
                return TipoProducao.TERMINAL_VARIAVEL
            elif isinstance(first, Variavel) and isinstance(second, Terminal):
                return TipoProducao.VARIAVEL_TERMINAL
            else:
                raise ValueError("Regra inválida: Deve ter um terminal e uma variável.")
        raise ValueError("Estrutura de produção não reconhecida como regular.")

    def __str__(self) -> str:
        dir_str = "".join(str(x) for x in self.direita) if not self.eh_vazia() else "ε"
        return f"{self.esquerda} -> {dir_str}"
