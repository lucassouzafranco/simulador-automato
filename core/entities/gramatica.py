from dataclasses import dataclass, field
import uuid
from enum import Enum
from core.value_objects.regra_producao import RegraProducao, Variavel, Terminal, TipoProducao
from core.exceptions.validacao import InvarianteVioladaException, GramaticaNaoRegularException

class TipoLinearidade(Enum):
    DIREITA = "DIREITA"
    ESQUERDA = "ESQUERDA"


@dataclass(kw_only=True)
class GramaticaRegular:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    variaveis: frozenset[Variavel]
    terminais: frozenset[Terminal]
    simbolo_inicial: Variavel
    producoes: frozenset[RegraProducao]

    def __post_init__(self) -> None:
        self.validar()

    def validar(self) -> None:
        # 1. Simbolo inicial deve pertencer a variaveis
        if self.simbolo_inicial not in self.variaveis:
            raise InvarianteVioladaException(
                f"O símbolo inicial {self.simbolo_inicial} deve pertencer ao conjunto de variáveis (não-terminais)."
            )

        # 2. Variaveis e terminais devem ser disjuntos em seus rótulos
        labels_var = {v.rotulo for v in self.variaveis}
        labels_term = {t.caractere for t in self.terminais}
        inter_labels = labels_var.intersection(labels_term)
        if inter_labels:
            raise InvarianteVioladaException(
                f"O conjunto de não-terminais e terminais deve ser disjunto. Interseção encontrada: {inter_labels}."
            )

        # 3. Validar se todas as produções usam símbolos existentes
        S_produz_epsilon = False
        for p in self.producoes:
            if p.esquerda not in self.variaveis:
                raise InvarianteVioladaException(
                    f"A produção {p} possui lado esquerdo {p.esquerda} que não é uma variável válida."
                )
            for item in p.direita:
                if isinstance(item, Variavel) and item not in self.variaveis:
                    raise InvarianteVioladaException(
                        f"A produção {p} referencia a variável {item} que não pertence à gramática."
                    )
                if isinstance(item, Terminal) and not item.caractere in ("epsilon", "ε", "&") and item not in self.terminais:
                    raise InvarianteVioladaException(
                        f"A produção {p} referencia o terminal {item} que não pertence à gramática."
                    )
            
            if p.esquerda == self.simbolo_inicial and p.eh_vazia():
                S_produz_epsilon = True

        # 4. Restrição do S produzindo epsilon
        if S_produz_epsilon:
            for p in self.producoes:
                if self.simbolo_inicial in p.direita:
                    raise GramaticaNaoRegularException(
                        f"Como o símbolo inicial {self.simbolo_inicial} produz a palavra vazia, "
                        f"ele não pode aparecer no lado direito da produção: {p}."
                    )

        # 5. Validar a consistência da linearidade
        self.obter_linearidade()

    def obter_linearidade(self) -> TipoLinearidade:
        tem_linear_direita = False
        tem_linear_esquerda = False

        for p in self.producoes:
            if p.eh_vazia() or len(p.direita) < 2:
                continue
            tipo = p.obter_tipo()
            if tipo == TipoProducao.TERMINAL_VARIAVEL:
                tem_linear_direita = True
            elif tipo == TipoProducao.VARIAVEL_TERMINAL:
                tem_linear_esquerda = True

        if tem_linear_direita and tem_linear_esquerda:
            raise GramaticaNaoRegularException(
                "A gramática mistura produções lineares à direita e à esquerda, o que viola a regularidade."
            )
        
        return TipoLinearidade.ESQUERDA if tem_linear_esquerda else TipoLinearidade.DIREITA
