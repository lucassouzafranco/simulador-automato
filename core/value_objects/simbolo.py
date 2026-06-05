from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Simbolo:
    valor: str

    def __post_init__(self) -> None:
        if not self.valor:
            raise ValueError("O valor de um símbolo não pode ser vazio.")
        # Permitir epsilon em diferentes formas clássicas
        if len(self.valor) != 1 and self.valor not in ("epsilon", "ε", "&"):
            raise ValueError("Um símbolo do alfabeto deve ter exatamente 1 caractere.")

    @property
    def eh_epsilon(self) -> bool:
        return self.valor in ("epsilon", "ε", "&")

    @classmethod
    def epsilon(cls) -> "Simbolo":
        return cls("ε")

    def __str__(self) -> str:
        return self.valor
