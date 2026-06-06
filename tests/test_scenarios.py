import unittest
from infrastructure import (
    InMemoryAutomatonRepository,
    InMemoryDidacticTraceAdapter,
)
from application import (
    CriarAFNInputDTO,
    ConverterAFNParaAFDInputDTO,
    SimularPalavraInputDTO,
    CriarAFNUseCase,
    ConverterAFNParaAFDUseCase,
    SimularPalavraUseCase,
)

class TestUserScenarios(unittest.TestCase):
    def setUp(self):
        self.auto_repo = InMemoryAutomatonRepository()
        self.trace_adapter = InMemoryDidacticTraceAdapter()
        
        self.uc_criar = CriarAFNUseCase(self.auto_repo)
        self.uc_determinar = ConverterAFNParaAFDUseCase(self.auto_repo, self.trace_adapter)
        self.uc_simular = SimularPalavraUseCase(self.auto_repo, self.trace_adapter)

    def _imprimir_resultado(self, cenario_num, afd, passos):
        print(f"\n=========================================")
        print(f"RESPOSTA DO CENÁRIO {cenario_num}")
        print(f"=========================================")
        print(f"AFD Estados: {sorted([str(e) for e in afd.estados])}")
        print(f"AFD Estado Inicial: {afd.estado_inicial}")
        print(f"AFD Estados Finais: {sorted([str(e) for e in afd.estados_finais])}")
        print(f"AFD Transições:")
        for t in sorted(afd.transicoes, key=lambda x: (str(x.origem), str(x.simbolo), str(x.destino))):
            print(f"  {t.origem} -({t.simbolo})-> {t.destino}")
        print(f"Passos didáticos de conversão:")
        for p in passos:
            print(f"  {p.indice}. {p.descricao}")
        print(f"=========================================\n")

    def test_cenario_1_epsilon_chain(self):
        # Cenário 1: Epsilon transitions q0 -> q1 -> q2 -> q3, q3 -a-> q0
        dto_criar = CriarAFNInputDTO(
            nome="Cenario_1",
            alfabeto=["a", "b"],
            estados=["q0", "q1", "q2", "q3"],
            estado_inicial="q0",
            estados_finais=["q3"],
            transicoes=[
                {"origem": "q0", "simbolo": "ε", "destino": "q1"},
                {"origem": "q1", "simbolo": "ε", "destino": "q2"},
                {"origem": "q2", "simbolo": "ε", "destino": "q3"},
                {"origem": "q3", "simbolo": "a", "destino": "q0"}
            ]
        )
        res_criar = self.uc_criar.execute(dto_criar)
        self.assertTrue(res_criar.sucesso)
        id_afn = res_criar.id_automato

        # Converter para AFD
        res_det = self.uc_determinar.execute(ConverterAFNParaAFDInputDTO(id_automato=id_afn))
        self.assertIsNotNone(res_det.id_afd)
        id_afd = res_det.id_afd

        # Obter o AFD gerado para verificar a estrutura
        afd = self.auto_repo.get_by_id(id_afd)
        
        # O estado inicial do AFD deve conter o fecho-epsilon de q0, que é {q0, q1, q2, q3}
        self.assertEqual(str(afd.estado_inicial), "{q0,q1,q2,q3}")
        
        # Exibir resposta no console
        self._imprimir_resultado(1, afd, res_det.passos_didaticos)

        # Testar aceitação e rejeição
        palavras_aceitas = ["", "a", "aa", "aaa", "aaaa"]
        palavras_rejeitadas = ["b", "ab", "ba", "aab", "aba"]
        
        for pal in palavras_aceitas:
            res_sim = self.uc_simular.execute(SimularPalavraInputDTO(id_automato=id_afd, palavra=pal))
            self.assertTrue(res_sim.aceita, f"Deveria aceitar: '{pal}'")
            
        for pal in palavras_rejeitadas:
            res_sim = self.uc_simular.execute(SimularPalavraInputDTO(id_automato=id_afd, palavra=pal))
            self.assertFalse(res_sim.aceita, f"Deveria rejeitar: '{pal}'")

    def test_cenario_2_multi_choice(self):
        # Cenário 2: AFN tradicional sem epsilon
        dto_criar = CriarAFNInputDTO(
            nome="Cenario_2",
            alfabeto=["a", "b"],
            estados=["q0", "q1", "q2", "q3"],
            estado_inicial="q0",
            estados_finais=["q3"],
            transicoes=[
                {"origem": "q0", "simbolo": "a", "destino": "q0"},
                {"origem": "q0", "simbolo": "b", "destino": "q0"},
                {"origem": "q0", "simbolo": "a", "destino": "q1"},
                {"origem": "q1", "simbolo": "a", "destino": "q2"},
                {"origem": "q1", "simbolo": "b", "destino": "q2"},
                {"origem": "q2", "simbolo": "a", "destino": "q3"},
                {"origem": "q2", "simbolo": "b", "destino": "q3"}
            ]
        )
        res_criar = self.uc_criar.execute(dto_criar)
        self.assertTrue(res_criar.sucesso)
        id_afn = res_criar.id_automato

        # Converter para AFD
        res_det = self.uc_determinar.execute(ConverterAFNParaAFDInputDTO(id_automato=id_afn))
        self.assertIsNotNone(res_det.id_afd)
        id_afd = res_det.id_afd

        # A linguagem aceita palavras que terminam com 'a' seguido de duas letras quaisquer (a ou b)
        afd = self.auto_repo.get_by_id(id_afd)
        
        # Exibir resposta no console
        self._imprimir_resultado(2, afd, res_det.passos_didaticos)

        palavras_aceitas = ["aaa", "aba", "aaba", "baba", "abb", "aabb", "babb"]
        palavras_rejeitadas = ["", "a", "b", "aa", "ab", "ba", "bb", "baa", "bbb", "abbb"]

        for pal in palavras_aceitas:
            res_sim_afd = self.uc_simular.execute(SimularPalavraInputDTO(id_automato=id_afd, palavra=pal))
            self.assertTrue(res_sim_afd.aceita, f"Deveria aceitar no AFD: '{pal}'")
            res_sim_afn = self.uc_simular.execute(SimularPalavraInputDTO(id_automato=id_afn, palavra=pal))
            self.assertTrue(res_sim_afn.aceita, f"Deveria aceitar no AFN: '{pal}'")
            
        for pal in palavras_rejeitadas:
            res_sim_afd = self.uc_simular.execute(SimularPalavraInputDTO(id_automato=id_afd, palavra=pal))
            self.assertFalse(res_sim_afd.aceita, f"Deveria rejeitar no AFD: '{pal}'")
            res_sim_afn = self.uc_simular.execute(SimularPalavraInputDTO(id_automato=id_afn, palavra=pal))
            self.assertFalse(res_sim_afn.aceita, f"Deveria rejeitar no AFN: '{pal}'")

    def test_cenario_3_minimal_binary(self):
        # Cenário 3: Transição única q0 -0-> q1
        dto_criar = CriarAFNInputDTO(
            nome="Cenario_3",
            alfabeto=["0", "1"],
            estados=["q0", "q1"],
            estado_inicial="q0",
            estados_finais=["q1"],
            transicoes=[
                {"origem": "q0", "simbolo": "0", "destino": "q1"}
            ]
        )
        res_criar = self.uc_criar.execute(dto_criar)
        self.assertTrue(res_criar.sucesso)
        id_afn = res_criar.id_automato

        # Converter para AFD
        res_det = self.uc_determinar.execute(ConverterAFNParaAFDInputDTO(id_automato=id_afn))
        self.assertIsNotNone(res_det.id_afd)
        id_afd = res_det.id_afd

        afd = self.auto_repo.get_by_id(id_afd)
        
        # Exibir resposta no console
        self._imprimir_resultado(3, afd, res_det.passos_didaticos)

        # Testar
        res_sim = self.uc_simular.execute(SimularPalavraInputDTO(id_automato=id_afd, palavra="0"))
        self.assertTrue(res_sim.aceita)

        res_sim2 = self.uc_simular.execute(SimularPalavraInputDTO(id_automato=id_afd, palavra="1"))
        self.assertFalse(res_sim2.aceita)

        res_sim3 = self.uc_simular.execute(SimularPalavraInputDTO(id_automato=id_afd, palavra="00"))
        self.assertFalse(res_sim3.aceita)

    def test_cenario_4_disconnected(self):
        # Cenário 4: q0 -x-> q1 -y-> q0, q2 -x-> q3 -y-> q2 (q2/q3 inacessíveis)
        dto_criar = CriarAFNInputDTO(
            nome="Cenario_4",
            alfabeto=["x", "y"],
            estados=["q0", "q1", "q2", "q3"],
            estado_inicial="q0",
            estados_finais=["q1", "q3"],
            transicoes=[
                {"origem": "q0", "simbolo": "x", "destino": "q1"},
                {"origem": "q1", "simbolo": "y", "destino": "q0"},
                {"origem": "q2", "simbolo": "x", "destino": "q3"},
                {"origem": "q3", "simbolo": "y", "destino": "q2"}
            ]
        )
        res_criar = self.uc_criar.execute(dto_criar)
        self.assertTrue(res_criar.sucesso)
        id_afn = res_criar.id_automato

        # Converter para AFD
        res_det = self.uc_determinar.execute(ConverterAFNParaAFDInputDTO(id_automato=id_afn))
        self.assertIsNotNone(res_det.id_afd)
        id_afd = res_det.id_afd

        # Obter AFD e verificar que q2 e q3 foram descartados (estados inacessíveis)
        afd = self.auto_repo.get_by_id(id_afd)
        
        # Exibir resposta no console
        self._imprimir_resultado(4, afd, res_det.passos_didaticos)

        # Apenas os subconjuntos contendo combinações de q0 e q1 devem estar nos estados
        for estado in afd.estados:
            # Estado do AFD não deve conter q2 nem q3
            self.assertNotIn("q2", str(estado))
            self.assertNotIn("q3", str(estado))

        # Testar simulações
        self.assertTrue(self.uc_simular.execute(SimularPalavraInputDTO(id_automato=id_afd, palavra="x")).aceita)
        self.assertTrue(self.uc_simular.execute(SimularPalavraInputDTO(id_automato=id_afd, palavra="xyx")).aceita)
        self.assertFalse(self.uc_simular.execute(SimularPalavraInputDTO(id_automato=id_afd, palavra="y")).aceita)

if __name__ == "__main__":
    unittest.main()
