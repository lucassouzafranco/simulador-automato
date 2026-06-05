from typing import Union
from application.ports.exportador import ExporterPort
from core.entities.automato import Automato
from core.entities.gramatica import GramaticaRegular, TipoLinearidade

class TxtExporter(ExporterPort):
    """Implementação concreta de exportador em formato texto amigável (.txt)."""
    
    def export(self, entidade: Union[Automato, GramaticaRegular]) -> str:
        if isinstance(entidade, Automato):
            return self._export_automaton(entidade)
        elif isinstance(entidade, GramaticaRegular):
            return self._export_grammar(entidade)
        else:
            raise TypeError("Tipo de entidade não suportado para exportação em texto.")

    def _export_automaton(self, af: Automato) -> str:
        linhas = []
        linhas.append(f"Nome: {af.nome}")
        linhas.append(f"Tipo: {af.tipo.value}")
        
        simbolos_sorted = sorted(str(s) for s in af.alfabeto.simbolos)
        linhas.append(f"Alfabeto: {{{', '.join(simbolos_sorted)}}}")
        
        estados_sorted = sorted(str(e) for e in af.estados)
        linhas.append(f"Estados: {{{', '.join(estados_sorted)}}}")
        
        linhas.append(f"Estado Inicial: {af.estado_inicial}")
        
        finais_sorted = sorted(str(e) for e in af.estados_finais)
        linhas.append(f"Estados Finais: {{{', '.join(finais_sorted)}}}")
        
        linhas.append("Transições:")
        trans_sorted = sorted(
            af.transicoes,
            key=lambda t: (str(t.origem), str(t.simbolo), str(t.destino))
        )
        for t in trans_sorted:
            linhas.append(f"  {t.origem} -- {t.simbolo} --> {t.destino}")
            
        return "\n".join(linhas)

    def _export_grammar(self, gr: GramaticaRegular) -> str:
        linhas = []
        linear_str = "linear à direita" if gr.obter_linearidade() == TipoLinearidade.DIREITA else "linear à esquerda"
        linhas.append(f"Gramática Regular ({linear_str})")
        linhas.append(f"Símbolo Inicial: {gr.simbolo_inicial}")
        
        var_sorted = sorted(str(v) for v in gr.variaveis)
        linhas.append(f"Variáveis: {{{', '.join(var_sorted)}}}")
        
        term_sorted = sorted(str(t) for t in gr.terminais)
        linhas.append(f"Terminais: {{{', '.join(term_sorted)}}}")
        
        linhas.append("Regras de Produção:")
        prod_sorted = sorted(
            gr.producoes,
            key=lambda p: (str(p.esquerda), "".join(str(x) for x in p.direita))
        )
        for p in prod_sorted:
            linhas.append(f"  {p}")
            
        return "\n".join(linhas)
