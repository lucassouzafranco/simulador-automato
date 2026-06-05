# Especificações Formais e Algoritmos Matemáticos

Este documento detalha os algoritmos fundamentais da teoria da computação aplicados neste simulador. A notação e a linguagem adotadas seguem os padrões de rigor matemático de nível universitário.

---

## 1. ε-fechamento (Epsilon Closure)

### Fundamentação Teórica
Seja $M = (Q, \Sigma, \delta, q_0, F)$ um Autômato Finito Não-Determinístico com ε-transições (AFN-ε). O ε-fechamento de um estado $q \in Q$, denotado por $\epsilon\text{-closure}(q)$, é o conjunto de todos os estados alcançáveis a partir de $q$ usando exclusivamente transições rotuladas com o símbolo vazio $\epsilon$ (zero ou mais vezes).

Formalmente, definimos $\epsilon\text{-closure}(q)$ de forma indutiva:
1. **Base:** $q \in \epsilon\text{-closure}(q)$ (reflexividade).
2. **Indução:** Se $p \in \epsilon\text{-closure}(q)$ e $r \in \delta(p, \epsilon)$, então $r \in \epsilon\text{-closure}(q)$ (transitividade).

Para um conjunto de estados $T \subseteq Q$, o fechamento é definido como:
$$\epsilon\text{-closure}(T) = \bigcup_{t \in T} \epsilon\text{-closure}(t)$$

### Passo a Passo
1. Inicializar uma estrutura de dados de pilha (ou fila) `P` contendo todos os estados pertencentes ao conjunto inicial $T$.
2. Inicializar o conjunto resultado `R` com o próprio conteúdo de $T$.
3. Enquanto a pilha `P` contiver elementos:
   1. Desempilhar o estado de topo `t`.
   2. Localizar todas as transições imediatas por ε a partir de `t`, ou seja, o conjunto $U = \delta(t, \epsilon)$.
   3. Para cada estado $u \in U$:
      1. Se $u \notin R$:
         1. Adicionar $u$ a $R$.
         2. Empilhar $u$ em `P`.
4. Retornar o conjunto `R`.

### Pseudocódigo
```
Função calcular_fecho_epsilon(T: Conjunto[Estado], delta: FuncaoTransicao) -> Conjunto[Estado]:
    R = copiar_conjunto(T)
    P = criar_pilha()
    
    Para cada estado q em T:
        P.empilhar(q)
        
    Enquanto P não estiver vazia:
        t = P.desempilhar()
        Para cada estado u em delta(t, epsilon):
            Se u não pertence a R:
                R.adicionar(u)
                P.empilhar(u)
                
    Retornar R
```

### Complexidade Computacional
* **Complexidade Temporal:** $O(|Q| + |\delta_\epsilon|)$, onde $|Q|$ é o número de estados do autômato e $|\delta_\epsilon|$ é a quantidade de transições vazias presentes no grafo do autômato. No pior caso, cada nó e cada aresta vazia são visitados uma única vez.
* **Complexidade Espacial:** $O(|Q|)$ para armazenamento do conjunto de estados visitados e do vetor da pilha de execução.

### Exemplo Completo
Sejam os estados $Q = \{q_0, q_1, q_2\}$ e as transições $\delta(q_0, \epsilon) = \{q_1\}$, $\delta(q_1, \epsilon) = \{q_2\}$, $\delta(q_2, \epsilon) = \emptyset$.
Calcular $\epsilon\text{-closure}(\{q_0\})$:
* Inicialização: `R = {q_0}`, `P = [q_0]`.
* Iteração 1:
  * Desempilha `t = q_0`.
  * Transições vazias de $q_0$: $\delta(q_0, \epsilon) = \{q_1\}$.
  * Como $q_1 \notin R$, atualiza-se `R = {q_0, q_1}` e `P = [q_1]`.
* Iteração 2:
  * Desempilha `t = q_1`.
  * Transições vazias de $q_1$: $\delta(q_1, \epsilon) = \{q_2\}$.
  * Como $q_2 \notin R$, atualiza-se `R = {q_0, q_1, q_2}` e `P = [q_2]`.
* Iteração 3:
  * Desempilha `t = q_2`.
  * Transições vazias de $q_2$: $\delta(q_2, \epsilon) = \emptyset$.
  * Nada a inserir. A pilha esvazia.
* Retorno: `R = {q_0, q_1, q_2}`.

---

## 2. Construção dos Subconjuntos (Subset Construction)

### Fundamentação Teórica
Teorema de Rabin-Scott: Para cada autômato não-determinístico (com ou sem ε-transições) existe um autômato determinístico equivalente que aceita a mesma linguagem.
Dada a estrutura $N = (Q_N, \Sigma, \delta_N, q_0, F_N)$, a construção do AFD equivalente $D = (Q_D, \Sigma, \delta_D, q'_0, F_D)$ mapeia cada estado de $Q_D$ a um elemento do conjunto de partes de $Q_N$ ($Q_D \subseteq \mathcal{P}(Q_N)$).

As componentes de $D$ são definidas por:
* $q'_0 = \epsilon\text{-closure}(\{q_0\})$
* $\delta_D(R, a) = \epsilon\text{-closure}\left( \bigcup_{r \in R} \delta_N(r, a) \right)$
* $F_D = \{R \in Q_D \mid R \cap F_N \neq \emptyset\}$

### Passo a Passo
1. Computar o estado de partida do AFD: $q'_0 = \epsilon\text{-closure}(\{q_0\})$. Adicionar à lista de estados não-marcados.
2. Enquanto existirem subconjuntos não-marcados na lista:
   1. Selecionar e marcar um subconjunto de estados $U$.
   2. Para cada símbolo $a \in \Sigma$:
      1. Determinar o conjunto de transições de destino em $N$: $Dest = \bigcup_{u \in U} \delta_N(u, a)$.
      2. Calcular $T = \epsilon\text{-closure}(Dest)$.
      3. Se $T \neq \emptyset$:
         1. Se $T$ ainda não existe em $Q_D$:
            1. Adicionar $T$ a $Q_D$ como um estado não-marcado.
         2. Adicionar a transição determinística $\delta_D(U, a) = T$.
3. Definir o conjunto de aceitação $F_D$ contendo todos os subconjuntos de $Q_D$ que contêm ao menos um estado final de $F_N$.

### Pseudocódigo
```
Função determinizar_afn(N: AutomatoNFA) -> AutomatoDFA:
    q0_prime = calcular_fecho_epsilon({N.estado_inicial}, N.delta)
    Q_D = {q0_prime}
    nao_marcados = [q0_prime]
    delta_D = criar_dicionario_transicoes()
    
    Enquanto nao_marcados não estiver vazio:
        U = nao_marcados.remover_primeiro()
        Para cada simbolo a em N.alfabeto:
            Dest = uniao_transicoes(U, a, N.delta)
            T = calcular_fecho_epsilon(Dest, N.delta)
            Se T não é vazio:
                Se T não pertence a Q_D:
                    Q_D.adicionar(T)
                    nao_marcados.adicionar(T)
                delta_D.adicionar_transicao(U, a, T)
                
    F_D = {U em Q_D | U intersecao N.estados_finais não é vazia}
    Retornar criar_afd(Q_D, N.alfabeto, delta_D, q0_prime, F_D)
```

### Complexidade Computacional
* **Complexidade Temporal:** $O(2^{|Q_N|} \cdot |\Sigma| \cdot |Q_N|^2)$ no pior caso teórico. Embora o limite superior seja exponencial devido à explosão de subconjuntos, a maioria dos autômatos práticos resulta em um crescimento linear ou quadrático de estados.
* **Complexidade Espacial:** $O(2^{|Q_N|} \cdot |Q_N|)$ para armazenar os subconjuntos correspondentes aos estados mapeados no AFD.

### Exemplo Completo
AFN com alfabeto $\Sigma = \{a, b\}$, estados $Q_N = \{q_0, q_1\}$, inicial $q_0$, finais $F_N = \{q_1\}$.
Transições: $\delta(q_0, a) = \{q_0, q_1\}$, $\delta(q_0, b) = \{q_1\}$, $\delta(q_1, a) = \emptyset$, $\delta(q_1, b) = \{q_0, q_1\}$. Sem ε-transições.
* $q'_0 = \epsilon\text{-closure}(\{q_0\}) = \{q_0\}$.
* **Fila:** `[{q_0}]`.
* **Exploração $\{q_0\}$:**
  * Símbolo 'a': $Dest = \delta(q_0, a) = \{q_0, q_1\}$. Fecho-ε: $\{q_0, q_1\}$. Estado $\{q_0, q_1\}$ adicionado a $Q_D$ e à fila.
  * Símbolo 'b': $Dest = \delta(q_0, b) = \{q_1\}$. Fecho-ε: $\{q_1\}$. Estado $\{q_1\}$ adicionado a $Q_D$ e à fila.
* **Exploração $\{q_0, q_1\}$:**
  * Símbolo 'a': $Dest = \delta(q_0, a) \cup \delta(q_1, a) = \{q_0, q_1\} \cup \emptyset = \{q_0, q_1\}$. Já existe.
  * Símbolo 'b': $Dest = \delta(q_0, b) \cup \delta(q_1, b) = \{q_1\} \cup \{q_0, q_1\} = \{q_0, q_1\}$. Já existe.
* **Exploração $\{q_1\}$:**
  * Símbolo 'a': $Dest = \delta(q_1, a) = \emptyset$. Não gera transição.
  * Símbolo 'b': $Dest = \delta(q_1, b) = \{q_0, q_1\}$. Já existe.
* **Resultados:**
  * Estados do AFD: $Q_D = \{\{q_0\}, \{q_0, q_1\}, \{q_1\}\}$.
  * Transições:
    * $\{q_0\} \xrightarrow{a} \{q_0, q_1\}$
    * $\{q_0\} \xrightarrow{b} \{q_1\}$
    * \{q_0, q_1\} \xrightarrow{a} \{q_0, q_1\}
    * \{q_0, q_1\} \xrightarrow{b} \{q_0, q_1\}
    * $\{q_1\} \xrightarrow{b} \{q_0, q_1\}$
  * Estados Finais: $F_D = \{\{q_0, q_1\}, \{q_1\}\}$ (pois contêm $q_1$).

---

## 3. Simulação de AFD

### Fundamentação Teórica
O processamento de uma palavra (cadeia) $w = c_1 c_2 \dots c_n$ por um AFD $D = (Q, \Sigma, \delta, q_0, F)$ descreve um caminho no grafo de estados orientado pela função de transição estendida $\hat{\delta}: Q \times \Sigma^* \to Q$:
$$\hat{\delta}(q, \epsilon) = q$$
$$\hat{\delta}(q, xc) = \delta(\hat{\delta}(q, x), c) \quad \text{onde } x \in \Sigma^* \text{ e } c \in \Sigma$$

Uma cadeia $w$ é aceita se $\hat{\delta}(q_0, w) \in F$. Caso caia em uma transição indefinida ou termine em um estado $q \notin F$, a cadeia é rejeitada.

### Passo a Passo
1. Atribuir o estado de partida ao ponteiro de navegação: $curr = q_0$.
2. Para cada caractere $c_i$ da cadeia $w$:
   1. Consultar a tabela de transição para identificar $next = \delta(curr, c_i)$.
   2. Se $next$ for indefinido (transição nula):
      1. Interromper o processo e indicar **rejeição**.
   3. Atualizar o ponteiro: $curr = next$.
3. Ao fim da cadeia, verificar se $curr \in F$.
4. Se sim, retornar **aceito** (True), caso contrário retornar **rejeitado** (False).

### Pseudocódigo
```
Função simular_cadeia_afd(D: AutomatoDFA, w: Palavra) -> Booleano:
    curr = D.estado_inicial
    Para cada simbolo c em w.sequencia:
        next_state = D.obter_transicao(curr, c)
        Se next_state é nulo:
            Retornar Falso
        curr = next_state
    Retornar curr pertence_a D.estados_finais
```

### Complexidade Computacional
* **Complexidade Temporal:** $O(|w|)$, onde $|w|$ representa o comprimento da cadeia de entrada. Cada símbolo requer uma consulta direta indexada na tabela de transição (tempo constante $O(1)$).
* **Complexidade Espacial:** $O(1)$ constante, pois necessita apenas de variáveis para manter o estado corrente.

### Exemplo Completo
AFD com $Q = \{q_0, q_1\}$, $\Sigma = \{0, 1\}$, inicial $q_0$, final $\{q_1\}$. Transições: $\delta(q_0, 0) = q_0$, $\delta(q_0, 1) = q_1$, $\delta(q_1, 0) = q_1$, $\delta(q_1, 1) = q_0$.
Simular a palavra $w = "010"$:
* Inicialização: `curr = q_0`.
* Símbolo 1 ('0'): `next = delta(q_0, 0) = q_0`. `curr = q_0`.
* Símbolo 2 ('1'): `next = delta(q_0, 1) = q_1`. `curr = q_1`.
* Símbolo 3 ('0'): `next = delta(q_1, 0) = q_1`. `curr = q_1`.
* Finalização: Fim da palavra. Verifica: $q_1 \in \{q_1\}$? Sim. Palavra aceita.

---

## 4. Remoção de Estados Inacessíveis

### Fundamentação Teórica
Um estado $q \in Q$ de um autômato é dito inacessível se não puder ser alcançado a partir do estado inicial $q_0$ por meio de nenhuma sequência de transições de tamanho $k \ge 0$. Formalmente:
$$\text{Inacessíveis} = \{ q \in Q \mid \nexists w \in \Sigma^* \text{ tal que } \hat{\delta}(q_0, w) = q \}$$

Sua remoção limpa o grafo de transições sem afetar a linguagem regular reconhecida pelo modelo.

### Passo a Passo
1. Inicializar um conjunto de estados marcados como `alcancaveis = {q_0}`.
2. Inicializar uma fila de processamento `F = [q_0]`.
3. Enquanto `F` contiver estados:
   1. Desenfileirar o estado `t`.
   2. Para cada caractere do alfabeto $a \in \Sigma$:
      1. Encontrar o estado destino $u = \delta(t, a)$.
      2. Se $u \neq \emptyset$ e $u \notin alcancaveis$:
         1. Adicionar $u$ ao conjunto `alcancaveis`.
         2. Enfileirar $u$ em `F`.
4. Os estados inacessíveis são obtidos pela diferença complementar $Q \setminus alcancaveis$.
5. Expurgar os inacessíveis de $Q$, das transições $\delta$ e dos estados finais $F$.

### Pseudocódigo
```
Função podar_estados_inacessiveis(D: AutomatoDFA) -> AutomatoDFA:
    alcancaveis = {D.estado_inicial}
    fila = [D.estado_inicial]
    
    Enquanto fila não estiver vazia:
        t = fila.desenfileirar()
        Para cada simbolo a em D.alfabeto:
            u = D.obter_transicao(t, a)
            Se u não é nulo e u não pertence a alcancaveis:
                alcancaveis.adicionar(u)
                fila.enfileirar(u)
                
    novos_estados = alcancaveis
    novos_finais = D.estados_finais intersecao alcancaveis
    novas_transicoes = filtrar_transicoes(D.transicoes, alcancaveis)
    
    Retornar criar_afd(novos_estados, D.alfabeto, novas_transicoes, D.estado_inicial, novos_finais)
```

### Complexidade Computacional
* **Complexidade Temporal:** $O(|Q| \cdot |\Sigma|)$ para um autômato determinístico, já que o número de arestas do grafo a serem exploradas é o produto do número de estados pelo tamanho do alfabeto.
* **Complexidade Espacial:** $O(|Q|)$ para manter o conjunto e fila de busca em largura.

### Exemplo Completo
$Q = \{q_0, q_1, q_2\}$, inicial $q_0$, alfabeto $\{a\}$, transições $\delta(q_0, a) = q_0$, $\delta(q_2, a) = q_1$.
* Início: `alcancaveis = {q_0}`, `fila = [q_0]`.
* Iteração 1:
  * Desfila `t = q_0`.
  * Destino sob 'a': $u = \delta(q_0, a) = q_0$. Como já pertence a `alcancaveis`, nada muda.
  * A fila esvazia.
* Fim da busca. `alcancaveis = {q_0}`.
* Estados inacessíveis: $\{q_1, q_2\}$.
* Novo autômato possui apenas o estado $q_0$.

---

## 5. Particionamento Inicial (Minimização - Fase 1)

### Fundamentação Teórica
O algoritmo clássico de minimização de autômatos baseia-se na partição de estados em classes de equivalência. O passo de inicialização divide o conjunto completo de estados $Q$ em dois subconjuntos disjuntos fundamentais: estados finais (aceitam a palavra vazia $\epsilon$) e estados não-finais (rejeitam a palavra vazia $\epsilon$). Esse par de blocos é a partição de ordem zero, $P_0$.

### Passo a Passo
1. Agrupar os estados pertencentes ao conjunto de estados finais: $Group_1 = F$.
2. Agrupar os estados não pertencentes a $F$: $Group_2 = Q \setminus F$.
3. Se algum desses grupos for vazio (por exemplo, um autômato sem estados finais), ele é ignorado.
4. Retornar a lista de conjuntos $\{Group_1, Group_2\}$ como a partição inicial $P_0$.

### Pseudocódigo
```
Função criar_particao_inicial(D: AutomatoDFA) -> Lista[Conjunto[Estado]]:
    grupo_finais = D.estados_finais
    grupo_nao_finais = D.estados - D.estados_finais
    
    particao = []
    Se grupo_finais não é vazio:
        particao.adicionar(grupo_finais)
    Se grupo_nao_finais não é vazio:
        particao.adicionar(grupo_nao_finais)
        
    Retornar particao
```

### Complexidade Computacional
* **Complexidade Temporal:** $O(|Q|)$ para percorrer a lista de estados e separá-los baseando-se no conjunto hash de estados de aceitação.
* **Complexidade Espacial:** $O(|Q|)$ para as novas estruturas de dados dos grupos formados.

### Exemplo Completo
AFD com estados $Q = \{A, B, C, D\}$, finais $F = \{C\}$.
* $Group_1 = \{C\}$
* $Group_2 = \{A, B, D\}$
* Partição inicial $P_0 = \{\{C\}, \{A, B, D\}\}$.

---

## 6. Refinamento de Partições (Minimização - Fase 2)

### Fundamentação Teórica
Dada uma partição atual $P_k$, refinamos a partição para gerar $P_{k+1}$. Dois estados $p$ e $q$ que pertencem a uma mesma classe de equivalência $C \in P_k$ permanecerão na mesma classe em $P_{k+1}$ se, e somente se, para cada símbolo $a \in \Sigma$, as suas transições $\delta(p, a)$ e $\delta(q, a)$ caírem em estados que pertencem a uma mesma classe de equivalência em $P_k$. Se para algum símbolo de entrada os destinos caírem em blocos separados, a classe $C$ deve ser cindida (refinada). O algoritmo atinge o ponto fixo quando $P_{k+1} = P_k$.

### Passo a Passo
1. Seja $P_{corrente}$ a partição inicial $P_0$.
2. Definir flag de iteração `mudou = True`.
3. Enquanto `mudou == True`:
   1. Setar `mudou = False`.
   2. Criar uma lista vazia para a nova partição: $P_{proxima} = []$.
   3. Para cada grupo $C$ pertencente a $P_{corrente}$:
      1. Subdividir $C$ em subgrupos equivalentes: dois estados $p, q \in C$ estão no mesmo subgrupo se, para todo símbolo $a \in \Sigma$, os estados de destino $\delta(p, a)$ e $\delta(q, a)$ residem no mesmo bloco da partição $P_{corrente}$.
      2. Adicionar os subgrupos gerados a $P_{proxima}$.
      3. Se o número de subgrupos gerados for maior do que 1 (cisão ocorreu):
         1. Setar `mudou = True`.
   4. Atualizar $P_{corrente} = P_{proxima}$.
4. Retornar a partição de classes de equivalência final.

### Pseudocódigo
```
Função refinar_particoes(D: AutomatoDFA, P0: Lista[Conjunto[Estado]]) -> Lista[Conjunto[Estado]]:
    P_corrente = P0
    refinando = Verdadeiro
    
    Enquanto refinando:
        P_proxima = []
        Para cada classe C em P_corrente:
            subclasses = dividir_classe_com_base_nas_transicoes(C, P_corrente, D)
            P_proxima.adicionar_todas(subclasses)
            
        Se tamanho(P_proxima) == tamanho(P_corrente):
            refinando = Falso
        Senao:
            P_corrente = P_proxima
            
    Retornar P_corrente
```

### Complexidade Computacional
* **Complexidade Temporal:** $O(|\Sigma| \cdot |Q| \log |Q|)$ utilizando a técnica do "menor subgrupo" proposta por Hopcroft, ou $O(|\Sigma| \cdot |Q|^2)$ na modelagem elementar clássica de Moore baseada em tabelas de transições.
* **Complexidade Espacial:** $O(|Q|)$ para armazenar o conjunto de divisões das classes.

### Exemplo Completo
Partição atual $P_k = \{\{C\}, \{A, B, D\}\}$. Alfabeto $\{a\}$. Transições: $\delta(A, a) = B$, $\delta(B, a) = D$, $\delta(D, a) = C$.
Avaliar cisão da classe $\{A, B, D\}$:
* Para o estado $A$: destino $\delta(A, a) = B$. O estado $B$ pertence ao bloco $\{A, B, D\}$ em $P_k$.
* Para o estado $B$: destino $\delta(B, a) = D$. O estado $D$ pertence ao bloco $\{A, B, D\}$ em $P_k$.
* Para o estado $D$: destino $\delta(D, a) = C$. O estado $C$ pertence ao bloco $\{C\}$ em $P_k$.
Como $D$ realiza uma transição para um bloco diferente de $A$ e $B$, a classe $\{A, B, D\}$ é cindida.
Nova partição: $P_{k+1} = \{\{C\}, \{D\}, \{A, B\}\}$.

---

## 7. Construção do AFD Minimizando (Minimização - Fase 3)

### Fundamentação Teórica
A partir da partição de estados refinada final de Myhill-Nerode, $P_{final} = \{C_1, C_2, \dots, C_m\}$, definimos a redução formal do autômato determinístico mínimo $M_{min} = (Q_{min}, \Sigma, \delta_{min}, S_0, F_{min})$ de modo que:
* $Q_{min} = P_{final}$ (cada classe de equivalência se torna um estado do novo autômato).
* $S_0 = C_i$ tal que $q_0 \in C_i$.
* $F_{min} = \{ C_i \in P_{final} \mid C_i \cap F \neq \emptyset \}$.
* $\delta_{min}(C_i, a) = C_j$ se, para um estado qualquer $q \in C_i$, temos $\delta(q, a) \in C_j$.

### Passo a Passo
1. Para cada conjunto/classe de equivalência $C_i$ em $P_{final}$, instanciar um novo estado identificável $S_i$.
2. Identificar a classe contendo o estado de partida original $q_0$; associá-la como o novo `estado_inicial` $S_0$.
3. Localizar todas as classes de equivalência que contêm ao menos um estado original que pertencia a $F$; marcá-las como `estados_finais`.
4. Para cada classe $C_i$ e caractere $a \in \Sigma$:
   1. Escolher um estado representante qualquer $q \in C_i$.
   2. Determinar para qual estado $u$ ocorria a transição original: $u = \delta(q, a)$.
   3. Localizar qual classe $C_j \in P_{final}$ contém o estado $u$.
   4. Construir a transição minimizada no novo autômato: $\delta_{min}(S_i, a) = S_j$.
5. Instanciar o AFD Mínimo.

### Pseudocódigo
```
Função construir_automato_minimo(D: AutomatoDFA, P_final: Lista[Conjunto[Estado]]) -> AutomatoDFA:
    novos_estados = []
    mapa_estados = criar_mapa()
    
    Para cada classe C em P_final:
        rotulo = gerar_nome_unico(C)
        novo_est = Estado(rotulo)
        novos_estados.adicionar(novo_est)
        Para cada estado original q em C:
            mapa_estados.salvar(q, novo_est)
            
    novo_inicial = mapa_estados.buscar(D.estado_inicial)
    novos_finais = {mapa_estados.buscar(q) para q em D.estados_finais}
    novas_transicoes = []
    
    Para cada classe C em P_final:
        rep = C.obter_qualquer()
        Para cada simbolo a em D.alfabeto:
            dest_orig = D.obter_transicao(rep, a)
            Se dest_orig não é nulo:
                est_orig = mapa_estados.buscar(rep)
                est_dest = mapa_estados.buscar(dest_orig)
                novas_transicoes.adicionar(Transicao(est_orig, a, est_dest))
                
    Retornar criar_afd(novos_estados, D.alfabeto, novas_transicoes, novo_inicial, novos_finais)
```

### Complexidade Computacional
* **Complexidade Temporal:** $O(|P_{final}| \cdot |\Sigma|)$ para mapear as novas transições dos estados aglutinados.
* **Complexidade Espacial:** $O(|Q|)$ para persistência das tabelas hash de translação de estados antigos para estados reduzidos.

### Exemplo Completo
Seja o autômato original com transições $\delta(A, a) = B$, $\delta(B, a) = C$, $\delta(C, a) = C$, inicial $A$, finais $\{C\}$.
A partição final calculada foi: $P_{final} = \{\{A\}, \{B\}, \{C\}\}$.
* Novas variáveis de estado: $S_A$ para $\{A\}$, $S_B$ para $\{B\}$, $S_C$ para $\{C\}$.
* Inicial: $S_A$ (pois contém $A$).
* Finais: $\{S_C\}$ (pois contém $C$).
* Transições:
  * De $S_A$ sob 'a': representante $A$ vai para $B \in S_B$. Logo, $S_A \xrightarrow{a} S_B$.
  * De $S_B$ sob 'a': representante $B$ vai para $C \in S_C$. Logo, $S_B \xrightarrow{a} S_C$.
  * De $S_C$ sob 'a': representante $C$ vai para $C \in S_C$. Logo, $S_C \xrightarrow{a} S_C$.

---

## 8. Conversão AF para Gramática Regular

### Fundamentação Teórica
Qualquer linguagem regular reconhecida por um autômato finito $M = (Q, \Sigma, \delta, q_0, F)$ pode ser gerada por uma gramática regular linear à direita $G = (V_N, V_T, P, S)$. O mapeamento direto estabelece que:
* $V_N = \{ V_q \mid q \in Q \}$ (cada estado vira uma variável não-terminal).
* $V_T = \Sigma$ (o alfabeto de entrada equivale aos símbolos terminais).
* $S = V_{q_0}$ (a variável associada ao estado de partida vira o símbolo inicial).
* As produções $P$ são criadas a partir das transições e estados de aceitação:
  * Se $\delta(q_i, a) \ni q_j$, então $V_{q_i} \to a V_{q_j} \in P$.
  * Se $q_i \in F$, então $V_{q_i} \to \epsilon \in P$.

### Passo a Passo
1. Criar um símbolo não-terminal $A_i \in V_N$ para cada estado $q_i \in Q$.
2. Definir $V_T$ como os elementos do alfabeto do autômato $\Sigma$.
3. Definir a variável inicial $S$ como o não-terminal correspondente ao estado inicial $q_0$.
4. Para cada transição direcional $(q_i, a, q_j)$ presente em $\delta$:
   1. Inserir a regra de produção: $A_i \to a A_j$.
5. Para cada estado de aceitação $q_f \in F$:
   1. Inserir a regra de produção de parada: $A_f \to \epsilon$.
6. Retornar a gramática regular formada.

### Pseudocódigo
```
Função converter_afn_para_gramatica(M: Automato) -> GramaticaRegular:
    V_N = criar_conjunto_nao_terminais(M.estados)
    V_T = criar_conjunto_terminais(M.alfabeto)
    S = obter_nao_terminal(M.estado_inicial)
    P = []
    
    Para cada transicao em M.transicoes:
        origem = obter_nao_terminal(transicao.origem)
        simbolo = obter_terminal(transicao.simbolo)
        destino = obter_nao_terminal(transicao.destino)
        P.adicionar(Producao(origem, (simbolo, destino)))
        
    Para cada est em M.estados_finais:
        origem = obter_nao_terminal(est)
        P.adicionar(Producao(origem, (SimboloVazioEpsilon)))
        
    Retornar criar_gramatica(V_N, V_T, P, S)
```

### Complexidade Computacional
* **Complexidade Temporal:** $O(|\delta| + |F|)$, onde $|\delta|$ representa a quantidade de transições e $|F|$ o tamanho do conjunto de estados finais. O algoritmo executa um único mapeamento linear de cada transição e estado final em regras de produção regulares.
* **Complexidade Espacial:** $O(|\delta| + |F|)$ de espaço para gravação das regras de produção intermediárias e estruturas de dados de saída.

### Exemplo Completo
Autômato com $Q = \{q_0, q_1\}$, $\Sigma = \{0, 1\}$, inicial $q_0$, finais $\{q_1\}$. Transições: $\delta(q_0, 0) = \{q_0\}$, $\delta(q_0, 1) = \{q_1\}$, $\delta(q_1, 0) = \{q_1\}$.
* Variáveis Não-Terminais: $V_N = \{Q_0, Q_1\}$. Terminais: $V_T = \{0, 1\}$. Partida: $Q_0$.
* Produções geradas por transições:
  * $q_0 \xrightarrow{0} q_0 \implies Q_0 \to 0 Q_0$
  * $q_0 \xrightarrow{1} q_1 \implies Q_0 \to 1 Q_1$
  * $q_1 \xrightarrow{0} q_1 \implies Q_1 \to 0 Q_1$
* Produções geradas por estados finais:
  * $q_1 \in F \implies Q_1 \to \epsilon$.
* Gramática final resultante:
  $$G = (\{Q_0, Q_1\}, \{0, 1\}, P, Q_0)$$
  $$P = \{ Q_0 \to 0 Q_0 \mid 1 Q_1, \quad Q_1 \to 0 Q_1 \mid \epsilon \}$$

---

## 9. Conversão Gramática Regular para AF

### Fundamentação Teórica
Uma gramática regular linear à direita $G = (V_N, V_T, P, S)$ pode ser mapeada em um Autômato Finito Não-Determinístico equivalente $M = (Q, \Sigma, \delta, q_0, F)$. O procedimento clássico de síntese do autômato mapeia:
* Cada variável não-terminal em um estado correspondente do autômato: $\{ q_A \mid A \in V_N \}$.
* Cria-se um estado adicional de aceitação final $q_{acc}$ para gerenciar regras de produção que geram terminais puros sem variáveis à direita.
* O alfabeto de entrada $\Sigma = V_T$.
* O estado inicial $q_0 = q_S$.
* O mapeamento de produções para transições e finais ocorre da seguinte maneira:
  * Regras do formato $A \to aB$ geram a transição $\delta(q_A, a) \ni q_B$.
  * Regras do formato $A \to a$ geram a transição $\delta(q_A, a) \ni q_{acc}$.
  * Regras do formato $A \to \epsilon$ adicionam o estado $q_A$ ao conjunto de estados finais $F$.

### Passo a Passo
1. Instanciar o conjunto de estados do autômato $Q$ contendo um nó correspondente para cada não-terminal $A \in V_N$ e adicionar um nó final extra chamado `q_acc`.
2. Definir o alfabeto $\Sigma$ com os elementos de $V_T$.
3. Definir o estado inicial $q_0$ correspondente ao símbolo inicial $S$.
4. Definir o conjunto de estados de aceitação inicial contendo o estado extra: $F = \{q_{acc}\}$.
5. Para cada produção em $P$:
   1. Se a produção for do tipo $A \to aB$:
      1. Adicionar transição $\delta(q_A, a) \ni q_B$.
   2. Se a produção for do tipo $A \to a$:
      1. Adicionar transição $\delta(q_A, a) \ni q_{acc}$.
   3. Se a produção for do tipo $A \to \epsilon$:
      1. Adicionar o estado $q_A$ ao conjunto de aceitação $F$.
6. Retornar o AFN equivalente.

### Pseudocódigo
```
Função converter_gramatica_para_afn(G: GramaticaRegular) -> AutomatoNFA:
    estados = {Estado(v.rotulo) para v em G.variaveis}
    est_aceitacao = Estado("q_acc")
    estados.adicionar(est_aceitacao)
    
    alfabeto = Alfabeto(G.terminais)
    inicial = Estado(G.simbolo_inicial.rotulo)
    finais = {est_aceitacao}
    transicoes = []
    
    Para cada prod em G.producoes:
        origem = Estado(prod.esquerda.rotulo)
        Se prod.tipo == TERMINAL_VARIAVEL:
            caractere = prod.direita[0]
            destino = Estado(prod.direita[1].rotulo)
            transicoes.adicionar(Transicao(origem, caractere, destino))
        Senao se prod.tipo == TERMINAL:
            caractere = prod.direita[0]
            transicoes.adicionar(Transicao(origem, caractere, est_aceitacao))
        Senao se prod.tipo == VAZIA:
            finais.adicionar(origem)
            
    Retornar criar_afn(estados, alfabeto, transicoes, inicial, finais)
```

### Complexidade Computacional
* **Complexidade Temporal:** $O(|P|)$, onde $|P|$ representa a quantidade total de produções na gramática de origem. Cada regra de substituição é lida e convertida em tempo constante em transições ou sinalizações de aceitação no autômato.
* **Complexidade Espacial:** $O(|P|)$ para alocar e persistir os estados de destino e vetores de transição.

### Exemplo Completo
Gramática linear à direita com não-terminais $\{S, A\}$, terminais $\{a, b\}$, símbolo inicial $S$. Produções $P = \{ S \to aA, S \to b, A \to aS, A \to \epsilon \}$.
* Estados do autômato: $Q = \{S, A, q_{acc}\}$, inicial $S$, alfabeto $\Sigma = \{a, b\}$, finais iniciais $F = \{q_{acc}\}$.
* Processando produções:
  * $S \to aA \implies \delta(S, a) \ni A$.
  * $S \to b \implies$ (produção simples para terminal) $\implies \delta(S, b) \ni q_{acc}$.
  * $A \to aS \implies \delta(A, a) \ni S$.
  * $A \to \epsilon \implies$ (produção vazia) $\implies$ adiciona $A$ aos estados finais: $F = \{q_{acc}, A\}$.
* Retorna o AFN gerado correspondente.
