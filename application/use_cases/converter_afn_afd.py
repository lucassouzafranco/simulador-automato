from application.ports.repositorio_automato import AutomatonRepositoryPort
from core.ports.interfaces import DidacticTracePort
from application.dtos import (
    ConverterAFNParaAFDInputDTO,
    ConverterAFNParaAFDOutputDTO,
    mapear_automato_para_dto,
    mapear_passos_didaticos,
)
from core.services.determinizador import NfaToDfaConverter
from core.entities.automato import AFN

class ConverterAFNParaAFDUseCase:
    """Caso de uso responsável pela conversão didática de um AFN para AFD."""
    
    def __init__(self, repository: AutomatonRepositoryPort, trace_port: DidacticTracePort) -> None:
        self.repository = repository
        self.trace_port = trace_port
        self.converter_service = NfaToDfaConverter()

    def execute(self, dto: ConverterAFNParaAFDInputDTO) -> ConverterAFNParaAFDOutputDTO:
        automato = self.repository.get_by_id(dto.id_automato)
        if not automato:
            raise ValueError(f"Autômato com ID {dto.id_automato} não encontrado.")
            
        if not isinstance(automato, AFN):
            raise ValueError("O autômato fornecido não é um AFN válido para determinização.")

        afd = self.converter_service.converter(automato, self.trace_port)
        self.repository.save(afd)

        passos = mapear_passos_didaticos(self.trace_port.get_steps())
        
        return ConverterAFNParaAFDOutputDTO(
            id_afd=afd.id,
            passos_didaticos=passos,
            automato_dto=mapear_automato_para_dto(afd)
        )
