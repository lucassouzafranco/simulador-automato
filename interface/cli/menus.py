import os
from typing import List, Dict, Any

def limpar_tela() -> None:
    """Limpa a tela do terminal dependendo do sistema operacional."""
    os.system("cls" if os.name == "nt" else "clear")

def exibir_cabecalho(titulo: str) -> None:
    """Exibe um cabeçalho decorado com o título."""
    largura = 80
    print("=" * largura)
    print(titulo.center(largura))
    print("=" * largura)

def exibir_menu(titulo: str, opcoes: List[str]) -> str:
    """Exibe um menu de opções e retorna a opção escolhida pelo usuário."""
    exibir_cabecalho(titulo)
    for idx, opcao in enumerate(opcoes, start=1):
        print(f" [{idx}] {opcao}")
    print(" [0] Voltar/Sair")
    print("-" * 80)
    escolha = input(" Escolha uma opção: ").strip()
    return escolha

def print_tabela(headers: List[str], rows: List[List[Any]]) -> None:
    """Desenha uma tabela ASCII formatada de forma profissional no console."""
    if not headers:
        return
        
    widths = [len(h) for h in headers]
    for r in rows:
        for idx, val in enumerate(r):
            widths[idx] = max(widths[idx], len(str(val)))
            
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    
    print("  " + sep)
    print("  | " + " | ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers)) + " |")
    print("  " + sep)
    for r in rows:
        print("  | " + " | ".join(str(val).ljust(widths[i]) for i, val in enumerate(r)) + " |")
    print("  " + sep)

def exibir_passos_didaticos(passos: List[Any]) -> None:
    """Imprime de forma legível e didática o histórico de passos de um algoritmo."""
    print("\n" + "#" * 80)
    print("                     DETALHAMENTO PASSO A PASSO (DIDÁTICO)                     ".center(80))
    print("#" * 80)
    
    for p in passos:
        print(f"\n>>> PASSO {p.indice}: {p.descricao}")
        print("-" * 80)
        for chave, valor in p.dados_calculo.items():
            if isinstance(valor, dict):
                print(f"  * {chave.replace('_', ' ').capitalize()}:")
                for k, v in valor.items():
                    print(f"    - {k}: {v}")
            elif isinstance(valor, (list, set, frozenset)):
                elementos = [str(x) for x in valor]
                print(f"  * {chave.replace('_', ' ').capitalize()}: {{{', '.join(sorted(elementos))}}}")
            else:
                print(f"  * {chave.replace('_', ' ').capitalize()}: {valor}")
        print("-" * 80)
    print("#" * 80 + "\n")
