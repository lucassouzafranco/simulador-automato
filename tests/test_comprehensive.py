import unittest
from core import (
    Estado, Simbolo, Transicao, Alfabeto, Palavra, AFN, AFD,
    NfaToDfaConverter, DfaMinimizer, WordSimulator,
    AutomatonToGrammarConverter, GrammarToAutomatonConverter,
    DidacticTracePort, PassoDidatico, Variavel, Terminal, RegraProducao, GramaticaRegular
)

class HistoricoFalso(DidacticTracePort):
    def log_step(self, step: PassoDidatico) -> None: pass
    def get_steps(self) -> list[PassoDidatico]: return []
    def clean(self) -> None: pass

class TestComprehensiveSuite(unittest.TestCase):
    def setUp(self):
        self.historico = HistoricoFalso()
        self.simulador = WordSimulator()
        self.conversor_afn_afd = NfaToDfaConverter()
        self.minimizador = DfaMinimizer()
        self.a = Simbolo("a")
        self.b = Simbolo("b")
        self.c = Simbolo("c")
        self.eps = Simbolo.epsilon()
        self.alfabeto = Alfabeto(frozenset([self.a, self.b, self.c]))
        self.alfabeto_ab = Alfabeto(frozenset([self.a, self.b]))

    # --- A. Determinização (AFN -> AFD) ---
    def test_d1_estado_inacessivel(self):
        q0, q1, q2, q3 = Estado("q0"), Estado("q1"), Estado("q2"), Estado("q3")
        transicoes = frozenset([
            Transicao(q0, self.a, q1),
            Transicao(q1, self.b, q2),
            Transicao(q3, self.a, q3),
            Transicao(q3, self.b, q3)
        ])
        afn = AFN(nome="AFN", alfabeto=self.alfabeto_ab, estados=frozenset([q0,q1,q2,q3]), estado_inicial=q0, estados_finais=frozenset([q2]), transicoes=transicoes)
        afd = self.conversor_afn_afd.converter(afn, self.historico)
        estados_nomes = [e.rotulo for e in afd.estados]
        self.assertFalse(any("q3" in e for e in estados_nomes))

    def test_d2_estado_morto(self):
        q0, q1, qd = Estado("q0"), Estado("q1"), Estado("qd")
        transicoes = frozenset([
            Transicao(q0, self.a, q1), Transicao(q0, self.b, qd),
            Transicao(q1, self.a, q1), Transicao(q1, self.b, qd),
            Transicao(qd, self.a, qd), Transicao(qd, self.b, qd)
        ])
        afn = AFN(nome="AFN", alfabeto=self.alfabeto_ab, estados=frozenset([q0,q1,qd]), estado_inicial=q0, estados_finais=frozenset([q1]), transicoes=transicoes)
        afd = self.conversor_afn_afd.converter(afn, self.historico)
        self.assertTrue(self.simulador.simular(afd, Palavra.de_string("a"), self.historico))
        self.assertFalse(self.simulador.simular(afd, Palavra.de_string("b"), self.historico))

    def test_d3_afn_multiplos_destinos(self):
        q0, q1, q2 = Estado("q0"), Estado("q1"), Estado("q2")
        transicoes = frozenset([
            Transicao(q0, self.a, q0), Transicao(q0, self.a, q1),
            Transicao(q1, self.b, q2)
        ])
        afn = AFN(nome="AFN", alfabeto=self.alfabeto_ab, estados=frozenset([q0,q1,q2]), estado_inicial=q0, estados_finais=frozenset([q2]), transicoes=transicoes)
        afd = self.conversor_afn_afd.converter(afn, self.historico)
        estados_nomes = [e.rotulo for e in afd.estados]
        self.assertTrue(any("q0,q1" in e or "q1,q0" in e for e in estados_nomes))

    def test_d5_afn_eps_ramificacoes(self):
        q0, q1, q2, q3 = Estado("q0"), Estado("q1"), Estado("q2"), Estado("q3")
        transicoes = frozenset([
            Transicao(q0, self.eps, q1), Transicao(q0, self.eps, q2),
            Transicao(q1, self.a, q1), Transicao(q1, self.b, q3),
            Transicao(q2, self.b, q2), Transicao(q2, self.a, q3)
        ])
        afn = AFN(nome="AFN", alfabeto=self.alfabeto_ab, estados=frozenset([q0,q1,q2,q3]), estado_inicial=q0, estados_finais=frozenset([q3]), transicoes=transicoes)
        afd = self.conversor_afn_afd.converter(afn, self.historico)
        init_name = afd.estado_inicial.rotulo
        self.assertTrue("q0" in init_name and "q1" in init_name and "q2" in init_name)

    def test_d6_ciclo_eps(self):
        q0, q1, q2 = Estado("q0"), Estado("q1"), Estado("q2")
        transicoes = frozenset([
            Transicao(q0, self.eps, q1), Transicao(q1, self.eps, q2), Transicao(q2, self.eps, q0)
        ])
        afn = AFN(nome="AFN", alfabeto=self.alfabeto_ab, estados=frozenset([q0,q1,q2]), estado_inicial=q0, estados_finais=frozenset([q2]), transicoes=transicoes)
        afd = self.conversor_afn_afd.converter(afn, self.historico)
        self.assertTrue("q0" in afd.estado_inicial.rotulo)
        self.assertTrue("q1" in afd.estado_inicial.rotulo)
        self.assertTrue("q2" in afd.estado_inicial.rotulo)

    def test_d7_final_alcancado_eps(self):
        q0, q1 = Estado("q0"), Estado("q1")
        transicoes = frozenset([Transicao(q0, self.eps, q1)])
        afn = AFN(nome="AFN", alfabeto=self.alfabeto_ab, estados=frozenset([q0,q1]), estado_inicial=q0, estados_finais=frozenset([q1]), transicoes=transicoes)
        afd = self.conversor_afn_afd.converter(afn, self.historico)
        self.assertIn(afd.estado_inicial, afd.estados_finais)

    def test_d8_fecho_eps_vazio(self):
        q0 = Estado("q0")
        afn = AFN(nome="AFN", alfabeto=self.alfabeto_ab, estados=frozenset([q0]), estado_inicial=q0, estados_finais=frozenset([]), transicoes=frozenset([]))
        afd = self.conversor_afn_afd.converter(afn, self.historico)
        self.assertEqual(len(afd.estados), 1)

    # --- B. Minimização ---
    def test_m1_estados_equivalentes(self):
        A, B, C, D, E, F = Estado("A"), Estado("B"), Estado("C"), Estado("D"), Estado("E"), Estado("F")
        zero, um = Simbolo("0"), Simbolo("1")
        alfabeto = Alfabeto(frozenset([zero, um]))
        transicoes = frozenset([
            Transicao(A, zero, B), Transicao(A, um, E),
            Transicao(B, zero, C), Transicao(B, um, F),
            Transicao(E, zero, D), Transicao(E, um, F),
            Transicao(C, zero, C), Transicao(C, um, C),
            Transicao(D, zero, D), Transicao(D, um, D),
            Transicao(F, zero, F), Transicao(F, um, F),
        ])
        afd = AFD(nome="AFD", alfabeto=alfabeto, estados=frozenset([A,B,C,D,E,F]), estado_inicial=A, estados_finais=frozenset([C,D,F]), transicoes=transicoes)
        min_afd = self.minimizer.minimizar(afd, self.historico)
        self.assertTrue(len(min_afd.estados) < 6)

    def test_m8_refinamento_cardinalidade(self):
        pass

    # --- C. Simulação de AFD ---
    def test_s1_palavra_aceita(self):
        q0, q1 = Estado("q0"), Estado("q1")
        transicoes = frozenset([Transicao(q0, self.a, q1), Transicao(q1, self.b, q1)])
        afd = AFD(nome="AFD", alfabeto=self.alfabeto_ab, estados=frozenset([q0,q1]), estado_inicial=q0, estados_finais=frozenset([q1]), transicoes=transicoes)
        self.assertTrue(self.simulador.simular(afd, Palavra.de_string("ab"), self.historico))
        self.assertTrue(self.simulador.simular(afd, Palavra.de_string("abbb"), self.historico))

    def test_s2_palavra_rejeitada(self):
        q0, q1 = Estado("q0"), Estado("q1")
        transicoes = frozenset([Transicao(q0, self.a, q1), Transicao(q1, self.b, q1)])
        afd = AFD(nome="AFD", alfabeto=self.alfabeto_ab, estados=frozenset([q0,q1]), estado_inicial=q0, estados_finais=frozenset([q1]), transicoes=transicoes)
        self.assertFalse(self.simulador.simular(afd, Palavra.de_string(""), self.historico))
        self.assertFalse(self.simulador.simular(afd, Palavra.de_string("b"), self.historico))
        self.assertFalse(self.simulador.simular(afd, Palavra.de_string("ba"), self.historico))

    def test_s8_nenhum_estado_ativo(self):
        q0, q1 = Estado("q0"), Estado("q1")
        transicoes = frozenset([Transicao(q0, self.a, q1)])
        afn = AFN(nome="AFN", alfabeto=self.alfabeto_ab, estados=frozenset([q0,q1]), estado_inicial=q0, estados_finais=frozenset([q1]), transicoes=transicoes)
        self.assertFalse(self.simulador.simular(afn, Palavra.de_string("ab"), self.historico))

    # --- F. Conversão Autômato -> Gramática ---
    def test_g2_estado_inicial_final(self):
        q0 = Estado("q0")
        transicoes = frozenset([Transicao(q0, self.a, q0)])
        afd = AFD(nome="AFD", alfabeto=self.alfabeto_ab, estados=frozenset([q0]), estado_inicial=q0, estados_finais=frozenset([q0]), transicoes=transicoes)
        conversor = AutomatonToGrammarConverter()
        gr = conversor.conversor(afd, self.historico)
        self.assertTrue(any(p.esquerda.rotulo.startswith("S_") for p in gr.producoes))

    # --- G. Conversão Gramática -> AFN ---
    def test_ga4_linear_esquerda_direta(self):
        S, A, B = Variavel("S"), Variavel("A"), Variavel("B")
        a, b, c = Terminal("a"), Terminal("b"), Terminal("c")
        producoes = frozenset([
            RegraProducao(esquerda=S, direita=tuple([a, A])),
            RegraProducao(esquerda=A, direita=tuple([b, B])),
            RegraProducao(esquerda=B, direita=tuple([c]))
        ])
        gr = GramaticaRegular(terminais=frozenset([a,b,c]), variaveis=frozenset([S,A,B]), producoes=producoes, simbolo_inicial=S)
        conversor = GrammarToAutomatonConverter()
        afn = conversor.conversor(gr, self.historico)
        self.assertTrue(self.simulador.simular(afn, Palavra.de_string("abc"), self.historico))
        self.assertFalse(self.simulador.simular(afn, Palavra.de_string("ab"), self.historico))

    # --- H. Testes de Consistência ---
    def test_c4_asterisco(self):
        q0 = Estado("q0")
        transicoes = frozenset([Transicao(q0, self.a, q0)])
        afd = AFD(nome="AFD", alfabeto=self.alfabeto_ab, estados=frozenset([q0]), estado_inicial=q0, estados_finais=frozenset([q0]), transicoes=transicoes)
        
        conv_gr = AutomatonToGrammarConverter().converter(afd, self.historico)
        afn_from_gr = GrammarToAutomatonConverter().converter(conv_gr, self.historico)
        afd_from_afn = self.conversor_afn_afd.converter(afn_from_gr, self.historico)
        min_afd = self.minimizador.minimizar(afd_from_afn, self.historico)
        
        self.assertTrue(self.simulador.simular(min_afd, Palavra.de_string(""), self.historico))
        self.assertTrue(self.simulador.simular(min_afd, Palavra.de_string("a"), self.historico))
        self.assertTrue(self.simulador.simular(min_afd, Palavra.de_string("aaa"), self.historico))
        self.assertFalse(self.simulador.simular(min_afd, Palavra.de_string("b"), self.historico))

if __name__ == '__main__':
    unittest.main()
