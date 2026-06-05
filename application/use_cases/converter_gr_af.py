from application.ports.repositorio_automato import AutomatonRepositoryPort
from application.ports.repositorio_gramatica import GrammarRepositoryPort
from core.ports.interfaces import DidacticTracePort
from application.dtos import (
    ConverterGRParaAFInputDTO,
    ConverterGRParaAFOutputDTO,
    mapear_automato_para_dto,
    mapear_passos_didaticos,
)
from core.services.conversor_gram_automato import GrammarToAutomatonConverter

class ConverterGRParaAFUseCase:
    """Caso de uso responsável pela conversão didática de gramática regular para AFN."""
    
    def __init__(self, automaton_repo: AutomatonRepositoryPort, grammar_repo: GrammarRepositoryPort, trace_port: DidacticTracePort) -> None:
        self.automaton_repo = automaton_repo
        self.grammar_repo = grammar_repo
        self.trace_port = trace_port
        self.converter = GrammarToAutomatonConverter()

    def execute(self, dto: ConverterGRParaAFInputDTO) -> ConverterGRParaAFOutputDTO:
        gramatica = self.grammar_repo.get_by_id(dto.id_gramatica)
        if not gramatica:
            raise ValueError(f"Gramática com ID {dto.id_gramatica} não encontrada.")

        afn = self.converter.converter(gramatica, self.trace_port)
        self.automaton_repo.save(afn)
        
        passos = mapear_passos_didaticos(self.trace_port.get_steps())
        
        return ConverterGRParaAFOutputDTO(
            id_automato=afn.id,
            automato_dto=mapear_automato_para_dto(afn),
            passos_didaticos=passos
        )
