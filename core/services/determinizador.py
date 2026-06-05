from typing import Optional, Any
from core.entities.automato import AFN, AFD, TipoAutomato
from core.value_objects.estado import Estado
from core.value_objects.simbolo import Simbolo
from core.value_objects.transicao import Transicao
from core.value_objects.passo_didatico import PassoDidatico
from core.ports.interfaces import DidacticTracePort

class NfaToDfaConverter:
    """
    Serviço de domínio responsável pela conversão de um AFN para um AFD
    utilizando a construção de subconjuntos.
    """
    def converter(self, afn: AFN, trace: Optional[DidacticTracePort] = None) -> AFD:
        if trace:
            trace.clean()
            trace.log_step(PassoDidatico(
                indice=1,
                descricao="Iniciando a determinização do AFN por construção de subconjuntos.",
                dados_calculo={"algoritmo": "Subset Construction"}
            ))

        # 1. Estado inicial do AFD é o fecho-epsilon do inicial do AFN
        q0_conjunto = afn.calcular_fecho_epsilon(frozenset([afn.estado_inicial]))
        if trace:
            trace.log_step(PassoDidatico(
                indice=2,
                descricao=f"Calculado fecho-epsilon do estado inicial do AFN ({afn.estado_inicial}): {self._frozenset_str(q0_conjunto)}.",
                dados_calculo={"estado_inicial_afn": str(afn.estado_inicial), "fecho_epsilon": [str(e) for e in q0_conjunto]}
            ))

        estado_map = {}  # frozenset[Estado] -> Estado
        q0_rotulo = self._format_subset_label(q0_conjunto)
        q0_afd = Estado(q0_rotulo)
        estado_map[q0_conjunto] = q0_afd

        from collections import deque
        estados_nao_marcados = deque([q0_conjunto])
        estados_afd = {q0_afd}
        transicoes_afd = set()

        passo_idx = 3
        while estados_nao_marcados:
            U = estados_nao_marcados.popleft()
            u_afd = estado_map[U]

            for s in afn.alfabeto.simbolos:
                # Obter transições diretas
                destinos = set()
                for est in U:
                    destinos.update(afn.obter_transicoes_partindo_de(est, s))
                
                # Obter fecho epsilon dos destinos
                T = afn.calcular_fecho_epsilon(frozenset(destinos))

                if not T:
                    continue

                if T not in estado_map:
                    t_rotulo = self._format_subset_label(T)
                    t_afd = Estado(t_rotulo)
                    estado_map[T] = t_afd
                    estados_nao_marcados.append(T)
                    estados_afd.add(t_afd)
                    if trace:
                        trace.log_step(PassoDidatico(
                            indice=passo_idx,
                            descricao=f"Descoberto novo subconjunto de estados sob o símbolo '{s}': {self._frozenset_str(T)} mapeado para o estado '{t_rotulo}'.",
                            dados_calculo={"simbolo": str(s), "subconjunto": [str(e) for e in T], "novo_estado": t_rotulo}
                        ))
                        passo_idx += 1
                else:
                    t_afd = estado_map[T]

                transicoes_afd.add(Transicao(origem=u_afd, simbolo=s, destino=t_afd))

        # Determinar estados finais
        estados_finais_afd = set()
        for subconjunto, est_afd in estado_map.items():
            finais_contidos = subconjunto.intersection(afn.estados_finais)
            if finais_contidos:
                estados_finais_afd.add(est_afd)
                if trace:
                    trace.log_step(PassoDidatico(
                        indice=passo_idx,
                        descricao=f"Estado '{est_afd}' é marcado como final porque seu subconjunto contém estados finais do AFN: {self._frozenset_str(finais_contidos)}.",
                        dados_calculo={"estado_afd": str(est_afd), "estados_finais_afn_contidos": [str(e) for e in finais_contidos]}
                    ))
                    passo_idx += 1

        if trace:
            trace.log_step(PassoDidatico(
                indice=passo_idx,
                descricao="Determinização concluída com sucesso.",
                dados_calculo={}
            ))

        return AFD(
            nome=f"AFD_equivalente_{afn.nome}",
            tipo=TipoAutomato.DFA,
            alfabeto=afn.alfabeto,
            estados=frozenset(estados_afd),
            estado_inicial=q0_afd,
            estados_finais=frozenset(estados_finais_afd),
            transicoes=frozenset(transicoes_afd)
        )

    def _natural_sort_key(self, obj: Any) -> list:
        import re
        s = str(obj)
        return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]

    def _frozenset_str(self, fs: frozenset) -> str:
        return f"{{{', '.join(str(x) for x in sorted(fs, key=self._natural_sort_key))}}}"

    def _format_subset_label(self, fs: frozenset) -> str:
        if not fs:
            return "vazio"
        sorted_labels = [str(x) for x in sorted(fs, key=self._natural_sort_key)]
        return f"{{{','.join(sorted_labels)}}}"
