from application.ports.repositorio_automato import AutomatonRepositoryPort
from application.ports.repositorio_gramatica import GrammarRepositoryPort
from application.ports.exportador import ExporterPort
from application.dtos import ExportarResultadoInputDTO, ExportarResultadoOutputDTO
from typing import Dict

class ExportarResultadoUseCase:
    """Caso de uso responsável por exportar autômatos ou gramáticas regulares."""
    
    def __init__(
        self,
        automaton_repo: AutomatonRepositoryPort,
        grammar_repo: GrammarRepositoryPort,
        exporters: Dict[str, ExporterPort],
    ) -> None:
        self.automaton_repo = automaton_repo
        self.grammar_repo = grammar_repo
        self.exporters = exporters

    def execute(self, dto: ExportarResultadoInputDTO) -> ExportarResultadoOutputDTO:
        formato = dto.formato.upper()
        exporter = self.exporters.get(formato)
        if not exporter:
            raise ValueError(f"Formato de exportação '{dto.formato}' não suportado.")

        tipo = dto.tipo_entidade.upper()
        if tipo == "AUTOMATO":
            entidade = self.automaton_repo.get_by_id(dto.id_entidade)
            if not entidade:
                raise ValueError(f"Autômato com ID {dto.id_entidade} não encontrado.")
        elif tipo == "GRAMATICA":
            entidade = self.grammar_repo.get_by_id(dto.id_entidade)
            if not entidade:
                raise ValueError(f"Gramática com ID {dto.id_entidade} não encontrada.")
        else:
            raise ValueError(f"Tipo de entidade '{dto.tipo_entidade}' inválido. Deve ser 'AUTOMATO' ou 'GRAMATICA'.")

        conteudo = exporter.export(entidade)
        
        return ExportarResultadoOutputDTO(
            conteudo=conteudo,
            caminho_arquivo=None
        )
