from application.ports.repositorio_automato import AutomatonRepositoryPort
from core.ports.interfaces import DidacticTracePort
from application.dtos import (
    MinimizarAFDInputDTO,
    MinimizarAFDOutputDTO,
    mapear_automato_para_dto,
    mapear_passos_didaticos,
)
from core.services.minimizador import DfaMinimizer
from core.entities.automato import AFD

class MinimizarAFDUseCase:
    """Caso de uso responsável pela minimização didática de um AFD."""
    
    def __init__(self, repository: AutomatonRepositoryPort, trace_port: DidacticTracePort) -> None:
        self.repository = repository
        self.trace_port = trace_port
        self.minimizer = DfaMinimizer()

    def execute(self, dto: MinimizarAFDInputDTO) -> MinimizarAFDOutputDTO:
        automato = self.repository.get_by_id(dto.id_automato)
        if not automato:
            raise ValueError(f"Autômato com ID {dto.id_automato} não encontrado.")
            
        if not isinstance(automato, AFD):
            raise ValueError("Minimização requer um autômato determinista (AFD).")

        afd_min = self.minimizer.minimizar(automato, self.trace_port)
        self.repository.save(afd_min)
        
        passos = mapear_passos_didaticos(self.trace_port.get_steps())
        
        return MinimizarAFDOutputDTO(
            id_afd_minimizado=afd_min.id,
            passos_didaticos=passos,
            automato_dto=mapear_automato_para_dto(afd_min)
        )
