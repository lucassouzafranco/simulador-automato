import os
from typing import Dict, List, Optional
from uuid import UUID

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
from infrastructure import (
    InMemoryAutomatonRepository,
    InMemoryGrammarRepository,
    InMemoryDidacticTraceAdapter,
    TxtExporter,
    JsonExporter,
)
from interface.cli.menus import (
    limpar_tela,
    exibir_cabecalho,
    exibir_menu,
    print_tabela,
    exibir_passos_didaticos,
)

class ConsoleApp:
    """Classe controladora principal do aplicativo de console didático."""

    def __init__(self) -> None:
        self.auto_repo = InMemoryAutomatonRepository()
        self.gram_repo = InMemoryGrammarRepository()
        self.trace_adapter = InMemoryDidacticTraceAdapter()
        
        self.exporters = {
            "TXT": TxtExporter(),
            "JSON": JsonExporter()
        }

        # Inicialização dos casos de uso
        self.uc_criar = CriarAFNUseCase(self.auto_repo)
        self.uc_determinar = ConverterAFNParaAFDUseCase(self.auto_repo, self.trace_adapter)
        self.uc_simular = SimularPalavraUseCase(self.auto_repo, self.trace_adapter)
        self.uc_minimizar = MinimizarAFDUseCase(self.auto_repo, self.trace_adapter)
        self.uc_af_gr = ConverterAFParaGRUseCase(self.auto_repo, self.gram_repo, self.trace_adapter)
        self.uc_gr_af = ConverterGRParaAFUseCase(self.auto_repo, self.gram_repo, self.trace_adapter)
        self.uc_exportar = ExportarResultadoUseCase(self.auto_repo, self.gram_repo, self.exporters)

        self._criar_dados_demonstracao()

    def _criar_dados_demonstracao(self) -> None:
        """Adiciona dados iniciais de demonstração (a*) para facilitar o teste imediato."""
        dto = CriarAFNInputDTO(
            nome="AFN_Exemplo_A_Star",
            alfabeto=["a"],
            estados=["q0", "q1"],
            estado_inicial="q0",
            estados_finais=["q0"],
            transicoes=[
                {"origem": "q0", "simbolo": "a", "destino": "q1"},
                {"origem": "q1", "simbolo": "ε", "destino": "q0"}
            ]
        )
        self.uc_criar.execute(dto)

    def rodar(self) -> None:
        """Loop principal do terminal."""
        while True:
            limpar_tela()
            opcoes = [
                "Criar AFN Interativamente",
                "Listar Autômatos e Gramáticas",
                "Simular Palavra (AFD ou AFN-ε)",
                "Converter AFN para AFD (Determinização)",
                "Minimizar AFD",
                "Converter AF para Gramática Regular",
                "Converter Gramática Regular para AFN",
                "Exportar Resultado (TXT/JSON)"
            ]
            escolha = exibir_menu("SIMULADOR DE AUTÔMATOS E GRAMÁTICAS - MENU PRINCIPAL", opcoes)
            
            if escolha == "1":
                self._criar_afn_interativo()
            elif escolha == "2":
                self._listar_entidades()
            elif escolha == "3":
                self._simular_palavra_interativo()
            elif escolha == "4":
                self._converter_afn_afd_interativo()
            elif escolha == "5":
                self._minimizar_afd_interativo()
            elif escolha == "6":
                self._converter_af_gr_interativo()
            elif escolha == "7":
                self._converter_gr_af_interativo()
            elif escolha == "8":
                self._exportar_entidade_interativo()
            elif escolha == "0":
                limpar_tela()
                print("\n  Obrigado por utilizar o simulador de autômatos didático!\n")
                break
            else:
                input("\n Opção inválida. Pressione [Enter] para tentar novamente...")

    def _selecionar_automato(self, apenas_tipo: Optional[str] = None) -> Optional[UUID]:
        """Exibe uma lista de autômatos para seleção e retorna o ID do selecionado."""
        automatos = self.auto_repo.get_all()
        if apenas_tipo:
            automatos = [a for a in automatos if a.tipo.value == apenas_tipo]
            
        if not automatos:
            print("\n Nenhum autômato disponível para seleção.")
            return None

        headers = ["#", "Nome", "Tipo", "Estados", "Alfabeto", "ID"]
        rows = []
        for idx, a in enumerate(automatos, start=1):
            rows.append([
                idx,
                a.nome,
                a.tipo.value,
                len(a.estados),
                ", ".join(str(s) for s in a.alfabeto.simbolos),
                str(a.id)[:8] + "..."
            ])
            
        print("\n Autômatos Disponíveis:")
        print_tabela(headers, rows)
        
        try:
            opc = int(input("\n Selecione o número correspondente ao autômato: ").strip())
            if 1 <= opc <= len(automatos):
                return automatos[opc - 1].id
        except ValueError:
            pass
        print(" Seleção inválida.")
        return None

    def _selecionar_gramatica(self) -> Optional[UUID]:
        """Exibe uma lista de gramáticas e retorna o ID da selecionada."""
        gramaticas = self.gram_repo.get_all()
        if not gramaticas:
            print("\n Nenhuma gramática disponível.")
            return None

        headers = ["#", "Linearidade", "Símbolo Inicial", "ID"]
        rows = []
        for idx, g in enumerate(gramaticas, start=1):
            rows.append([
                idx,
                g.obter_linearidade().value,
                g.simbolo_inicial,
                str(g.id)[:8] + "..."
            ])
            
        print("\n Gramáticas Disponíveis:")
        print_tabela(headers, rows)
        
        try:
            opc = int(input("\n Selecione o número correspondente à gramática: ").strip())
            if 1 <= opc <= len(gramaticas):
                return gramaticas[opc - 1].id
        except ValueError:
            pass
        print(" Seleção inválida.")
        return None

    def _criar_afn_interativo(self) -> None:
        limpar_tela()
        exibir_cabecalho("CRIAR AFN INTERATIVAMENTE")
        
        nome = input(" Nome do autômato (Ex: M1): ").strip()
        alfabeto_str = input(" Símbolos do alfabeto separados por vírgula (Ex: a,b): ").strip()
        alfabeto = [s.strip() for s in alfabeto_str.split(",") if s.strip()]
        
        estados_str = input(" Estados separados por vírgula (Ex: q0,q1,q2): ").strip()
        estados = [e.strip() for e in estados_str.split(",") if e.strip()]
        
        estado_inicial = input(f" Estado Inicial (Disponíveis: {estados}): ").strip()
        
        finais_str = input(f" Estados Finais separados por vírgula (Subconjunto de {estados}): ").strip()
        estados_finais = [f.strip() for f in finais_str.split(",") if f.strip()]
        
        print("\n Definição de Transições:")
        print(" Digite as transições no formato: origem simbolo destino")
        print(" Use 'ε', 'epsilon', '&' ou deixe vazio para transições vazias.")
        print(" Pressione [Enter] em uma linha vazia para encerrar.")
        
        transicoes = []
        while True:
            linha = input(f" Transição {len(transicoes) + 1}: ").strip()
            if not linha:
                break
            partes = linha.split()
            if len(partes) < 2:
                print("   Erro: Use o formato 'origem simbolo destino' ou 'origem destino' para transição vazia.")
                continue
            
            if len(partes) == 2:
                origem, destino = partes
                simbolo = "ε"
            else:
                origem, simbolo, destino = partes[0], partes[1], partes[2]
                
            transicoes.append({
                "origem": origem,
                "simbolo": simbolo,
                "destino": destino
            })
            
        dto = CriarAFNInputDTO(
            nome=nome,
            alfabeto=alfabeto,
            estados=estados,
            estado_inicial=estado_inicial,
            estados_finais=estados_finais,
            transicoes=transicoes
        )
        
        res = self.uc_criar.execute(dto)
        if res.sucesso:
            print(f"\n [SUCESSO] AFN '{res.nome}' criado com ID: {res.id_automato}")
        else:
            print(f"\n [FALHA] Não foi possível criar o AFN: {res.mensagem_erro}")
            
        input("\nPressione [Enter] para continuar...")

    def _listar_entidades(self) -> None:
        limpar_tela()
        exibir_cabecalho("LISTAR ENTIDADES EM MEMÓRIA")
        
        # Listar Automatos
        automatos = self.auto_repo.get_all()
        if automatos:
            print("\n Autômatos Registrados:")
            headers = ["Nome", "Tipo", "Alfabeto", "Estados", "Finais"]
            rows = []
            for a in automatos:
                rows.append([
                    a.nome,
                    a.tipo.value,
                    ", ".join(str(s) for s in a.alfabeto.simbolos),
                    ", ".join(str(e) for e in a.estados),
                    ", ".join(str(f) for f in a.estados_finais)
                ])
            print_tabela(headers, rows)
        else:
            print("\n Nenhum autômato cadastrado.")
            
        # Listar Gramaticas
        gramaticas = self.gram_repo.get_all()
        if gramaticas:
            print("\n Gramáticas Regulares Registradas:")
            headers = ["ID", "Linearidade", "Símbolo Inicial", "Regras"]
            rows = []
            for g in gramaticas:
                rows.append([
                    str(g.id)[:8] + "...",
                    g.obter_linearidade().value,
                    g.simbolo_inicial,
                    ", ".join(str(p) for p in g.producoes)
                ])
            print_tabela(headers, rows)
        else:
            print("\n Nenhuma gramática cadastrada.")
            
        input("\nPressione [Enter] para continuar...")

    def _simular_palavra_interativo(self) -> None:
        limpar_tela()
        exibir_cabecalho("SIMULAÇÃO DE PALAVRA")
        
        id_auto = self._selecionar_automato()
        if not id_auto:
            input("\nPressione [Enter] para retornar...")
            return
            
        palavra = input("\n Digite a palavra a ser simulada (Ex: aab ou deixe vazio para ε): ").strip()
        
        self.trace_adapter.clean()
        dto = SimularPalavraInputDTO(id_automato=id_auto, palavra=palavra)
        res = self.uc_simular.execute(dto)
        
        exibir_passos_didaticos(res.passos_didaticos)
        
        if res.aceita:
            print(" VERDICT: PALAVRA ACEITA PELO AUTÔMATO! ".center(80, "*"))
        else:
            print(" VERDICT: PALAVRA REJEITADA PELO AUTÔMATO! ".center(80, "*"))
            
        input("\nPressione [Enter] para continuar...")

    def _converter_afn_afd_interativo(self) -> None:
        limpar_tela()
        exibir_cabecalho("CONVERSÃO AFN PARA AFD (DETERMINIZAÇÃO)")
        
        id_auto = self._selecionar_automato(apenas_tipo="AFN")
        if not id_auto:
            input("\nPressione [Enter] para retornar...")
            return
            
        self.trace_adapter.clean()
        dto = ConverterAFNParaAFDInputDTO(id_automato=id_auto)
        
        try:
            res = self.uc_determinar.execute(dto)
            exibir_passos_didaticos(res.passos_didaticos)
            
            print(f" [SUCESSO] AFD determinístico criado com sucesso!")
            print(f"   Nome do AFD: {res.automato_dto.nome}")
            print(f"   Estados do AFD: {res.automato_dto.estados}")
            print(f"   Estados Finais: {res.automato_dto.estados_finais}")
        except Exception as e:
            print(f"\n [ERRO] Falha durante a determinização: {e}")
            
        input("\nPressione [Enter] para continuar...")

    def _minimizar_afd_interativo(self) -> None:
        limpar_tela()
        exibir_cabecalho("MINIMIZAÇÃO DE AFD")
        
        id_auto = self._selecionar_automato(apenas_tipo="AFD")
        if not id_auto:
            input("\nPressione [Enter] para retornar...")
            return
            
        self.trace_adapter.clean()
        dto = MinimizarAFDInputDTO(id_automato=id_auto)
        
        try:
            res = self.uc_minimizar.execute(dto)
            exibir_passos_didaticos(res.passos_didaticos)
            
            print(f" [SUCESSO] AFD minimizado criado com sucesso!")
            print(f"   Nome do AFD Min: {res.automato_dto.nome}")
            print(f"   Estados Finais: {res.automato_dto.estados_finais}")
            print(f"   Quantidade de estados reduzida para: {len(res.automato_dto.estados)}")
        except Exception as e:
            print(f"\n [ERRO] Falha durante a minimização: {e}")
            
        input("\nPressione [Enter] para continuar...")

    def _converter_af_gr_interativo(self) -> None:
        limpar_tela()
        exibir_cabecalho("CONVERSÃO DE AUTÔMATO PARA GRAMÁTICA REGULAR")
        
        id_auto = self._selecionar_automato()
        if not id_auto:
            input("\nPressione [Enter] para retornar...")
            return
            
        self.trace_adapter.clean()
        dto = ConverterAFParaGRInputDTO(id_automato=id_auto)
        
        try:
            res = self.uc_af_gr.execute(dto)
            exibir_passos_didaticos(res.passos_didaticos)
            
            print(f" [SUCESSO] Gramática Regular gerada com sucesso!")
            print(f"   Linearidade: {res.gramatica_dto.linearidade}")
            print(f"   Símbolo Inicial: {res.gramatica_dto.simbolo_inicial}")
            print(f"   Regras de Produção:")
            for p in res.gramatica_dto.producoes:
                dir_str = "".join(p.direita)
                print(f"     {p.esquerda} -> {dir_str}")
        except Exception as e:
            print(f"\n [ERRO] Falha na conversão: {e}")
            
        input("\nPressione [Enter] para continuar...")

    def _converter_gr_af_interativo(self) -> None:
        limpar_tela()
        exibir_cabecalho("CONVERSÃO DE GRAMÁTICA REGULAR PARA AUTÔMATO")
        
        id_gram = self._selecionar_gramatica()
        if not id_gram:
            input("\nPressione [Enter] para retornar...")
            return
            
        self.trace_adapter.clean()
        dto = ConverterGRParaAFInputDTO(id_gramatica=id_gram)
        
        try:
            res = self.uc_gr_af.execute(dto)
            exibir_passos_didaticos(res.passos_didaticos)
            
            print(f" [SUCESSO] Autômato Finito (AFN) equivalente criado!")
            print(f"   Nome: {res.automato_dto.nome}")
            print(f"   Estados: {res.automato_dto.estados}")
            print(f"   Estado Inicial: {res.automato_dto.estado_inicial}")
            print(f"   Estados Finais: {res.automato_dto.estados_finais}")
        except Exception as e:
            print(f"\n [ERRO] Falha na conversão: {e}")
            
        input("\nPressione [Enter] para continuar...")

    def _exportar_entidade_interativo(self) -> None:
        limpar_tela()
        exibir_cabecalho("EXPORTAR RESULTADOS")
        
        print(" O que você deseja exportar?")
        print("  [1] Um Autômato")
        print("  [2] Uma Gramática Regular")
        escolha = input(" Opção: ").strip()
        
        tipo_entidade = ""
        id_entidade = None
        if escolha == "1":
            tipo_entidade = "AUTOMATO"
            id_entidade = self._selecionar_automato()
        elif escolha == "2":
            tipo_entidade = "GRAMATICA"
            id_entidade = self._selecionar_gramatica()
        else:
            print(" Opção inválida.")
            input("\nPressione [Enter] para retornar...")
            return
            
        if not id_entidade:
            input("\nPressione [Enter] para retornar...")
            return
            
        print("\n Escolha o formato de exportação:")
        print("  [1] Texto legível (.txt)")
        print("  [2] JSON estruturado (.json)")
        form_opc = input(" Opção: ").strip()
        
        formato = ""
        if form_opc == "1":
            formato = "TXT"
        elif form_opc == "2":
            formato = "JSON"
        else:
            print(" Formato inválido.")
            input("\nPressione [Enter] para retornar...")
            return
            
        dto = ExportarResultadoInputDTO(
            id_entidade=id_entidade,
            tipo_entidade=tipo_entidade,
            formato=formato
        )
        
        try:
            res = self.uc_exportar.execute(dto)
            print("\n" + "-" * 50)
            print(" CONTEÚDO EXPORTADO:")
            print("-" * 50)
            print(res.conteudo)
            print("-" * 50)
            
            salvar = input("\n Deseja salvar este conteúdo em um arquivo físico? (s/n): ").strip().lower()
            if salvar == "s":
                nome_padrao = "exportacao." + formato.lower()
                nome_arquivo = input(f" Nome do arquivo (Padrão: {nome_padrao}): ").strip()
                if not nome_arquivo:
                    nome_arquivo = nome_padrao
                
                os.makedirs("exports", exist_ok=True)
                caminho = os.path.join("exports", nome_arquivo)
                with open(caminho, "w", encoding="utf-8") as f:
                    f.write(res.conteudo)
                print(f" [SUCESSO] Arquivo salvo em: {caminho}")
        except Exception as e:
            print(f"\n [ERRO] Falha na exportação: {e}")
            
        input("\nPressione [Enter] para continuar...")
