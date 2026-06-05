# Instruções de Execução

Este guia descreve os pré-requisitos e comandos necessários para rodar e testar o Simulador de Autômatos e Gramáticas.

---

## 1. Pré-requisitos

* **Python 3.12+** instalado e disponível na variável de ambiente do sistema (`python` ou `python3`).
* O projeto utiliza apenas bibliotecas nativas da biblioteca padrão do Python (`unittest`, `dataclasses`, `typing`, `json`, `logging`, `uuid`, `threading`), dispensando a instalação de pacotes externos ou criação de ambientes virtuais (`venv`).

---

## 2. Executando a Aplicação (CLI)

Para inicializar o simulador interativo de console, execute o comando a partir do diretório raiz do projeto:

```bash
python main.py
```

---

## 3. Executando a Suíte de Testes Automatizados

O projeto contém três suítes de testes que cobrem as camadas do sistema. Elas utilizam a biblioteca padrão `unittest` do Python.

Para rodar todos os testes simultaneamente a partir do diretório raiz:

```bash
python -m unittest discover -s tests
```

### Rodando suítes individualmente:

1. **Testes do Core (Lógica Teórica e Algoritmos)**:
   ```bash
   python -m unittest tests/test_core.py
   ```
2. **Testes da Infraestrutura (Repositórios e Exportadores)**:
   ```bash
   python -m unittest tests/test_infrastructure.py
   ```
3. **Testes de Aplicação (Use Cases e Fluxos de Integração)**:
   ```bash
   python -m unittest tests/test_application.py
   ```
