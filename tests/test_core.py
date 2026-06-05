import unittest
from core import (
    Estado,
    Simbolo,
    Transicao,
    Alfabeto,
    Palavra,
    AFN,
    AFD,
    NfaToDfaConverter,
    DfaMinimizer,
    WordSimulator,
    AutomatonToGrammarConverter,
    GrammarToAutomatonConverter,
    DidacticTracePort,
    PassoDidatico,
    Variavel,
    Terminal,
    RegraProducao,
    GramaticaRegular,
)

class MemoriaDidacticTrace(DidacticTracePort):
    def __init__(self):
        self.steps = []

    def log_step(self, step: PassoDidatico) -> None:
        self.steps.append(step)

    def get_steps(self) -> list[PassoDidatico]:
        return self.steps

    def clean(self) -> None:
        self.steps = []


class TestCoreDomain(unittest.TestCase):
    def test_completo_fluxo_core(self):
        # 1. Criação de um AFN-ε (que aceita a palavra "a" ou "ab")
        # Estados: q0, q1, q2, q3 (finais: q1, q3)
        # q0 --a--> q1
        # q0 --ε--> q2
        # q2 --b--> q3
        q0 = Estado("q0")
        q1 = Estado("q1")
        q2 = Estado("q2")
        q3 = Estado("q3")

        a = Simbolo("a")
        b = Simbolo("b")
        eps = Simbolo.epsilon()

        alfabeto = Alfabeto(frozenset([a, b]))
        estados = frozenset([q0, q1, q2, q3])
        estados_finais = frozenset([q1, q3])

        transicoes = frozenset([
            Transicao(q0, a, q1),
            Transicao(q0, eps, q2),
            Transicao(q2, b, q3)
        ])

        afn = AFN(
            nome="AFN_Teste",
            alfabeto=alfabeto,
            estados=estados,
            estado_inicial=q0,
            estados_finais=estados_finais,
            transicoes=transicoes
        )

        # 2. Testar Simulação no AFN
        simulador = WordSimulator()
        trace = MemoriaDidacticTrace()

        self.assertTrue(simulador.simular(afn, Palavra.de_string("a"), trace))
        self.assertTrue(len(trace.get_steps()) > 0)

        trace.clean()
        self.assertTrue(simulador.simular(afn, Palavra.de_string("b"), trace)) # Por causa de q0 --ε--> q2 --b--> q3

        self.assertFalse(simulador.simular(afn, Palavra.de_string("ab")))
        
        # 3. Conversão AFN para AFD
        converter_nfa_dfa = NfaToDfaConverter()
        trace.clean()
        afd = converter_nfa_dfa.converter(afn, trace)
        
        # O AFD deve aceitar as mesmas palavras ("a", "b")
        self.assertTrue(simulador.simular(afd, Palavra.de_string("a")))
        self.assertTrue(simulador.simular(afd, Palavra.de_string("b")))
        self.assertFalse(simulador.simular(afd, Palavra.de_string("ab")))

        # 4. Minimização do AFD
        minimizer = DfaMinimizer()
        trace.clean()
        afd_min = minimizer.minimizar(afd, trace)
        
        # O AFD mínimo deve reter equivalência de linguagem
        self.assertTrue(simulador.simular(afd_min, Palavra.de_string("a")))
        self.assertTrue(simulador.simular(afd_min, Palavra.de_string("b")))

        # 5. Conversão do AFD para Gramática Regular
        converter_af_gram = AutomatonToGrammarConverter()
        trace.clean()
        gramatica = converter_af_gram.converter(afd_min, trace)
        
        # Validar consistência da Gramática
        self.assertEqual(len(gramatica.variaveis), len(afd_min.estados))
        self.assertEqual(len(gramatica.terminais), len(afd_min.alfabeto.simbolos))

        # 6. Conversão de Gramática Regular para AFN
        converter_gram_af = GrammarToAutomatonConverter()
        trace.clean()
        afn_da_gram = converter_gram_af.converter(gramatica, trace)
        
        # O autômato gerado a partir da gramática deve aceitar "a" e "b"
        self.assertTrue(simulador.simular(afn_da_gram, Palavra.de_string("a")))
        self.assertTrue(simulador.simular(afn_da_gram, Palavra.de_string("b")))


if __name__ == "__main__":
    unittest.main()
