# Simulador de Autômatos e Gramáticas

Este projeto foi arquitetado para rodar de forma simples e direta, sem exigir configurações complexas de infraestrutura. Escolha a opção que melhor se adapta ao seu ambiente:

## Opção 1: O Caminho Mais Rápido (Windows)
Nós empacotamos o sistema inteiro (Motor Python + Interface Web React) em um único executável nativo que funciona 100% offline e sem dependências.
1. Abra a pasta `dist/`
2. Dê um duplo-clique em **`simulador.exe`**.
3. Uma janela preta vai subir (o motor em background) e o seu navegador vai abrir o sistema automaticamente. *(Obs: O Windows pode exibir um alerta azul do SmartScreen informando que o desenvolvedor é desconhecido. Basta clicar em "Mais informações" > "Executar mesmo assim")*.

## Opção 2: Código-Fonte Integrado Automático (Windows)
Se você preferir rodar o código-fonte Python diretamente pelo seu próprio interpretador local:
1. Dê um duplo-clique em **`INICIAR_WINDOWS.bat`** na raiz do projeto.
2. Ele vai criar um ambiente virtual isolado (`venv`), instalar as dependências da API (FastAPI/Uvicorn) e abrir a interface no seu navegador.

## Opção 3: Código-Fonte Integrado Automático (Linux ou Mac)
1. Abra o terminal na pasta raiz deste projeto.
2. Execute o comando: `./INICIAR_LINUX_MAC.sh`
3. Ele criará o `venv`, instalará o FastAPI via `pip` e abrirá a porta no seu navegador padrão.

## Opção 4: Instalação Manual Completa (Via Terminal)
Caso prefira rodar o projeto do modo de desenvolvimento tradicional pelo terminal, instalando as dependências do Frontend (Node) e Backend (Python) passo a passo:

**Pré-requisitos:** Node.js, NPM e Python 3.10+ instalados.

### No Windows (PowerShell / CMD):
Abra **dois** terminais na pasta raiz do projeto.

**Terminal 1 (Frontend React/Vite):**
```powershell
cd web
npm install
npm run dev
```

**Terminal 2 (Backend FastAPI):**
```powershell
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn pydantic
python interface\run_dev.py
```

### No Linux / Mac (Bash / Zsh):
Abra **dois** terminais na pasta raiz do projeto.

**Terminal 1 (Frontend React/Vite):**
```bash
cd web
npm install
npm run dev
```

**Terminal 2 (Backend FastAPI):**
```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn pydantic
python3 interface/run_dev.py
```

*(No modo de instalação manual, o frontend ficará acessível na porta 5173 e o backend servirá a API de forma independente).*

---

### Executando os Testes Automatizados
A suíte de testes (15 cenários de ponta a ponta cobrindo as regras do motor teórico) pode ser executada com o comando:
```bash
python -m unittest tests/test_comprehensive.py
```
