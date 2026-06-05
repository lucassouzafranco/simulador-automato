import unittest
from infrastructure import (
    InMemoryAutomatonRepository,
    InMemoryGrammarRepository,
    InMemoryDidacticTraceAdapter,
    TxtExporter,
    JsonExporter,
)
from application import (
    CriarAFNInputDTO,
    ConverterAFNParaAFDInputDTO,
    SimularPalavraInputDTO,
    MinimizarAFDInputDTO,
    ConverterAFParaGRInputDTO,
    ConverterGRParaAFInputDTO,
    ExportarResultadoInputDTO,
    CriarAFNUseCase,
    ConverterAFNParaAFDUseCase,
    SimularPalavraUseCase,
    MinimizarAFDUseCase,
    ConverterAFParaGRUseCase,
    ConverterGRParaAFUseCase,
    ExportarResultadoUseCase,
)

class TestApplicationFlow(unittest.TestCase):
    def test_completo_fluxo_aplicacao(self):
        auto_repo = InMemoryAutomatonRepository()
        gram_repo = InMemoryGrammarRepository()
        trace = InMemoryDidacticTraceAdapter()
        
        exporters = {
            "TXT": TxtExporter(),
            "JSON": JsonExporter()
        }

        # Use cases instanciados
        uc_criar = CriarAFNUseCase(auto_repo)
        uc_determinar = ConverterAFNParaAFDUseCase(auto_repo, trace)
        uc_simular = SimularPalavraUseCase(auto_repo, trace)
        uc_minimizar = MinimizarAFDUseCase(auto_repo, trace)
        uc_af_gr = ConverterAFParaGRUseCase(auto_repo, gram_repo, trace)
        uc_gr_af = ConverterGRParaAFUseCase(auto_repo, gram_repo, trace)
        uc_exportar = ExportarResultadoUseCase(auto_repo, gram_repo, exporters)

        # 1. Criar AFN para a linguagem a*
        dto_criar = CriarAFNInputDTO(
            nome="AFN_A_Star",
            alfabeto=["a"],
            estados=["q0", "q1"],
            estado_inicial="q0",
            estados_finais=["q0"],
            transicoes=[
                {"origem": "q0", "simbolo": "a", "destino": "q1"},
                {"origem": "q1", "simbolo": "ε", "destino": "q0"}
            ]
        )
        
        res_criar = uc_criar.execute(dto_criar)
        self.assertTrue(res_criar.sucesso)
        self.assertIsNotNone(res_criar.id_automato)
        id_afn = res_criar.id_automato

        # 2. Simular palavra no AFN
        res_sim_afn = uc_simular.execute(SimularPalavraInputDTO(id_automato=id_afn, palavra="aaa"))
        self.assertTrue(res_sim_afn.aceita)
        self.assertTrue(len(res_sim_afn.passos_didaticos) > 0)

        # 3. Converter AFN para AFD
        res_det = uc_determinar.execute(ConverterAFNParaAFDInputDTO(id_automato=id_afn))
        self.assertIsNotNone(res_det.id_afd)
        id_afd = res_det.id_afd
        self.assertTrue(len(res_det.passos_didaticos) > 0)

        # 4. Simular palavra no AFD
        res_sim_afd = uc_simular.execute(SimularPalavraInputDTO(id_automato=id_afd, palavra="aaa"))
        self.assertTrue(res_sim_afd.aceita)

        # 5. Minimizar o AFD
        res_min = uc_minimizar.execute(MinimizarAFDInputDTO(id_automato=id_afd))
        self.assertIsNotNone(res_min.id_afd_minimizado)
        id_afd_min = res_min.id_afd_minimizado
        self.assertTrue(len(res_min.passos_didaticos) > 0)

        # 6. Converter AFD minimizado para Gramática Regular
        res_gr = uc_af_gr.execute(ConverterAFParaGRInputDTO(id_automato=id_afd_min))
        self.assertIsNotNone(res_gr.id_gramatica)
        id_gram = res_gr.id_gramatica
        self.assertTrue(len(res_gr.passos_didaticos) > 0)

        # 7. Converter Gramática Regular de volta para AFN
        res_afn_final = uc_gr_af.execute(ConverterGRParaAFInputDTO(id_gramatica=id_gram))
        self.assertIsNotNone(res_afn_final.id_automato)
        id_afn_final = res_afn_final.id_automato
        self.assertTrue(len(res_afn_final.passos_didaticos) > 0)

        # Simular palavra no AFN final obtido
        res_sim_final = uc_simular.execute(SimularPalavraInputDTO(id_automato=id_afn_final, palavra="aaa"))
        self.assertTrue(res_sim_final.aceita)

        # 8. Exportar resultados (TXT e JSON)
        res_exp_txt = uc_exportar.execute(ExportarResultadoInputDTO(id_entidade=id_afd_min, tipo_entidade="AUTOMATO", formato="TXT"))
        self.assertIn("Nome: AFD_equivalente_AFN_A_Star_minimizado", res_exp_txt.conteudo)

        res_exp_json = uc_exportar.execute(ExportarResultadoInputDTO(id_entidade=id_gram, tipo_entidade="GRAMATICA", formato="JSON"))
        self.assertIn('"simbolo_inicial"', res_exp_json.conteudo)

if __name__ == "__main__":
    unittest.main()
