from abc import ABC, abstractmethod
from core.value_objects.passo_didatico import PassoDidatico

class DidacticTracePort(ABC):
    """
    Interface para o rastreador didático de passos.
    Permite que os algoritmos de domínio gravem explicações passo a passo
    da execução dos cálculos teóricos.
    """
    @abstractmethod
    def log_step(self, step: PassoDidatico) -> None:
        """Registra um novo passo de execução didática."""
        pass

    @abstractmethod
    def get_steps(self) -> list[PassoDidatico]:
        """Recupera todos os passos didáticos gravados."""
        pass

    @abstractmethod
    def clean(self) -> None:
        """Limpa a pilha de passos registrados."""
        pass
