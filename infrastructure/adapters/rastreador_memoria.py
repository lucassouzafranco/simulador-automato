from core.ports.interfaces import DidacticTracePort
from core.value_objects.passo_didatico import PassoDidatico

class InMemoryDidacticTraceAdapter(DidacticTracePort):
    """Adaptador concreto para gravação didática de passos na memória RAM."""
    
    def __init__(self) -> None:
        self._steps: list[PassoDidatico] = []

    def log_step(self, step: PassoDidatico) -> None:
        self._steps.append(step)

    def get_steps(self) -> list[PassoDidatico]:
        return self._steps

    def clean(self) -> None:
        self._steps.clear()
