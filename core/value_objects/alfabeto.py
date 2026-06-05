from dataclasses import dataclass
from core.value_objects.simbolo import Simbolo

@dataclass(frozen=True, slots=True)
class Alfabeto:
    simbolos: frozenset[Simbolo]

    def __post_init__(self) -> None:
        if not self.simbolos:
            raise ValueError("O alfabeto não pode ser vazio.")
        for s in self.simbolos:
            if s.eh_epsilon:
                raise ValueError("O símbolo vazio (epsilon) não pode pertencer ao alfabeto formal.")

    def contem(self, simbolo: Simbolo) -> bool:
        return simbolo in self.simbolos

    def __str__(self) -> str:
        return f"{{{', '.join(sorted(str(s) for s in self.simbolos))}}}"
