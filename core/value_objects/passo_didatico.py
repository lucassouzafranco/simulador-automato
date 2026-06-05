from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True, slots=True)
class PassoDidatico:
    indice: int
    descricao: str
    dados_calculo: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"Passo {self.indice}: {self.descricao}"
