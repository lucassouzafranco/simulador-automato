from application.ports.repositorio_automato import AutomatonRepositoryPort
from core.ports.interfaces import DidacticTracePort
from application.dtos import (
    SimularPalavraInputDTO,
    SimularPalavraOutputDTO,
    mapear_passos_didaticos,
)
from core.services.simulador_palavra import WordSimulator
from core.value_objects.palavra import Palavra

class SimularPalavraUseCase:
    """Caso de uso responsável por simular o processamento de uma palavra em um autômato."""
    
    def __init__(self, repository: AutomatonRepositoryPort, trace_port: DidacticTracePort) -> None:
        self.repository = repository
        self.trace_port = trace_port
        self.simulator = WordSimulator()

    def execute(self, dto: SimularPalavraInputDTO) -> SimularPalavraOutputDTO:
        automato = self.repository.get_by_id(dto.id_automato)
        if not automato:
            raise ValueError(f"Autômato com ID {dto.id_automato} não encontrado.")
            
        palavra = Palavra.de_string(dto.palavra)
        aceita = self.simulator.simular(automato, palavra, self.trace_port)
        
        passos = mapear_passos_didaticos(self.trace_port.get_steps())
        
        return SimularPalavraOutputDTO(
            aceita=aceita,
            passos_didaticos=passos
        )
