O sistema é um simulador de teoria da computação que materializa conceitos matemáticos abstratos — como autômatos finitos e linguagens formais — em código operável. O problema real que ele resolve é separar a pureza das regras matemáticas da infraestrutura de software necessária para recebê-las de uma interface web, manipulá-las no banco de dados e expor resultados via API. Para isso, o sistema adota uma divisão estrutural estrita: o núcleo (`core/`) isola a lógica proposicional e os teoremas, enquanto a camada de aplicação (`application/`) assume apenas a orquestração do transporte de dados.

Muitas aplicações tradicionais acidentalmente misturam a lógica de negócios (aqui, as provas matemáticas) com o acesso a dados ou o tratamento de requisições. Quando um autômato possui uma transição vazia acidental enquanto deveria ser determinístico, e isso não é validado isoladamente em seu núcleo, o erro matemático se propaga e quebra toda a pilha de execução e persistência.

A resposta adotada foi particionar rigidamente o código, evitando anomalias. Por exemplo, um Autômato Finito Determinístico (AFD) não pode, por definição teórica formal, conter transições por épsilon ($\epsilon$). Isso é garantido estritamente de forma independente através do método interno de validação `_validar_determinismo()` da própria classe de entidade `AFD`.

### As frentes de divisão do núcleo

Para resolver a complexidade intrínseca da teoria, o diretório `core/` foi fatiado de forma contundente em três frentes complementares.

A primeira frente lida com as Regras de Formação, ou seja, o que constitui um modelo matemático válido. Em vez de espalhar checagens pela base de código, as entidades e os objetos de valor que vivem em `core/entities/` são blindados logo em sua inicialização. O método `__post_init__` localizado em `core/entities/automato.py` garante imediatamente que nenhum estado inicial possa ser definido se não pertencer ao conjunto global de estados. Isso evita a criação de qualquer "aberração matemática" no sistema.

A segunda frente foca nas Operações de Transformação, as implementações práticas dos teoremas acadêmicos. O diretório `core/services/` isola a matemática estrutural pesada. É ali que a Construção de Subconjuntos habita dentro do arquivo `determinizador.py`, permitindo converter um Autômato Finito Não-Determinístico (AFN) em AFD. Lá também se encontra o Teorema de Equivalência em `conversor_gram_automato.py` (transformando uma gramática regular num AFN) e o algoritmo de minimização em `minimizador.py`, que executa de forma limpa a remoção de inalcançáveis e o agrupamento de estados equivalentes.

A terceira frente materializa a Operação de Reconhecimento: a execução literal da máquina matemática. O motor de leitura contido em `simulador_palavra.py` serve como a codificação exata da função programa (a função estendida $\hat{\delta}$). Ele consome uma cadeia linear de caracteres (palavra), navega de forma recursiva pelo grafo dos estados — ramificando caso encontre o não-determinismo característico de um AFN — e retorna uma confirmação de pertencimento à linguagem daquele autômato, tudo sem sequer saber da existência de interfaces web ou banco de dados.

### O papel puramente logístico da Orquestração

Ao removermos todo esse encargo teórico e delegarmos ao núcleo, compreendemos o motivo da simplicidade exterior. A camada `application/use_cases/` abriga os processos organizacionais de alto nível e não possui um pingo de teoria computacional. Os "Casos de Uso" servem apenas como maestros da operação.

A rotina de um maestro é puramente logística: ele aciona a base de dados (Repositório) buscando um autômato a partir do seu ID. Em seguida, entrega a entidade encontrada para o arquivo `determinizador.py` fazer a conversão pesada em memória. Recebendo de volta o novo artefato do núcleo, o maestro armazena no banco de dados, compila para formato JSON e envia o retorno limpo de volta à aplicação web externa.

```python
# Exemplo conceitual da divisão no arquivo: application/use_cases/converter_afn_afd.py
class ConverterAFNparaAFDUseCase:
    def __init__(self, repositorio: AutomatoRepository, determinizador: DeterminizadorService):
        self.repositorio = repositorio
        self.determinizador = determinizador

    def executar(self, id_afn: str) -> dict:
        # 1. Logística de Busca: Comunica com o mundo externo (banco)
        afn = self.repositorio.buscar_por_id(id_afn)
        
        # 2. Transformação Teórica: Delegação cega para o núcleo matemático
        afd = self.determinizador.converter(afn)
        
        # 3. Logística de Resposta: Persistência e serialização
        self.repositorio.salvar(afd)
        return afd.to_dict()
```
O trecho exposto reflete claramente a regra de decisão: a camada estrutural externa nunca deve saber *como* a construção de subconjuntos afeta as transições algébricas, restringindo-se unicamente ao papel de controlar a direção do fluxo.

| Camada | Responsabilidade | Exemplo | Conhecimento sobre o mundo externo |
|---|---|---|---|
| Core (Entities) | Regras de Formação (o que é válido) | `__post_init__` no Autômato | Nenhum |
| Core (Services) | Teoremas e Reconhecimento da máquina | `DeterminizadorService` | Nenhum |
| Application (Use Cases)| Logística, transporte e persistência | `ConverterAFNparaAFDUseCase` | Comunica com o Repositório e Interface Web |

### Essência

A arquitetura geral funciona como uma bolha de vidro. O núcleo (`core/`) existe como um motor inteiramente independente e imutável que blinda a pureza algébrica de uma teoria da computação. Enquanto ele processa e garante as invariantes internas, as camadas externas (`application/`) limitam-se a transportar esses dados entre clientes, discos e o motor computacional.

---

### Termos Técnicos

**Autômato Finito Determinístico (AFD)**  
Máquina de estados onde cada estado tem exatamente uma única transição definida por símbolo do alfabeto, sendo impossível qualquer transição vazia.

**Autômato Finito Não-Determinístico (AFN)**  
Máquina que permite múltiplas transições por um mesmo símbolo para diferentes estados ou transições instantâneas que independem de qualquer leitura de símbolo ($\epsilon$).

**Construção de Subconjuntos**  
Algoritmo de conversão que extrai um novo estado macro determinístico compondo as possíveis ramificações combinadas de um AFN, mantendo exatamente a mesma linguagem.

**Função Programa ($\hat{\delta}$)**  
Função estendida de transição matemática onde a leitura avança iterativamente sobre todos os símbolos de uma cadeia (palavra) inteira em vez de avaliar apenas o primeiro passo.
