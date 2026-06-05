from core import Automato, GramaticaRegular, PassoDidatico
from application.dtos.automato import AutomatonOutputDTO, TransicaoDTO, PassoDidaticoDTO
from application.dtos.gramatica import GrammarOutputDTO, RegraProducaoDTO

def mapear_automato_para_dto(af: Automato) -> AutomatonOutputDTO:
    """Mapeia uma entidade Automato para seu respectivo DTO de saída."""
    return AutomatonOutputDTO(
        id=af.id,
        nome=af.nome,
        tipo=af.tipo.value,
        alfabeto=sorted(str(s) for s in af.alfabeto.simbolos),
        estados=sorted(str(e) for e in af.estados),
        estado_inicial=str(af.estado_inicial),
        estados_finais=sorted(str(e) for e in af.estados_finais),
        transicoes=[
            TransicaoDTO(origem=str(t.origem), simbolo=str(t.simbolo), destino=str(t.destino))
            for t in sorted(
                af.transicoes,
                key=lambda x: (str(x.origem), str(x.simbolo), str(x.destino))
            )
        ]
    )

def mapear_gramatica_para_dto(gr: GramaticaRegular) -> GrammarOutputDTO:
    """Mapeia uma entidade GramaticaRegular para seu respectivo DTO de saída."""
    return GrammarOutputDTO(
        id=gr.id,
        linearidade=gr.obter_linearidade().value,
        simbolo_inicial=str(gr.simbolo_inicial),
        variaveis=sorted(str(v) for v in gr.variaveis),
        terminais=sorted(str(t) for t in gr.terminais),
        producoes=[
            RegraProducaoDTO(esquerda=str(p.esquerda), direita=[str(x) for x in p.direita] if p.direita else ["ε"])
            for p in sorted(
                gr.producoes,
                key=lambda x: (str(x.esquerda), "".join(str(i) for i in x.direita))
            )
        ]
    )

def mapear_passos_didaticos(passos: list[PassoDidatico]) -> list[PassoDidaticoDTO]:
    """Mapeia passos didáticos do core para DTOs."""
    return [
        PassoDidaticoDTO(indice=p.indice, descricao=p.descricao, dados_calculo=p.dados_calculo)
        for p in passos
    ]
