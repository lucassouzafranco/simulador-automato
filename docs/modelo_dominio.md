# Modelagem Completa do Domínio

Este documento descreve detalhadamente o modelo de domínio do simulador de autômatos e gramáticas regulares, baseado em conceitos de **Domain-Driven Design (DDD)** e orientação a objetos acadêmica avançada.

---

## 1. Enums do Domínio

```
Enum TipoAutomato {
    DFA     # Autômato Finito Determinístico
    NFA     # Autômato Finito Não-Determinístico
    E_NFA   # Autômato Finito Não-Determinístico com transições-ε (epsilon)
}

Enum TipoLinearidade {
    DIREITA   # Linear à Direita (ex: A -> aB ou A -> a)
    ESQUERDA  # Linear à Esquerda (ex: A -> Ba ou A -> a)
}

Enum TipoProducao {
    TERMINAL           # A -> a
    TERMINAL_VARIAVEL  # A -> aB
    VARIAVEL_TERMINAL  # A -> Ba
    VAZIA              # A -> ε
}
```

---

## 2. Entidades e Agregados

### Agregado de Autômatos (Automaton Aggregate)
* **Raiz do Agregado:** `Automato` (Entidade)
* **Entidades Internas:** `AFD` (Especialização/Entidade), `AFN` (Especialização/Entidade)
* **Objetos de Valor associados:** `Estado`, `Transicao`, `Alfabeto`, `Simbolo`

### Agregado de Gramáticas (Grammar Aggregate)
* **Raiz do Agregado:** `GramaticaRegular` (Entidade)
* **Objetos de Valor associados:** `Producao`, `Variavel`, `Terminal`

---

## 3. Detalhamento das Classes de Domínio

### 3.1. Classe `Automato` (Entidade - Aggregate Root)
* **Responsabilidade:** Representar um autômato finito genérico (5-tupla formal) e manter a consistência matemática de seus componentes.
* **Atributos:**
  * `id`: `UUID` (Identificador exclusivo)
  * `nome`: `str` (Nome descritivo acadêmico)
  * `tipo`: `TipoAutomato` (Enum)
  * `alfabeto`: `Alfabeto` (Value Object)
  * `estados`: `frozenset[Estado]` (Conjunto imutável de estados)
  * `estado_inicial`: `Estado` (Estado de partida)
  * `estados_finais`: `frozenset[Estado]` (Subconjunto de estados de aceitação)
  * `transicoes`: `frozenset[Transicao]` (Relação de transição)
* **Métodos:**
  * `validar() -> None` (Valida a estrutura formal do autômato e dispara exceções de domínio se inconsistente)
  * `obter_transicoes_partindo_de(origem: Estado, simbolo: Simbolo) -> frozenset[Estado]` (Retorna os estados alcançáveis)
  * `obter_estados_alcancaveis() -> frozenset[Estado]` (Executa busca em largura a partir do estado inicial)
* **Invariantes:**
  * O `estado_inicial` deve obrigatoriamente pertencer ao conjunto `estados`.
  * O conjunto `estados_finais` deve ser um subconjunto válido de `estados` ($F \subseteq Q$).
  * Todas as `transicoes` devem possuir estado de `origem` e `destino` pertencentes a `estados`.
  * Os símbolos presentes nas transições devem pertencer ao `alfabeto` ou ser o caractere especial de movimento vazio ($\epsilon$).
* **Regras de Negócio:**
  * A classe `Automato` é imutável após a sua construção. Qualquer mutação estrutural gera uma nova instância de `Automato` com um novo `id`.

---

### 3.2. Classe `AFD` (Entidade - Especialização de `Automato`)
* **Responsabilidade:** Representar um Autômato Finito Determinístico, impondo as restrições formais de determinismo rígido.
* **Atributos:** Herda todos os atributos de `Automato`.
* **Métodos:**
  * `obter_transicao_determinista(origem: Estado, simbolo: Simbolo) -> Estado` (Retorna o único estado destino ou lança erro se não definido)
* **Invariantes:**
  * Não pode conter nenhuma transição cujo símbolo seja o de movimento vazio ($\epsilon$).
  * Para qualquer par `(Estado, Simbolo)` onde o símbolo pertence ao alfabeto, não pode existir mais de uma transição ativa (não há caminhos paralelos).
* **Regras de Negócio:**
  * Caso não exista transição explícita definida para um determinado par estado-símbolo, subentende-se que o processamento cai em um estado de erro/rejeição (tratamento de determinismo parcial).

---

### 3.3. Classe `AFN` (Entidade - Especialização de `Automato`)
* **Responsabilidade:** Representar um Autômato Finito Não-Determinístico (podendo incluir transições vazias/fechos-ε).
* **Atributos:** Herda todos os atributos de `Automato`.
* **Métodos:**
  * `calcular_fecho_epsilon(estados: frozenset[Estado]) -> frozenset[Estado]` (Computa o fecho-ε recursivo do conjunto de estados)
* **Invariantes:**
  * Permite múltiplos estados destino para o mesmo par `(Estado, Simbolo)`.
  * Permite transições usando o símbolo vazio ($\epsilon$).
* **Regras de Negócio:**
  * Para a simulação, é necessário computar o fecho-ε do estado inicial antes de consumir o primeiro caractere da palavra.

---

### 3.4. Classe `Estado` (Value Object)
* **Responsabilidade:** Representar um estado formal de um autômato.
* **Atributos:**
  * `rotulo`: `str` (Rótulo/nome que identifica o estado, ex: "q0", "A", "{q0,q1}")
* **Métodos:**
  * `eh_composto() -> bool` (Verifica se o rótulo representa a fusão de um subconjunto de estados)
  * `obter_estados_de_origem() -> frozenset[str]` (Se composto, desmembra os nomes dos estados originais)
* **Invariantes:**
  * O `rotulo` não pode ser nulo ou string vazia.
  * O rótulo não pode conter delimitadores especiais reservados, a menos que devidamente escapados pelo parser.
* **Regras de Negócio:**
  * Dois objetos `Estado` são idênticos se seus rótulos forem textualmente idênticos.

---

### 3.5. Classe `Transicao` (Value Object)
* **Responsabilidade:** Representar um arco de transição direcional no autômato ($\delta$).
* **Atributos:**
  * `origem`: `Estado` (Estado de partida)
  * `simbolo`: `Simbolo` (Símbolo de entrada consumido ou ε)
  * `destino`: `Estado` (Estado de destino)
* **Métodos:**
  * `eh_epsilon() -> bool` (Informa se a transição é de movimento vazio)
* **Invariantes:**
  * A `origem` e o `destino` não podem ser nulos e devem ser estados válidos.
  * O `simbolo` não pode ser nulo.
* **Regras de Negócio:**
  * Uma transição é igual a outra se e somente se sua origem, seu destino e seu símbolo forem idênticos.

---

### 3.6. Classe `Alfabeto` (Value Object)
* **Responsabilidade:** Representar o conjunto formal de símbolos de entrada ($\Sigma$) do autômato.
* **Atributos:**
  * `simbolos`: `frozenset[Simbolo]` (Conjunto imutável de símbolos válidos)
* **Métodos:**
  * `contem(simbolo: Simbolo) -> bool` (Verifica a presença de um símbolo)
* **Invariantes:**
  * Não pode conter o símbolo vazio ($\epsilon$) como parte do alfabeto de entrada.
  * O conjunto não pode ser vazio.
* **Regras de Negócio:**
  * Ao criar o alfabeto, todos os caracteres de controle são rejeitados.

---

### 3.7. Classe `Simbolo` (Value Object)
* **Responsabilidade:** Representar a menor unidade de entrada (caractere formal).
* **Atributos:**
  * `valor`: `str` (String de tamanho 1 ou o caractere especial de fecho/epsilon)
* **Métodos:**
  * `eh_epsilon() -> bool` (Informa se representa ε)
* **Invariantes:**
  * O tamanho da string de `valor` deve ser exatamente 1, exceto para representações especiais de ε aceitas pelo parser (ex: "epsilon" ou "&").
* **Regras de Negócio:**
  * Símbolos com o mesmo caractere de representação são equivalentes.

---

### 3.8. Classe `Palavra` (Value Object)
* **Responsabilidade:** Representar uma cadeia ou sequência finita de símbolos a ser simulada.
* **Atributos:**
  * `sequencia`: `tuple[Simbolo, ...]` (Sequência imutável de símbolos de entrada)
* **Métodos:**
  * `obter_comprimento() -> int`
  * `como_texto() -> str` (Concatena os símbolos em uma string limpa)
* **Invariantes:**
  * Não pode conter símbolos de movimento vazio ($\epsilon$) em nenhuma posição de sua sequência (pois palavras contêm apenas símbolos do alfabeto).
* **Regras de Negócio:**
  * Uma palavra sem símbolos representa a palavra vazia formal (comprimento 0).

---

### 3.9. Classe `GramaticaRegular` (Entidade - Aggregate Root)
* **Responsabilidade:** Representar a estrutura matemática formal de uma gramática regular ($G = (V_N, V_T, P, S)$).
* **Atributos:**
  * `id`: `UUID`
  * `variaveis`: `frozenset[Variavel]` (Variáveis não-terminais, $V_N$)
  * `terminais`: `frozenset[Terminal]` (Símbolos terminais, $V_T$)
  * `simbolo_inicial`: `Variavel` (Variável de partida, $S$)
  * `producoes`: `frozenset[Producao]` (Regras de produção, $P$)
* **Métodos:**
  * `validar() -> None` (Garante a consistência matemática formal da gramática)
  * `obter_linearidade() -> TipoLinearidade` (Retorna se a gramática é linear à direita ou linear à esquerda)
* **Invariantes:**
  * O `simbolo_inicial` deve obrigatoriamente pertencer ao conjunto `variaveis`.
  * A interseção entre o conjunto de `variaveis` e `terminais` deve ser vazia ($V_N \cap V_T = \emptyset$).
  * Todas as `producoes` devem partir (lado esquerdo) de uma variável contida em `variaveis`.
  * Todas as produções devem seguir as regras de linearidade (todas lineares à direita ou todas lineares à esquerda). Misturas violam a regularidade.
* **Regras de Negócio:**
  * É imutável para assegurar a consistência dos algoritmos de conversão.

---

### 3.10. Classe `Producao` (Value Object)
* **Responsabilidade:** Representar uma regra de substituição formal na gramática regular.
* **Atributos:**
  * `esquerda`: `Variavel` (Lado esquerdo da produção, deve ser um não-terminal único)
  * `direita`: `tuple[Union[Variavel, Terminal], ...]` (Corpo da produção)
* **Métodos:**
  * `obter_tipo() -> TipoProducao` (Enum do formato estrutural)
  * `eh_vazia() -> bool` (Informa se produz a palavra vazia ε)
* **Invariantes:**
  * A tupla da `direita` deve conter no máximo dois elementos para respeitar os formatos regulares:
    * Um único terminal ($A \to a$)
    * Um terminal seguido de não-terminal ($A \to aB$, linear à direita)
    * Um não-terminal seguido de terminal ($A \to Ba$, linear à esquerda)
    * A palavra vazia ε ($A \to \epsilon$)
* **Regras de Negócio:**
  * Se houver a produção $S \to \epsilon$, a variável $S$ (símbolo inicial) não pode aparecer no lado direito de nenhuma produção da gramática (regrade invariância de gramáticas regulares formais).

---

### 3.11. Classe `Variavel` (Value Object)
* **Responsabilidade:** Representar um símbolo não-terminal da gramática.
* **Atributos:**
  * `rotulo`: `str` (Ex: "S", "A", "B")
* **Invariantes:**
  * O rótulo não pode ser vazio.
* **Regras de Negócio:**
  * Por convenção acadêmica didática, é representada em letras maiúsculas para facilitar a distinção visual em logs e relatórios.

---

### 3.12. Classe `Terminal` (Value Object)
* **Responsabilidade:** Representar um símbolo terminal da gramática.
* **Atributos:**
  * `caractere`: `str` (Ex: "a", "b", "0")
* **Invariantes:**
  * Deve conter exatamente um caractere.
  * Não pode ser o caractere especial reservado de palavra vazia (ε).
* **Regras de Negócio:**
  * Possui equivalência biunívoca com o objeto `Simbolo` na tradução de Gramática para Autômato.

---

## 4. Interfaces do Domínio (Ports de Domínio)

As interfaces do domínio definem os contratos de validação e simulação pura do sistema de forma abstrata.

### 4.1. Interface `ValidadorFormal`
* **Métodos:**
  * `validar_invariantes(modelo: Union[Automato, GramaticaRegular]) -> bool` (Verifica a consistência e lança erros específicos)

### 4.2. Interface `SimuladorDeCadeia`
* **Métodos:**
  * `simular(automato: Automato, palavra: Palavra) -> SimulationResultDTO` (Simula a palavra gerando passos didáticos)

### 4.3. Interface `ConversorDomínio`
* **Métodos:**
  * `converter(origem: Union[Automato, GramaticaRegular]) -> Union[Automato, GramaticaRegular]`

---

## UML Textual Completo (PlantUML)

O diagrama textual descreve a estrutura das classes de domínio e seus tipos (Entidades, Objetos de Valor e Enums).

```
@startuml
skinparam style strictuml

enum TipoAutomato {
  DFA
  NFA
  E_NFA
}

enum TipoLinearidade {
  DIREITA
  ESQUERDA
}

enum TipoProducao {
  TERMINAL
  TERMINAL_VARIAVEL
  VARIAVEL_TERMINAL
  VAZIA
}

class Automato <<Entity>> {
  - id: UUID
  - nome: String
  - tipo: TipoAutomato
  - estado_inicial: Estado
  + validar(): void
  + obter_transicoes_partindo_de(origem: Estado, simbolo: Simbolo): frozenset[Estado]
  + obter_estados_alcancaveis(): frozenset[Estado]
}

class AFD <<Entity>> {
  + obter_transicao_determinista(origem: Estado, simbolo: Simbolo): Estado
}

class AFN <<Entity>> {
  + calcular_fecho_epsilon(estados: frozenset[Estado]): frozenset[Estado]
}

class Estado <<Value Object>> {
  - rotulo: String
  + eh_composto(): Boolean
  + obter_estados_de_origem(): frozenset[String]
}

class Transicao <<Value Object>> {
  - origem: Estado
  - simbolo: Simbolo
  - destino: Estado
  + eh_epsilon(): Boolean
}

class Alfabeto <<Value Object>> {
  + contem(simbolo: Simbolo): Boolean
}

class Simbolo <<Value Object>> {
  - valor: String
  + eh_epsilon(): Boolean
}

class Palavra <<Value Object>> {
  - sequencia: tuple[Simbolo, ...]
  + obter_comprimento(): Integer
  + como_texto(): String
}

class GramaticaRegular <<Entity>> {
  - id: UUID
  - simbolo_inicial: Variavel
  + validar(): void
  + obter_linearidade(): TipoLinearidade
}

class Producao <<Value Object>> {
  - esquerda: Variavel
  - direita: tuple[Union[Variavel, Terminal], ...]
  + obter_tipo(): TipoProducao
  + eh_vazia(): Boolean
}

class Variavel <<Value Object>> {
  - rotulo: String
}

class Terminal <<Value Object>> {
  - caractere: String
}

' Heranças e especializações
Automato <|-- AFD
Automato <|-- AFN

' Relacionamentos no Agregado de Autômatos
Automato "1" *-- "1" Alfabeto : possui >
Automato "1" *-- "1..*" Estado : composto por >
Automato "1" *-- "0..*" Transicao : define >
Alfabeto "1" *-- "1..*" Simbolo : contem >
Transicao "1" o-- "2" Estado : conecta >
Transicao "1" o-- "1" Simbolo : lê >
Palavra "1" o-- "0..*" Simbolo : formada por >

' Relacionamentos no Agregado de Gramáticas
GramaticaRegular "1" *-- "1..*" Variavel : possui >
GramaticaRegular "1" *-- "1..*" Terminal : possui >
GramaticaRegular "1" *-- "1..*" Producao : define >
Producao "1" o-- "1" Variavel : esq >
Producao "1" o-- "1..2" Variavel : dir_var >
Producao "1" o-- "1..2" Terminal : dir_term >

@enduml
```

---

## Relacionamentos e Cardinalidades

### Agregado do Autômato
1. **`Automato` para `Alfabeto`**
   * **Tipo:** Composição (o Alfabeto não existe fora do contexto de validação do Autômato).
   * **Cardinalidade:** `1 -> 1` (todo autômato possui exatamente um alfabeto).
2. **`Automato` para `Estado`**
   * **Tipo:** Composição (os Estados pertencem ao ciclo de vida do autômato).
   * **Cardinalidade:** `1 -> 1..*` (um autômato possui de 1 a n estados).
3. **`Automato` para `Transicao`**
   * **Tipo:** Composição (as regras de transição dependem do ciclo de vida do autômato).
   * **Cardinalidade:** `1 -> 0..*` (um autômato possui zero ou mais transições).
4. **`Alfabeto` para `Simbolo`**
   * **Tipo:** Composição.
   * **Cardinalidade:** `1 -> 1..*` (um alfabeto possui pelo menos 1 símbolo válido).
5. **`Transicao` para `Estado`**
   * **Tipo:** Agregação/Associação (a transição apenas faz referência a estados que já existem no autômato).
   * **Cardinalidade:** `1 -> 2` (uma transição conecta exatamente 1 estado de origem a 1 estado de destino).
6. **`Transicao` para `Simbolo`**
   * **Tipo:** Agregação/Associação.
   * **Cardinalidade:** `1 -> 1` (uma transição consome exatamente 1 símbolo ou ε).

### Agregado da Gramática
1. **`GramaticaRegular` para `Variavel`**
   * **Tipo:** Composição.
   * **Cardinalidade:** `1 -> 1..*` (uma gramática regular possui pelo menos 1 variável não-terminal).
2. **`GramaticaRegular` para `Terminal`**
   * **Tipo:** Composição.
   * **Cardinalidade:** `1 -> 1..*` (uma gramática regular possui pelo menos 1 símbolo terminal).
3. **`GramaticaRegular` para `Producao`**
   * **Tipo:** Composição.
   * **Cardinalidade:** `1 -> 1..*` (uma gramática possui pelo menos 1 regra de produção).
4. **`Producao` para `Variavel` (Lado Esquerdo)**
   * **Tipo:** Agregação.
   * **Cardinalidade:** `1 -> 1` (uma regra de produção tem exatamente uma variável não-terminal no lado esquerdo).
5. **`Producao` para `Variavel` / `Terminal` (Lado Direito)**
   * **Tipo:** Agregação.
   * **Cardinalidade:** `1 -> 0..2` (o lado direito de uma produção regular contém de 0 a 2 elementos terminais ou variáveis).
