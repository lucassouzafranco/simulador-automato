# Camada Application (Camada de Aplicação)

Esta especificação define os Casos de Uso (Use Cases), DTOs (Data Transfer Objects), validações e contratos de serviço que estruturam a camada `Application` do simulador acadêmico. Todos os fluxos seguem os princípios da Clean Architecture.

---

## 1. Casos de Uso (Use Cases)

### 1.1. Caso de Uso: `CriarAFN`
* **Objetivo:** Instanciar um Autômato Finito Não-Determinístico (AFN), validar suas regras formais de consistência matemática e persistir sua estrutura.
* **Entradas:** `CriarAFNInputDTO`
* **Saídas:** `CriarAFNOutputDTO`
* **DTOs:**
  * **`CriarAFNInputDTO`**
    * `nome`: `str`
    * `alfabeto`: `list[str]` (Lista de caracteres válidos)
    * `estados`: `list[str]` (Rótulos dos estados)
    * `estado_inicial`: `str`
    * `estados_finais`: `list[str]`
    * `transicoes`: `list[dict]` (Lista de dicionários contendo `origem`, `simbolo` e `destino`)
  * **`CriarAFNOutputDTO`**
    * `id_automato`: `UUID`
    * `nome`: `str`
    * `sucesso`: `bool`
* **Fluxo Principal:**
  1. O caso de uso recebe o `CriarAFNInputDTO`.
  2. Valida sintaticamente o DTO (formatos de strings e arrays).
  3. Mapeia as entradas básicas para objetos de valor (`Estado`, `Simbolo`, `Transicao`, `Alfabeto`).
  4. Instancia a entidade `AFN` injetando seus objetos de valor.
  5. O construtor da entidade `AFN` executa as validações matemáticas internas de consistência (Invariantes de Domínio).
  6. Chama o `AutomatonRepositoryPort.save(afn)` para persistir a entidade.
  7. Retorna `CriarAFNOutputDTO` com o ID gerado e status de sucesso.
* **Fluxos Alternativos:**
  * **A1: Invariante de Domínio Violada**
    1. Se o domínio levantar uma exceção formal (ex: estado de transição inexistente no conjunto de estados), o caso de uso captura o erro.
    2. Registra o erro no log técnico.
    3. Retorna o DTO com `sucesso = False` e mensagens detalhadas de falha teórica.
* **Validações:**
  * **Sintáticas:** Tipagem dos dados de entrada, chaves presentes na lista de transições.
  * **Semânticas:** Invariantes de autômato (ex: $F \subseteq Q$, transições usando apenas estados e símbolos que pertencem ao autômato).
* **Exceções:**
  * `DTOInvalidoException` (Sintática)
  * `EstadoInicialInexistenteException` (Domínio)
  * `EstadoFinalInvalidoException` (Domínio)
  * `TransicaoInvalidaException` (Domínio)

---

### 1.2. Caso de Uso: `ConverterAFNParaAFD`
* **Objetivo:** Converter um AFN cadastrado em um AFD equivalente utilizando o algoritmo clássico de Determinação (Subset Construction), gerando o passo-a-passo didático.
* **Entradas:** `ConverterAFNParaAFDInputDTO`
* **Saídas:** `ConverterAFNParaAFDOutputDTO`
* **DTOs:**
  * **`ConverterAFNParaAFDInputDTO`**
    * `id_automato`: `UUID`
  * **`ConverterAFNParaAFDOutputDTO`**
    * `id_afd`: `UUID` (ID do novo autômato gerado)
    * `passos_didaticos`: `list[PassoDidaticoDTO]`
    * `automato_dto`: `AutomatonOutputDTO` (Estrutura do AFD gerado)
  * **`PassoDidaticoDTO`**
    * `passo`: `int`
    * `acao`: `str` (Ex: "Calculando fecho-ε")
    * `detalhe`: `str` (Ex: "Fecho-ε({q0}) = {q0, q1}")
* **Fluxo Principal:**
  1. O caso de uso recebe o `ConverterAFNParaAFDInputDTO`.
  2. Busca o autômato de origem usando `AutomatonRepositoryPort.get_by_id(id_automato)`.
  3. Valida se o autômato existe e se o seu tipo é compatível com conversão (`NFA` ou `E_NFA`).
  4. Executa o serviço de domínio `NfaToDfaConverter`, registrando cada etapa do algoritmo (fechos-ε, criação de subconjuntos de estados e montagem da nova tabela de transição) através da porta `DidacticTracePort`.
  5. Obtém a entidade `AFD` retornada pelo serviço de domínio.
  6. Salva a nova entidade `AFD` no repositório.
  7. Recupera a lista de passos pedagógicos do `DidacticTracePort`.
  8. Mapeia o AFD para `AutomatonOutputDTO` e retorna o `ConverterAFNParaAFDOutputDTO`.
* **Fluxos Alternativos:**
  * **A1: Autômato não encontrado**
    1. Se o repositório retornar nulo para o ID fornecido, o caso de uso lança `AutomatoNaoEncontradoException`.
  * **A2: Autômato já é Determinístico (DFA)**
    1. Se o autômato recuperado for do tipo `DFA`, o caso de uso interrompe a operação e dispara `AutomatoJaDeterministaException`.
* **Validações:**
  * Existência do autômato de entrada e tipo compatível.
* **Exceções:**
  * `AutomatoNaoEncontradoException` (Aplicação)
  * `AutomatoJaDeterministaException` (Aplicação)

---

### 1.3. Caso de Uso: `SimularPalavra`
* **Objetivo:** Simular o processamento passo-a-passo de uma cadeia de símbolos em um autômato, reportando a aceitação e a árvore de execução para fins didáticos.
* **Entradas:** `SimularPalavraInputDTO`
* **Saídas:** `SimularPalavraOutputDTO`
* **DTOs:**
  * **`SimularPalavraInputDTO`**
    * `id_automato`: `UUID`
    * `palavra`: `str`
  * **`SimularPalavraOutputDTO`**
    * `aceita`: `bool`
    * `passos`: `list[PassoSimulacaoDTO]`
  * **`PassoSimulacaoDTO`**
    * `indice_simbolo`: `int`
    * `simbolo_lido`: `str`
    * `estados_ativos_antes`: `list[str]`
    * `transicoes_utilizadas`: `list[str]`
    * `estados_ativos_depois`: `list[str]`
* **Fluxo Principal:**
  1. O caso de uso recebe o `SimularPalavraInputDTO`.
  2. Recupera o autômato no repositório.
  3. Instancia o objeto de valor `Palavra` a partir da string recebida.
  4. Executa a validação se todos os caracteres da palavra são válidos no `Alfabeto` do autômato.
  5. Invoca o serviço de domínio `WordSimulator` injetando o autômato e a palavra.
  6. O serviço rastreia os estados ativos a cada transição (e calcula fechos-ε paralelos em caso de AFN), gravando as etapas no `DidacticTracePort`.
  7. Retorna se a palavra foi aceita e o detalhamento do rastro em `SimularPalavraOutputDTO`.
* **Fluxos Alternativos:**
  * **A1: Símbolo inválido no alfabeto**
    1. Se a criação do VO `Palavra` ou a validação de alfabeto indicar caracteres intrusos, lança `SimboloInvalidoNoAlfabetoException`.
* **Validações:**
  * Valida se a palavra possui símbolos externos ao alfabeto formal do autômato em simulação.
* **Exceções:**
  * `AutomatoNaoEncontradoException` (Aplicação)
  * `SimboloInvalidoNoAlfabetoException` (Aplicação)

---

### 1.4. Caso de Uso: `MinimizarAFD`
* **Objetivo:** Minimizar um AFD existente no sistema, eliminando estados inacessíveis e fundindo estados equivalentes.
* **Entradas:** `MinimizarAFDInputDTO`
* **Saídas:** `MinimizarAFDOutputDTO`
* **DTOs:**
  * **`MinimizarAFDInputDTO`**
    * `id_automato`: `UUID`
  * **`MinimizarAFDOutputDTO`**
    * `id_afd_minimizado`: `UUID`
    * `passos_didaticos`: `list[PassoDidaticoDTO]`
    * `automato_dto`: `AutomatonOutputDTO`
* **Fluxo Principal:**
  1. Recebe o `MinimizarAFDInputDTO`.
  2. Recupera o autômato no repositório.
  3. Valida se o autômato é do tipo `DFA`.
  4. Invoca o serviço de domínio `DfaMinimizer` que executa:
     * Remoção de estados inacessíveis por busca em largura.
     * Particionamento de equivalência (Hopcroft).
     * Registro das matrizes de partições intermediárias no `DidacticTracePort`.
  5. Persiste o AFD minimizado gerado.
  6. Retorna `MinimizarAFDOutputDTO`.
* **Fluxos Alternativos:**
  * **A1: Autômato é não-determinístico**
    1. Se o autômato de entrada for `NFA` ou `E_NFA`, interrompe a execução e dispara `AutomatoNaoDeterministaException`.
* **Validações:**
  * Tipo do autômato (deve ser deterministic).
* **Exceções:**
  * `AutomatoNaoDeterministaException` (Aplicação)
  * `AutomatoNaoEncontradoException` (Aplicação)

---

### 1.5. Caso de Uso: `ConverterAFParaGR`
* **Objetivo:** Traduzir um Autômato Finito (DFA/NFA) em uma Gramática Regular equivalente.
* **Entradas:** `ConverterAFParaGRInputDTO`
* **Saídas:** `ConverterAFParaGROutputDTO`
* **DTOs:**
  * **`ConverterAFParaGRInputDTO`**
    * `id_automato`: `UUID`
  * **`ConverterAFParaGROutputDTO`**
    * `id_gramatica`: `UUID`
    * `gramatica_dto`: `GrammarOutputDTO`
    * `passos_didaticos`: `list[PassoDidaticoDTO]`
* **Fluxo Principal:**
  1. Recebe `ConverterAFParaGRInputDTO`.
  2. Recupera o autômato no repositório.
  3. Invoca o serviço de domínio `AutomatonToGrammarConverter`.
  4. O serviço mapeia estados para variáveis ($Q \to V_N$), símbolos para terminais ($\Sigma \to V_T$), o estado inicial para símbolo de partida ($q_0 \to S$) e as transições para regras de produção ($P$), registrando o mapeamento passo a passo.
  5. Salva a nova `GramaticaRegular` gerada no repositório de gramáticas.
  6. Retorna `ConverterAFParaGROutputDTO`.
* **Fluxos Alternativos:**
  * **A1: Transições com palavra vazia (ε) no autômato**
    1. O serviço gera produções vazias ($A \to \epsilon$) e notifica didaticamente a tradução da aceitação direta.
* **Validações:**
  * Existência do autômato de origem.
* **Exceções:**
  * `AutomatoNaoEncontradoException` (Aplicação)

---

### 1.6. Caso de Uso: `ConverterGRParaAF`
* **Objetivo:** Converter uma Gramática Regular (linear à direita/esquerda) em um Autômato Finito Não-Determinístico equivalente.
* **Entradas:** `ConverterGRParaAFInputDTO`
* **Saídas:** `ConverterGRParaAFOutputDTO`
* **DTOs:**
  * **`ConverterGRParaAFInputDTO`**
    * `id_gramatica`: `UUID`
  * **`ConverterGRParaAFOutputDTO`**
    * `id_automato`: `UUID`
    * `automato_dto`: `AutomatonOutputDTO`
    * `passos_didaticos`: `list[PassoDidaticoDTO]`
* **Fluxo Principal:**
  1. Recebe `ConverterGRParaAFInputDTO`.
  2. Recupera a gramática regular no repositório.
  3. Invoca o serviço de domínio `GrammarToAutomatonConverter`.
  4. O serviço mapeia variáveis para estados ($V_N \to Q$), cria um estado de aceitação adicional se necessário para regras de parada, e converte regras de produção para transições, registrando o passo-a-passo.
  5. Persiste o autômato resultante no repositório.
  6. Retorna `ConverterGRParaAFOutputDTO`.
* **Fluxos Alternativos:**
  * **A1: Gramática não respeita regularidade formal**
    1. Se as regras de produção possuírem linearidades misturadas ou mais de duas variáveis no lado direito, o domínio acusa violação no método de validação.
    2. Caso de uso intercepta e dispara `GramaticaNaoRegularException`.
* **Validações:**
  * Valida invariante de regularidade da gramática (linearidade estrita à direita ou à esquerda).
* **Exceções:**
  * `GramaticaNaoEncontradaException` (Aplicação)
  * `GramaticaNaoRegularException` (Domínio/Aplicação)

---

### 1.7. Caso de Uso: `ExportarResultado`
* **Objetivo:** Exportar os modelos ou simulações para arquivos em formatos específicos de representação visual ou estruturada.
* **Entradas:** `ExportarResultadoInputDTO`
* **Saídas:** `ExportarResultadoOutputDTO`
* **DTOs:**
  * **`ExportarResultadoInputDTO`**
    * `id_entidade`: `UUID`
    * `tipo_entidade`: `str` (Ex: "AUTOMATO" ou "GRAMATICA")
    * `formato`: `str` (Ex: "DOT", "JSON", "JFLAP")
  * **`ExportarResultadoOutputDTO`**
    * `caminho_arquivo`: `str`
    * `conteudo`: `str` (Conteúdo serializado)
* **Fluxo Principal:**
  1. Recebe o `ExportarResultadoInputDTO`.
  2. Busca a entidade correspondente no respectivo repositório (`AutomatonRepositoryPort` ou `GrammarRepositoryPort`).
  3. Instancia o adaptador correto que implementa `ExporterPort` conforme o formato selecionado.
  4. Chama `ExporterPort.export(...)` passando a entidade.
  5. O adaptador gera a representação (ex: sintaxe DOT/Graphviz ou XML JFLAP) e a salva em arquivo, caso configurado.
  6. Retorna `ExportarResultadoOutputDTO` contendo o conteúdo serializado e o caminho físico do arquivo gerado.
* **Fluxos Alternativos:**
  * **A1: Formato não suportado**
    1. Lança `FormatoIncompativelException` se o formato solicitado não for implementado pelo tipo de entidade.
* **Validações:**
  * Suporte ao formato para a entidade específica.
* **Exceções:**
  * `EntidadeNaoEncontradaException` (Aplicação)
  * `FormatoIncompativelException` (Aplicação)

---

## UML Textual dos Use Cases (PlantUML)

```
@startuml
left to right direction
skinparam packageStyle rect

actor "Usuário / Cliente REST" as User

rectangle "Camada Application (Use Cases)" {
  usecase "CriarAFN" as UC_Criar
  usecase "ConverterAFNParaAFD" as UC_Determinar
  usecase "SimularPalavra" as UC_Simular
  usecase "MinimizarAFD" as UC_Minimizar
  usecase "ConverterAFParaGR" as UC_AF_GR
  usecase "ConverterGRParaAF" as UC_GR_AF
  usecase "ExportarResultado" as UC_Exportar
}

User --> UC_Criar
User --> UC_Determinar
User --> UC_Simular
User --> UC_Minimizar
User --> UC_AF_GR
User --> UC_GR_AF
User --> UC_Exportar

note right of UC_Determinar
  Gera passos didáticos
  usando DidacticTracePort
end note

note right of UC_Minimizar
  Exige tipo DFA
end note
@enduml
```

---

## Fluxograma Textual Geral de Execução

O fluxograma textual a seguir demonstra a dinâmica de execução a partir de uma solicitação de entrada até a saída estruturada:

```
[Início]
   |
   v
[Receber Request no Adaptador de Interface (CLI / Controller API)]
   |
   v
[Instanciar InputDTO correspondente]
   |
   v
[Validação Sintática do InputDTO (Camada de Aplicação)]
   |
   +---> [Invalido] ---> [Retornar Erro Sintático / HTTP 400]
   |
   +---> [Valido]
           |
           v
     [Executar Caso de Uso correspondente]
           |
           v
     [Recuperar Entidades do Repositório (se aplicável)]
           |
           +---> [Não Encontrado] ---> [Lançar RecursoNãoEncontradoException]
           |
           +---> [Encontrado]
                   |
                   v
             [Invocar Regras de Negócio e Serviços de Domínio]
                   |
                   v
             [Algoritmo de Domínio executa] --(escreve)--> [DidacticTracePort]
                   |
                   v
             [Retorna Nova Entidade / Status do Domínio]
                   |
                   v
             [Salvar Alterações (RepositoryPort) - se houver alteração]
                   |
                   v
             [Recuperar Logs Didáticos (TracePort)]
                   |
                   v
             [Mapear para OutputDTO (incluindo novo modelo + passos didáticos)]
                   |
                   v
             [Interface exibe no console em formato didático / envia JSON para React]
                   |
                   v
                 [Fim]
```
