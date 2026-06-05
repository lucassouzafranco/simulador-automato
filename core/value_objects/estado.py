from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Estado:
    rotulo: str

    def __post_init__(self) -> None:
        if not self.rotulo:
            raise ValueError("O rótulo de um estado não pode ser vazio.")

    def eh_composto(self) -> bool:
        return "," in self.rotulo or "{" in self.rotulo or "_" in self.rotulo

    def obter_estados_de_origem(self) -> frozenset[str]:
        cleaned = self.rotulo.strip("{}")
        if "," in cleaned:
            return frozenset(s.strip() for s in cleaned.split(",") if s.strip())
        if "_" in cleaned:
            return frozenset(s.strip() for s in cleaned.split("_") if s.strip())
        return frozenset([cleaned])

    def __str__(self) -> str:
        return self.rotulo
