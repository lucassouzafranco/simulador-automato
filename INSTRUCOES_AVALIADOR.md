# Simulador de Autômatos e Gramáticas
**Guia Rápido de Avaliação**

Bem-vindo(a)! Este projeto foi arquitetado para não lhe dar nenhuma dor de cabeça com instalações de infraestrutura (Node.js, NPM, bibliotecas do React, etc).

Escolha a opção que melhor se adapta à sua máquina:

## Opção 1: O Caminho Mais Rápido (Windows)
Nós empacotamos o sistema inteiro (Motor Python + Interface Web React) em um único arquivo nativo que funciona sem dependências.
1. Abra a pasta `dist/`
2. Dê um duplo-clique em **`simulador.exe`**.
3. Uma janela preta vai subir (o motor em background) e o seu navegador vai abrir o sistema automaticamente. *(Obs: O Windows pode exibir um alerta azul do SmartScreen pois não é um .exe com licença corporativa. Basta clicar em "Mais informações" > "Executar mesmo assim")*.

## Opção 2: Código-Fonte Direto (Windows)
Se você preferir rodar o código-fonte Python diretamente pelo seu próprio interpretador local:
1. Dê um duplo-clique em **`INICIAR_WINDOWS.bat`** na raiz do projeto.
2. Ele vai criar um ambiente virtual izolado (`venv`), instalar as dependências do FastAPI e abrir a interface no seu navegador.

## Opção 3: Código-Fonte Direto (Linux ou Mac)
1. Abra o terminal na pasta raiz deste projeto.
2. Execute o comando: `./INICIAR_LINUX_MAC.sh`
3. Ele criará o `venv`, instalará o FastAPI via `pip` e abrirá a porta no seu navegador padrão.

---

### Executando os Testes Automatizados (Opcional)
Se desejar verificar a nossa suíte de testes (15 cenários cobrindo todo o motor), basta ter o Python instalado e rodar no terminal, na pasta raiz:
```bash
python -m unittest tests/test_comprehensive.py
```
