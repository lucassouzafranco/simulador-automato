# Manual do Usuário: Simulador de Autômatos e Gramáticas

Este manual descreve como interagir com o Simulador de Autômatos e Gramáticas Didático através da interface de linha de comando (CLI). O software foi desenvolvido sob princípios acadêmicos de Teoria da Computação, fornecendo detalhamentos didáticos em todas as conversões.

---

## 1. Visão Geral

O simulador é projetado para operar sobre três modelos formais fundamentais:
* **Autômato Finito Não-Determinístico com $\varepsilon$-transições (AFN-$e$)**
* **Autômato Finito Determinístico (AFD)**
* **Gramática Regular (GR)** (linear à esquerda ou à direita)

---

## 2. Inicialização e Menu Principal

Ao iniciar o programa (`python main.py`), você será apresentado ao **Menu Principal**:
```
================================================================================
               SIMULADOR DE AUTÔMATOS E GRAMÁTICAS - MENU PRINCIPAL
================================================================================
 [1] Criar AFN Interativamente
 [2] Listar Autômatos e Gramáticas
 [3] Simular Palavra (AFD ou AFN-ε)
 [4] Converter AFN para AFD (Determinização)
 [5] Minimizar AFD
 [6] Converter AF para Gramática Regular
 [7] Converter Gramática Regular para AFN
 [8] Exportar Resultado (TXT/JSON)
 [0] Voltar/Sair
================================================================================
```

---

## 3. Guia Passo a Passo de Operações

### 3.1. Criar um AFN Interativamente (Opção 1)
Permite construir um autômato definindo elemento por elemento:
1. **Nome**: Um identificador (Ex: `M1`).
2. **Alfabeto**: Símbolos permitidos separados por vírgula (Ex: `a,b`). O símbolo vazio ($\epsilon$) é reservado e não deve ser incluído aqui.
3. **Estados**: Rótulos de estados separados por vírgula (Ex: `q0,q1,q2`).
4. **Estado Inicial**: Defina o rótulo do estado de partida (Ex: `q0`).
5. **Estados Finais**: Subconjunto de aceitação separado por vírgula (Ex: `q0,q2`).
6. **Transições**: Informe no formato `origem simbolo destino`. Exemplo:
   * `q0 a q1`
   * Para transições vazias ($\epsilon$), escreva `q1 q0` ou `q1 ε q0` (utilizando o caractere de epsilon ou as palavras chave `epsilon` ou `&`).
   * Para terminar a inserção, apenas pressione **[Enter]** em uma linha vazia.

### 3.2. Listar Entidades Cadastradas (Opção 2)
Exibe todos os autômatos e gramáticas atualmente salvos na memória da sessão, dispostos em tabelas formatadas.

### 3.3. Simular uma Cadeia (Opção 3)
Selecione o autômato desejado e digite a cadeia de caracteres (palavra) para teste:
* Para testar a palavra vazia ($\epsilon$), pressione **[Enter]** diretamente sem digitar nada.
* O sistema imprimirá a execução detalhada, exibindo os conjuntos de estados ativos a cada passo e a decisão de aceitação.

### 3.4. Determinização: AFN $\to$ AFD (Opção 4)
* Converte um AFN selecionado para seu AFD equivalente usando o algoritmo de **Construção de Subconjuntos** com $\varepsilon$-fechamentos.
* A CLI exibirá passo a passo cada novo estado de subconjunto criado, seus respectivos fechamentos reflexivos/transitivos de $\epsilon$ e a tabela de transição resultante.

### 3.5. Minimização de AFD (Opção 5)
* Remove estados inacessíveis e funde estados equivalentes através do algoritmo de partição por classes de equivalência (baseado no algoritmo de Moore/Hopcroft).
* A CLI ilustra as iterações de refinamento dos blocos $P_0, P_1, \dots$ até a estabilização do conjunto de estados do AFD mínimo.

### 3.6. Conversões Bidirecionais (Opções 6 e 7)
* **AF $\to$ Gramática**: Converte o autômato para uma gramática linear correspondente, criando produções do tipo $A \to aB$ e $A \to a$.
* **Gramática $\to$ AFN**: Converte uma gramática de entrada linear à direita ou à esquerda em um AFN de transições correspondentes com estado final de aceitação.

### 3.7. Exportação (Opção 8)
* Permite visualizar e exportar o autômato ou gramática em formatos:
  * **TXT**: Relatório textual estruturado amigável.
  * **JSON**: Serialização completa para transmissão de dados.
* O usuário pode optar por gravar o resultado no disco, que será salvo na pasta `exports/` raiz do projeto.
