from application.dtos import (
    PassoDidaticoDTO,
    TransicaoDTO,
    CriarAFNInputDTO,
    CriarAFNOutputDTO,
    AutomatonOutputDTO,
    ConverterAFNParaAFDInputDTO,
    ConverterAFNParaAFDOutputDTO,
    MinimizarAFDInputDTO,
    MinimizarAFDOutputDTO,
    RegraProducaoDTO,
    GrammarOutputDTO,
    ConverterAFParaGRInputDTO,
    ConverterAFParaGROutputDTO,
    ConverterGRParaAFInputDTO,
    ConverterGRParaAFOutputDTO,
    SimularPalavraInputDTO,
    SimularPalavraOutputDTO,
    ExportarResultadoInputDTO,
    ExportarResultadoOutputDTO,
    mapear_automato_para_dto,
    mapear_gramatica_para_dto,
    mapear_passos_didaticos,
)
from application.ports import (
    AutomatonRepositoryPort,
    GrammarRepositoryPort,
    ExporterPort,
)
from application.use_cases import (
    CriarAFNUseCase,
    ConverterAFNParaAFDUseCase,
    SimularPalavraUseCase,
    MinimizarAFDUseCase,
    ConverterAFParaGRUseCase,
    ConverterGRParaAFUseCase,
    ExportarResultadoUseCase,
)

__all__ = [
    # DTOs
    "PassoDidaticoDTO",
    "TransicaoDTO",
    "CriarAFNInputDTO",
    "CriarAFNOutputDTO",
    "AutomatonOutputDTO",
    "ConverterAFNParaAFDInputDTO",
    "ConverterAFNParaAFDOutputDTO",
    "MinimizarAFDInputDTO",
    "MinimizarAFDOutputDTO",
    
    "RegraProducaoDTO",
    "GrammarOutputDTO",
    "ConverterAFParaGRInputDTO",
    "ConverterAFParaGROutputDTO",
    "ConverterGRParaAFInputDTO",
    "ConverterGRParaAFOutputDTO",
    
    "SimularPalavraInputDTO",
    "SimularPalavraOutputDTO",
    
    "ExportarResultadoInputDTO",
    "ExportarResultadoOutputDTO",
    
    "mapear_automato_para_dto",
    "mapear_gramatica_para_dto",
    "mapear_passos_didaticos",
    
    # Ports
    "AutomatonRepositoryPort",
    "GrammarRepositoryPort",
    "ExporterPort",
    
    # Use Cases
    "CriarAFNUseCase",
    "ConverterAFNParaAFDUseCase",
    "SimularPalavraUseCase",
    "MinimizarAFDUseCase",
    "ConverterAFParaGRUseCase",
    "ConverterGRParaAFUseCase",
    "ExportarResultadoUseCase",
]
