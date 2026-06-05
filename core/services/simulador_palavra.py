from typing import Optional
from core.entities.automato import Automato, AFD, AFN
from core.value_objects.palavra import Palavra
from core.value_objects.passo_didatico import PassoDidatico
from core.ports.interfaces import DidacticTracePort

class WordSimulator:
    """
    Serviço de domínio responsável pela simulação passo-a-passo de uma cadeia de símbolos
    em um autômato (AFD ou AFN), registrando os caminhos didáticos.
    """
    def simular(self, automato: Automato, palavra: Palavra, trace: Optional[DidacticTracePort] = None) -> bool:
        if trace:
            trace.clean()
            trace.log_step(PassoDidatico(
                indice=1,
                descricao=f"Iniciando simulação da palavra '{palavra.como_texto()}' no autômato '{automato.nome}'.",
                dados_calculo={"palavra": palavra.como_texto(), "comprimento": palavra.obter_comprimento()}
            ))

        if isinstance(automato, AFD):
            return self._simular_afd(automato, palavra, trace)
        elif isinstance(automato, AFN):
            return self._simular_afn(automato, palavra, trace)
        else:
            raise ValueError("Tipo de autômato não suportado para simulação.")

    def _simular_afd(self, afd: AFD, palavra: Palavra, trace: Optional[DidacticTracePort]) -> bool:
        curr = afd.estado_inicial
        passo_idx = 2

        for idx, s in enumerate(palavra.sequencia):
            if not afd.alfabeto.contem(s):
                if trace:
                    trace.log_step(PassoDidatico(
                        indice=passo_idx,
                        descricao=f"Erro: Símbolo '{s}' não pertence ao alfabeto do autômato.",
                        dados_calculo={"simbolo_invalido": str(s)}
                    ))
                return False

            next_state = afd.obter_transicao_determinista(curr, s)
            
            if next_state is None:
                if trace:
                    trace.log_step(PassoDidatico(
                        indice=passo_idx,
                        descricao=f"Rejeitado: Não existe transição a partir de '{curr}' sob o símbolo '{s}'.",
                        dados_calculo={"origem": str(curr), "simbolo": str(s)}
                    ))
                return False

            if trace:
                trace.log_step(PassoDidatico(
                    indice=passo_idx,
                    descricao=f"Consumindo símbolo '{s}': Transição de '{curr}' para '{next_state}'.",
                    dados_calculo={
                        "posicao_palavra": idx,
                        "simbolo": str(s),
                        "origem": str(curr),
                        "destino": str(next_state)
                    }
                ))
            curr = next_state
            passo_idx += 1

        aceita = curr in afd.estados_finais
        if trace:
            status = "ACEITA" if aceita else "REJEITADA"
            trace.log_step(PassoDidatico(
                indice=passo_idx,
                descricao=f"Palavra concluída. Estado final: '{curr}'. A palavra foi {status}.",
                dados_calculo={"estado_final": str(curr), "resultado": status}
            ))

        return aceita

    def _simular_afn(self, afn: AFN, palavra: Palavra, trace: Optional[DidacticTracePort]) -> bool:
        ativos = afn.calcular_fecho_epsilon(frozenset([afn.estado_inicial]))
        passo_idx = 2

        if trace:
            trace.log_step(PassoDidatico(
                indice=passo_idx,
                descricao=f"Estados ativos iniciais (fecho-epsilon de {afn.estado_inicial}): {self._conjunto_str(ativos)}.",
                dados_calculo={"ativos_iniciais": [str(e) for e in ativos]}
            ))
            passo_idx += 1

        for idx, s in enumerate(palavra.sequencia):
            if not afn.alfabeto.contem(s):
                if trace:
                    trace.log_step(PassoDidatico(
                        indice=passo_idx,
                        descricao=f"Erro: Símbolo '{s}' não pertence ao alfabeto do autômato.",
                        dados_calculo={"simbolo_invalido": str(s)}
                    ))
                return False

            proximos = set()
            for est in ativos:
                proximos.update(afn.obter_transicoes_partindo_de(est, s))
            
            ativos = afn.calcular_fecho_epsilon(frozenset(proximos))

            if not ativos:
                if trace:
                    trace.log_step(PassoDidatico(
                        indice=passo_idx,
                        descricao=f"Consumindo símbolo '{s}': Nenhum estado ativo restante. Simulação rejeitada.",
                        dados_calculo={"posicao_palavra": idx, "simbolo": str(s), "ativos": []}
                    ))
                return False

            if trace:
                trace.log_step(PassoDidatico(
                    indice=passo_idx,
                    descricao=f"Consumindo símbolo '{s}': Próximos estados ativos: {self._conjunto_str(ativos)}.",
                    dados_calculo={
                        "posicao_palavra": idx,
                        "simbolo": str(s),
                        "ativos": [str(e) for e in ativos]
                    }
                ))
            passo_idx += 1

        finais_ativos = ativos.intersection(afn.estados_finais)
        aceita = len(finais_ativos) > 0

        if trace:
            status = "ACEITA" if aceita else "REJEITADA"
            trace.log_step(PassoDidatico(
                indice=passo_idx,
                descricao=f"Palavra concluída. Estados ativos finais: {self._conjunto_str(ativos)}. A palavra foi {status}.",
                dados_calculo={
                    "ativos_finais": [str(e) for e in ativos],
                    "finais_ativos_alcancados": [str(e) for e in finais_ativos],
                    "resultado": status
                }
            ))

        return aceita

    def _conjunto_str(self, fs: frozenset) -> str:
        return f"{{{', '.join(sorted(str(x) for x in fs))}}}"
