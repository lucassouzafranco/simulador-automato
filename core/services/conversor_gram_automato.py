from typing import Optional
from core.entities.gramatica import GramaticaRegular, TipoLinearidade
from core.entities.automato import AFN, TipoAutomato
from core.value_objects.estado import Estado
from core.value_objects.simbolo import Simbolo
from core.value_objects.transicao import Transicao
from core.value_objects.alfabeto import Alfabeto
from core.value_objects.passo_didatico import PassoDidatico
from core.ports.interfaces import DidacticTracePort
from core.value_objects.regra_producao import TipoProducao

class GrammarToAutomatonConverter:
    """
    Serviço de domínio responsável por converter uma Gramática Regular (linear
    à direita ou à esquerda) em um AFN equivalente.
    """
    def converter(self, gramatica: GramaticaRegular, trace: Optional[DidacticTracePort] = None) -> AFN:
        if trace:
            trace.clean()
            trace.log_step(PassoDidatico(
                indice=1,
                descricao="Iniciando conversão de Gramática Regular para AFN.",
                dados_calculo={"linearidade": gramatica.obter_linearidade().name}
            ))

        linearidade = gramatica.obter_linearidade()
        if linearidade == TipoLinearidade.DIREITA:
            return self._converter_linear_direita(gramatica, trace)
        else:
            return self._converter_linear_esquerda(gramatica, trace)

    def _converter_linear_direita(self, gramatica: GramaticaRegular, trace: Optional[DidacticTracePort]) -> AFN:
        estados = set(Estado(v.rotulo) for v in gramatica.variaveis)
        q_acc = Estado("q_acc")
        estados.add(q_acc)

        simbolos = set(Simbolo(t.caractere) for t in gramatica.terminais)
        alfabeto = Alfabeto(frozenset(simbolos))

        estado_inicial = Estado(gramatica.simbolo_inicial.rotulo)
        estados_finais = {q_acc}
        transicoes = set()
        passo_idx = 2

        for p in gramatica.producoes:
            orig = Estado(p.esquerda.rotulo)
            tipo = p.obter_tipo()

            if tipo == TipoProducao.TERMINAL_VARIAVEL:
                term = Simbolo(p.direita[0].caractere)
                dest = Estado(p.direita[1].rotulo)
                trans = Transicao(origem=orig, simbolo=term, destino=dest)
                transicoes.add(trans)
                if trace:
                    trace.log_step(PassoDidatico(
                        indice=passo_idx,
                        descricao=f"Produção '{p}' gerou transição: {trans}.",
                        dados_calculo={"producao": str(p), "transicao": str(trans)}
                    ))
                    passo_idx += 1

            elif tipo == TipoProducao.TERMINAL:
                term = Simbolo(p.direita[0].caractere)
                trans = Transicao(origem=orig, simbolo=term, destino=q_acc)
                transicoes.add(trans)
                if trace:
                    trace.log_step(PassoDidatico(
                        indice=passo_idx,
                        descricao=f"Produção '{p}' (terminal) gerou transição para aceitação '{q_acc}': {trans}.",
                        dados_calculo={"producao": str(p), "transicao": str(trans)}
                    ))
                    passo_idx += 1

            elif tipo == TipoProducao.VAZIA:
                estados_finais.add(orig)
                if trace:
                    trace.log_step(PassoDidatico(
                        indice=passo_idx,
                        descricao=f"Produção vazia '{p}' marcou o estado '{orig}' como final.",
                        dados_calculo={"producao": str(p), "estado_final": str(orig)}
                    ))
                    passo_idx += 1

        if trace:
            trace.log_step(PassoDidatico(
                indice=passo_idx,
                descricao="Conversão de gramática linear à direita para AFN concluída.",
                dados_calculo={}
            ))

        return AFN(
            nome="AFN_da_Gramatica_Regular",
            tipo=TipoAutomato.E_NFA,
            alfabeto=alfabeto,
            estados=frozenset(estados),
            estado_inicial=estado_inicial,
            estados_finais=frozenset(estados_finais),
            transicoes=frozenset(transicoes)
        )

    def _converter_linear_esquerda(self, gramatica: GramaticaRegular, trace: Optional[DidacticTracePort]) -> AFN:
        estados = set(Estado(v.rotulo) for v in gramatica.variaveis)
        q_init = Estado("q_init")
        estados.add(q_init)

        simbolos = set(Simbolo(t.caractere) for t in gramatica.terminais)
        alfabeto = Alfabeto(frozenset(simbolos))

        estado_inicial = q_init
        estados_finais = {Estado(gramatica.simbolo_inicial.rotulo)}
        transicoes = set()
        passo_idx = 2

        for p in gramatica.producoes:
            dest = Estado(p.esquerda.rotulo)
            tipo = p.obter_tipo()

            if tipo == TipoProducao.VARIAVEL_TERMINAL:
                orig = Estado(p.direita[0].rotulo)
                term = Simbolo(p.direita[1].caractere)
                trans = Transicao(origem=orig, simbolo=term, destino=dest)
                transicoes.add(trans)
                if trace:
                    trace.log_step(PassoDidatico(
                        indice=passo_idx,
                        descricao=f"Produção linear à esquerda '{p}' gerou transição reversa: {trans}.",
                        dados_calculo={"producao": str(p), "transicao": str(trans)}
                    ))
                    passo_idx += 1

            elif tipo == TipoProducao.TERMINAL:
                term = Simbolo(p.direita[0].caractere)
                trans = Transicao(origem=q_init, simbolo=term, destino=dest)
                transicoes.add(trans)
                if trace:
                    trace.log_step(PassoDidatico(
                        indice=passo_idx,
                        descricao=f"Produção '{p}' (terminal) gerou transição a partir do inicial '{q_init}': {trans}.",
                        dados_calculo={"producao": str(p), "transicao": str(trans)}
                    ))
                    passo_idx += 1

            elif tipo == TipoProducao.VAZIA:
                eps = Simbolo.epsilon()
                trans = Transicao(origem=q_init, simbolo=eps, destino=dest)
                transicoes.add(trans)
                if trace:
                    trace.log_step(PassoDidatico(
                        indice=passo_idx,
                        descricao=f"Produção vazia '{p}' gerou transição epsilon a partir do inicial '{q_init}': {trans}.",
                        dados_calculo={"producao": str(p), "transicao": str(trans)}
                    ))
                    passo_idx += 1

        if trace:
            trace.log_step(PassoDidatico(
                indice=passo_idx,
                descricao="Conversão de gramática linear à esquerda para AFN concluída.",
                dados_calculo={}
            ))

        return AFN(
            nome="AFN_da_Gramatica_Regular",
            tipo=TipoAutomato.E_NFA,
            alfabeto=alfabeto,
            estados=frozenset(estados),
            estado_inicial=estado_inicial,
            estados_finais=frozenset(estados_finais),
            transicoes=frozenset(transicoes)
        )
