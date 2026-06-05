import sys
from interface.cli import ConsoleApp

def main() -> None:
    """Função de entrada principal para executar o simulador via CLI."""
    try:
        app = ConsoleApp()
        app.rodar()
    except KeyboardInterrupt:
        print("\n\n  Execução encerrada pelo usuário (Ctrl+C). Até mais!\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
