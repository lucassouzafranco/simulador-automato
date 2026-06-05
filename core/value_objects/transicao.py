from dataclasses import dataclass
from core.value_objects.estado import Estado
from core.value_objects.simbolo import Simbolo

@dataclass(frozen=True, slots=True)
class Transicao:
    origem: Estado
    simbolo: Simbolo
    destino: Estado

    @property
    def eh_epsilon(self) -> bool:
        return self.simbolo.eh_epsilon

    def __str__(self) -> str:
        return f"({self.origem} -- {self.simbolo} --> {self.destino})"
