import unittest
import json
import os
from core import (
    Estado,
    Simbolo,
    Transicao,
    Alfabeto,
    AFN,
    GramaticaRegular,
    Variavel,
    Terminal,
    RegraProducao,
    PassoDidatico,
)
from infrastructure import (
    InMemoryAutomatonRepository,
    InMemoryGrammarRepository,
    TxtExporter,
    JsonExporter,
    InMemoryDidacticTraceAdapter,
    logger,
)

class TestInfrastructure(unittest.TestCase):
    def test_in_memory_automaton_repository(self):
        repo = InMemoryAutomatonRepository()
        
        q0 = Estado("q0")
        alfabeto = Alfabeto(frozenset([Simbolo("a")]))
        af = AFN(
            nome="A1",
            alfabeto=alfabeto,
            estados=frozenset([q0]),
            estado_inicial=q0,
            estados_finais=frozenset([q0]),
            transicoes=frozenset()
        )
        
        repo.save(af)
        
        retrieved = repo.get_by_id(af.id)
        self.assertEqual(retrieved, af)
        
        all_items = repo.get_all()
        self.assertIn(af, all_items)

    def test_in_memory_grammar_repository(self):
        repo = InMemoryGrammarRepository()
        
        s = Variavel("S")
        a = Terminal("a")
        r = RegraProducao(esquerda=s, direita=(a,))
        gr = GramaticaRegular(
            variaveis=frozenset([s]),
            terminais=frozenset([a]),
            simbolo_inicial=s,
            producoes=frozenset([r])
        )
        
        repo.save(gr)
        
        retrieved = repo.get_by_id(gr.id)
        self.assertEqual(retrieved, gr)
        
        all_items = repo.get_all()
        self.assertIn(gr, all_items)

    def test_txt_exporter(self):
        exporter = TxtExporter()
        
        # Teste com Autômato
        q0 = Estado("q0")
        alf = Alfabeto(frozenset([Simbolo("x")]))
        af = AFN(
            nome="AF_TXT",
            alfabeto=alf,
            estados=frozenset([q0]),
            estado_inicial=q0,
            estados_finais=frozenset([q0]),
            transicoes=frozenset([Transicao(q0, Simbolo("x"), q0)])
        )
        
        txt_af = exporter.export(af)
        self.assertIn("Nome: AF_TXT", txt_af)
        self.assertIn("q0 -- x --> q0", txt_af)
        
        # Teste com Gramática
        s = Variavel("S")
        term = Terminal("x")
        r = RegraProducao(esquerda=s, direita=(term,))
        gr = GramaticaRegular(
            variaveis=frozenset([s]),
            terminais=frozenset([term]),
            simbolo_inicial=s,
            producoes=frozenset([r])
        )
        
        txt_gr = exporter.export(gr)
        self.assertIn("Símbolo Inicial: S", txt_gr)
        self.assertIn("S -> x", txt_gr)

    def test_json_exporter(self):
        exporter = JsonExporter()
        
        # Teste com Autômato
        q0 = Estado("q0")
        alf = Alfabeto(frozenset([Simbolo("x")]))
        af = AFN(
            nome="AF_JSON",
            alfabeto=alf,
            estados=frozenset([q0]),
            estado_inicial=q0,
            estados_finais=frozenset([q0]),
            transicoes=frozenset([Transicao(q0, Simbolo("x"), q0)])
        )
        
        json_af_str = exporter.export(af)
        json_af = json.loads(json_af_str)
        self.assertEqual(json_af["nome"], "AF_JSON")
        self.assertEqual(json_af["estado_inicial"], "q0")
        self.assertEqual(json_af["transicoes"][0]["simbolo"], "x")
        
        # Teste com Gramática
        s = Variavel("S")
        term = Terminal("x")
        r = RegraProducao(esquerda=s, direita=(term,))
        gr = GramaticaRegular(
            variaveis=frozenset([s]),
            terminais=frozenset([term]),
            simbolo_inicial=s,
            producoes=frozenset([r])
        )
        
        json_gr_str = exporter.export(gr)
        json_gr = json.loads(json_gr_str)
        self.assertEqual(json_gr["simbolo_inicial"], "S")
        self.assertEqual(json_gr["producoes"][0]["direita"], ["x"])

    def test_didactic_trace_adapter(self):
        trace = InMemoryDidacticTraceAdapter()
        trace.log_step(PassoDidatico(
            indice=1,
            descricao="Passo de Teste",
            dados_calculo={"valor": 123}
        ))
        
        self.assertEqual(len(trace.get_steps()), 1)
        self.assertEqual(trace.get_steps()[0].indice, 1)
        
        trace.clean()
        self.assertEqual(len(trace.get_steps()), 0)

    def test_logger(self):
        logger.info("Log técnico de teste da infraestrutura executado com sucesso.")
        self.assertTrue(os.path.exists("logs/app.log"))

if __name__ == "__main__":
    unittest.main()
