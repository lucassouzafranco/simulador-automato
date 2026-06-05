from typing import Optional, Any
from core.entities.automato import AFD, TipoAutomato
from core.value_objects.estado import Estado
from core.value_objects.simbolo import Simbolo
from core.value_objects.transicao import Transicao
from core.value_objects.passo_didatico import PassoDidatico
from core.ports.interfaces import DidacticTracePort

class DfaMinimizer:
    """
    Serviço de domínio responsável pela minimização de um AFD
    removendo estados inacessíveis e fundindo estados equivalentes.
    """
    def minimizar(self, afd: AFD, trace: Optional[DidacticTracePort] = None) -> AFD:
        if trace:
            trace.clean()
            trace.log_step(PassoDidatico(
                indice=1,
                descricao=f"Iniciando minimização do AFD '{afd.nome}'.",
                dados_calculo={}
            ))

        # 1. Remover inacessíveis
        estados_alcancaveis = afd.obter_estados_alcancaveis()
        estados_inacessiveis = afd.estados - estados_alcancaveis
        
        if estados_inacessiveis:
            if trace:
                trace.log_step(PassoDidatico(
                    indice=2,
                    descricao=f"Removendo estados inacessíveis: {self._conjunto_str(estados_inacessiveis)}.",
                    dados_calculo={"inacessiveis": [str(e) for e in estados_inacessiveis]}
                ))
            novos_estados = estados_alcancaveis
            novos_finais = afd.estados_finais.intersection(estados_alcancaveis)
            novas_transicoes = frozenset(
                t for t in afd.transicoes 
                if t.origem in estados_alcancaveis and t.destino in estados_alcancaveis
            )
            afd_limpo = AFD(
                nome=afd.nome,
                tipo=TipoAutomato.DFA,
                alfabeto=afd.alfabeto,
                estados=frozenset(novos_estados),
                estado_inicial=afd.estado_inicial,
                estados_finais=frozenset(novos_finais),
                transicoes=novas_transicoes
            )
        else:
            if trace:
                trace.log_step(PassoDidatico(
                    indice=2,
                    descricao="Nenhum estado inacessível encontrado.",
                    dados_calculo={}
                ))
            afd_limpo = afd

        # 2. Particionamento inicial (Finais vs Não-Finais)
        grupo_finais = afd_limpo.estados_finais
        grupo_nao_finais = afd_limpo.estados - afd_limpo.estados_finais

        particoes = []
        if grupo_finais:
            particoes.append(grupo_finais)
        if grupo_nao_finais:
            particoes.append(grupo_nao_finais)

        passo_idx = 3
        if trace:
            trace.log_step(PassoDidatico(
                indice=passo_idx,
                descricao=f"Criada partição inicial P0: {self._particao_str(particoes)}.",
                dados_calculo={"particao": [[str(e) for e in p] for p in particoes]}
            ))
            passo_idx += 1

        # 3. Refinamento de partições
        refinando = True
        iteracao = 1
        while refinando:
            proximas_particoes = []
            cisao_ocorreu = False

            for classe in particoes:
                if len(classe) <= 1:
                    proximas_particoes.append(classe)
                    continue

                subclasses = self._dividir_classe(classe, particoes, afd_limpo)
                proximas_particoes.extend(subclasses)
                if len(subclasses) > 1:
                    cisao_ocorreu = True

            if len(proximas_particoes) == len(particoes):
                refinando = False
                if trace:
                    trace.log_step(PassoDidatico(
                        indice=passo_idx,
                        descricao=f"Nenhum refinamento adicional na iteração {iteracao}. Partição estabilizou.",
                        dados_calculo={}
                    ))
                    passo_idx += 1
            else:
                particoes = proximas_particoes
                if trace:
                    trace.log_step(PassoDidatico(
                        indice=passo_idx,
                        descricao=f"Partição refinada na iteração {iteracao}: {self._particao_str(particoes)}.",
                        dados_calculo={"particao": [[str(e) for e in p] for p in particoes]}
                    ))
                    passo_idx += 1
                passo_idx += 1
                iteracao += 1

        # 4. Construção do AFD Minimizando
        estado_map = {}  # Estado original -> Estado minimizado
        estados_min = set()
        for bloco in particoes:
            rotulo = self._format_block_label(bloco)
            est_min = Estado(rotulo)
            estados_min.add(est_min)
            for est_orig in bloco:
                estado_map[est_orig] = est_min

        novo_inicial = estado_map[afd_limpo.estado_inicial]
        novos_finais = set(estado_map[q] for q in afd_limpo.estados_finais)

        transicoes_min = set()
        for bloco in particoes:
            rep = next(iter(bloco))
            for s in afd_limpo.alfabeto.simbolos:
                dest_orig = afd_limpo.obter_transicao_determinista(rep, s)
                if dest_orig is not None:
                    orig_min = estado_map[rep]
                    dest_min = estado_map[dest_orig]
                    transicoes_min.add(Transicao(origem=orig_min, simbolo=s, destino=dest_min))

        if trace:
            trace.log_step(PassoDidatico(
                indice=passo_idx,
                descricao=f"AFD minimizado construído com {len(estados_min)} estados.",
                dados_calculo={
                    "estados_minimais": [str(e) for e in estados_min],
                    "estado_inicial": str(novo_inicial),
                    "estados_finais": [str(e) for e in novos_finais],
                    "transicoes": [str(t) for t in transicoes_min]
                }
            ))

        return AFD(
            nome=f"{afd.nome}_minimizado",
            tipo=TipoAutomato.DFA,
            alfabeto=afd.alfabeto,
            estados=frozenset(estados_min),
            estado_inicial=novo_inicial,
            estados_finais=frozenset(novos_finais),
            transicoes=frozenset(transicoes_min)
        )

    def _dividir_classe(self, classe: frozenset[Estado], particoes: list[frozenset[Estado]], afd: AFD) -> list[frozenset[Estado]]:
        grupos = {}
        for est in classe:
            assinatura = []
            for s in sorted(list(afd.alfabeto.simbolos), key=lambda x: x.valor):
                dest = afd.obter_transicao_determinista(est, s)
                bloco_idx = -1
                if dest is not None:
                    for idx, bloco in enumerate(particoes):
                        if dest in bloco:
                            bloco_idx = idx
                            break
                assinatura.append(bloco_idx)
            
            assinatura_tuple = tuple(assinatura)
            if assinatura_tuple not in grupos:
                grupos[assinatura_tuple] = []
            grupos[assinatura_tuple].append(est)

        return [frozenset(g) for g in grupos.values()]

    def _natural_sort_key(self, obj: Any) -> list:
        import re
        s = str(obj)
        return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]

    def _conjunto_str(self, fs: frozenset) -> str:
        return f"{{{', '.join(str(x) for x in sorted(fs, key=self._natural_sort_key))}}}"

    def _particao_str(self, particoes: list) -> str:
        return f"{{{', '.join(self._conjunto_str(p) for p in particoes)}}}"

    def _format_block_label(self, fs: frozenset) -> str:
        sorted_labels = [str(x) for x in sorted(fs, key=self._natural_sort_key)]
        if len(sorted_labels) == 1:
            return sorted_labels[0]
        return f"{{{','.join(sorted_labels)}}}"
