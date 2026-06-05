from typing import Optional
from core.entities.automato import Automato
from core.entities.gramatica import GramaticaRegular
from core.value_objects.regra_producao import RegraProducao, Variavel, Terminal
from core.value_objects.passo_didatico import PassoDidatico
from core.ports.interfaces import DidacticTracePort

class AutomatonToGrammarConverter:
    """
    Serviço de domínio responsável por converter um Autômato Finito (AFD/AFN)
    em uma Gramática Regular equivalente.
    """
    def converter(self, automato: Automato, trace: Optional[DidacticTracePort] = None) -> GramaticaRegular:
        if trace:
            trace.clean()
            trace.log_step(PassoDidatico(
                indice=1,
                descricao=f"Iniciando conversão do autômato '{automato.nome}' para Gramática Regular.",
                dados_calculo={}
            ))

        # Mapear estados para variáveis não-terminais
        var_map = {}  # Estado -> Variavel
        variaveis = set()
        for est in automato.estados:
            var = Variavel(est.rotulo)
            var_map[est] = var
            variaveis.add(var)

        # Mapear alfabeto para símbolos terminais
        terminais = set(Terminal(s.valor) for s in automato.alfabeto.simbolos)

        producoes = set()
        passo_idx = 2

        # Transições -> Regras de Produção (A -> aB)
        for t in automato.transicoes:
            orig = var_map[t.origem]
            term = Terminal(t.simbolo.valor)
            dest = var_map[t.destino]
            
            prod = RegraProducao(esquerda=orig, direita=(term, dest))
            producoes.add(prod)
            
            if trace:
                trace.log_step(PassoDidatico(
                    indice=passo_idx,
                    descricao=f"Transição ({t.origem} -- {t.simbolo} --> {t.destino}) convertida em regra: '{prod}'.",
                    dados_calculo={"transicao": str(t), "producao": str(prod)}
                ))
                passo_idx += 1

        # Estados Finais -> Regras de Produção (A -> epsilon)
        for est_f in automato.estados_finais:
            orig = var_map[est_f]
            eps = Terminal("ε")
            prod = RegraProducao(esquerda=orig, direita=(eps,))
            producoes.add(prod)
            
            if trace:
                trace.log_step(PassoDidatico(
                    indice=passo_idx,
                    descricao=f"Estado final '{est_f}' gera produção vazia de parada: '{prod}'.",
                    dados_calculo={"estado_final": str(est_f), "producao": str(prod)}
                ))
                passo_idx += 1

        # Tratar restrição do símbolo inicial produzindo epsilon
        if automato.estado_inicial in automato.estados_finais:
            rotulo_novo = "S_start"
            while any(v.rotulo == rotulo_novo for v in variaveis):
                rotulo_novo += "_"
            simbolo_inicial = Variavel(rotulo_novo)
            variaveis.add(simbolo_inicial)
            
            # Adicionar S_start -> ε
            eps = Terminal("ε")
            producoes.add(RegraProducao(esquerda=simbolo_inicial, direita=(eps,)))
            
            # Adicionar cópias das regras de saída do inicial original
            for t in automato.transicoes:
                if t.origem == automato.estado_inicial:
                    term = Terminal(t.simbolo.valor)
                    dest = var_map[t.destino]
                    prod_copia = RegraProducao(esquerda=simbolo_inicial, direita=(term, dest))
                    producoes.add(prod_copia)
            
            if trace:
                trace.log_step(PassoDidatico(
                    indice=passo_idx,
                    descricao=f"Estado inicial '{automato.estado_inicial}' é final. Criada nova variável inicial '{simbolo_inicial}' para evitar que apareça no lado direito das produções.",
                    dados_calculo={"nova_variavel_inicial": str(simbolo_inicial)}
                ))
                passo_idx += 1
        else:
            simbolo_inicial = var_map[automato.estado_inicial]

        if trace:
            trace.log_step(PassoDidatico(
                indice=passo_idx,
                descricao="Conversão concluída com sucesso.",
                dados_calculo={}
            ))

        return GramaticaRegular(
            variaveis=frozenset(variaveis),
            terminais=frozenset(terminais),
            simbolo_inicial=simbolo_inicial,
            producoes=frozenset(producoes)
        )
