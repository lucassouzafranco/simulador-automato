import asyncio
from typing import List
from core import DidacticTracePort, PassoDidatico

class AsyncQueueTraceAdapter(DidacticTracePort):
    """
    Adaptador de rastreamento didático que envia os passos para uma fila assíncrona (asyncio.Queue).
    Permite a comunicação segura entre a thread de processamento do Caso de Uso (síncrona)
    e o loop de eventos principal do FastAPI (assíncrono).
    """
    def __init__(self, loop: asyncio.AbstractEventLoop, queue: asyncio.Queue) -> None:
        self.loop = loop
        self.queue = queue
        self.steps: List[PassoDidatico] = []

    def log_step(self, step: PassoDidatico) -> None:
        """Registra o passo localmente e enfileira no loop de eventos assíncrono de forma thread-safe."""
        self.steps.append(step)
        self.loop.call_soon_threadsafe(self.queue.put_nowait, step)

    def get_steps(self) -> List[PassoDidatico]:
        """Recupera os passos didáticos gravados localmente."""
        return self.steps

    def clean(self) -> None:
        """Limpa a lista interna de passos."""
        self.steps.clear()
