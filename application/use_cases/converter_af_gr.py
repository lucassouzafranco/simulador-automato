from application.ports.repositorio_automato import AutomatonRepositoryPort
from application.ports.repositorio_gramatica import GrammarRepositoryPort
from core.ports.interfaces import DidacticTracePort
from application.dtos import (
    ConverterAFParaGRInputDTO,
    ConverterAFParaGROutputDTO,
    mapear_gramatica_para_dto,
    mapear_passos_didaticos,
)
from core.services.conversor_automato_gram import AutomatonToGrammarConverter

class ConverterAFParaGRUseCase:
    """Caso de uso responsável pela conversão didática de autômato para gramática regular."""
    
    def __init__(self, automaton_repo: AutomatonRepositoryPort, grammar_repo: GrammarRepositoryPort, trace_port: DidacticTracePort) -> None:
        self.automaton_repo = automaton_repo
        self.grammar_repo = grammar_repo
        self.trace_port = trace_port
        self.converter = AutomatonToGrammarConverter()

    def execute(self, dto: ConverterAFParaGRInputDTO) -> ConverterAFParaGROutputDTO:
        automato = self.automaton_repo.get_by_id(dto.id_automato)
        if not automato:
            raise ValueError(f"Autômato com ID {dto.id_automato} não encontrado.")

        gramatica = self.converter.converter(automato, self.trace_port)
        self.grammar_repo.save(gramatica)
        
        passos = mapear_passos_didaticos(self.trace_port.get_steps())
        
        return ConverterAFParaGROutputDTO(
            id_gramatica=gramatica.id,
            gramatica_dto=mapear_gramatica_para_dto(gramatica),
            passos_didaticos=passos
        )
