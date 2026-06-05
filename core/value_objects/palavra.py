from dataclasses import dataclass
from core.value_objects.simbolo import Simbolo

@dataclass(frozen=True, slots=True)
class Palavra:
    sequencia: tuple[Simbolo, ...]

    def __post_init__(self) -> None:
        for s in self.sequencia:
            if s.eh_epsilon:
                raise ValueError("Uma palavra de entrada não pode conter o símbolo vazio epsilon em sua sequência.")

    def obter_comprimento(self) -> int:
        return len(self.sequencia)

    def como_texto(self) -> str:
        return "".join(s.valor for s in self.sequencia)

    @classmethod
    def vazia(cls) -> "Palavra":
        return cls(tuple())

    @classmethod
    def de_string(cls, texto: str) -> "Palavra":
        if not texto:
            return cls.vazia()
        return cls(tuple(Simbolo(c) for c in texto))

    def __str__(self) -> str:
        return self.como_texto() if self.sequencia else "ε"
