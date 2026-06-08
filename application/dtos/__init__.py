from application.dtos.automato import (
    PassoDidaticoDTO,
    TransicaoDTO,
    CriarAFNInputDTO,
    CriarAFNOutputDTO,
    AutomatonOutputDTO,
    ConverterAFNParaAFDInputDTO,
    ConverterAFNParaAFDOutputDTO,
    MinimizarAFDInputDTO,
    MinimizarAFDOutputDTO,
)
from application.dtos.gramatica import (
    RegraProducaoDTO,
    GrammarOutputDTO,
    ConverterAFParaGRInputDTO,
    ConverterAFParaGROutputDTO,
    ConverterGRParaAFInputDTO,
    ConverterGRParaAFOutputDTO,
)
from application.dtos.simula import (
    SimularPalavraInputDTO,
    SimularPalavraOutputDTO,
)
from application.dtos.mapeadores import (
    mapear_automato_para_dto,
    mapear_gramatica_para_dto,
    mapear_passos_didaticos,
)

__all__ = [
    # Automato
    "PassoDidaticoDTO",
    "TransicaoDTO",
    "CriarAFNInputDTO",
    "CriarAFNOutputDTO",
    "AutomatonOutputDTO",
    "ConverterAFNParaAFDInputDTO",
    "ConverterAFNParaAFDOutputDTO",
    "MinimizarAFDInputDTO",
    "MinimizarAFDOutputDTO",
    
    # Gramatica
    "RegraProducaoDTO",
    "GrammarOutputDTO",
    "ConverterAFParaGRInputDTO",
    "ConverterAFParaGROutputDTO",
    "ConverterGRParaAFInputDTO",
    "ConverterGRParaAFOutputDTO",
    
    # Simula
    "SimularPalavraInputDTO",
    "SimularPalavraOutputDTO",
    
    # Mapeadores
    "mapear_automato_para_dto",
    "mapear_gramatica_para_dto",
    "mapear_passos_didaticos",
]
