# Suíte Completa de Testes

Organizada por módulo e prioridade.

---

# A. Determinização (AFN  AFD)

## D1. Estado inacessível

Estados:
q0,q1,q2,q3

Transições:
q0,a,q1
q1,b,q2
q3,a,q3
q3,b,q3

Esperado:
* q3 nunca aparece no AFD.
* Apenas estados alcançáveis são gerados.

---

## D2. Estado morto

q0,a,q1
q0,b,qd
q1,a,q1
q1,b,qd
qd,a,qd
qd,b,qd

Esperado:
* Determinização preserva linguagem.
* Estado morto tratado corretamente.

---

## D3. AFN com múltiplos destinos

q0,a,q0
q0,a,q1
q1,b,q2

Esperado:
{q0}
{q0,q1}
{q2}

---

## D4. Explosão de subconjuntos

q0,a,q0
q0,a,q1

q1,a,q1
q1,a,q2

q2,a,q2
q2,a,q3

q3,a,q3
q3,a,q4

Esperado:
Múltiplos subconjuntos distintos.

---

## D5. AFN-ε com ramificações

q0,ε,q1
q0,ε,q2

q1,a,q1
q1,b,q3

q2,b,q2
q2,a,q3

Esperado:
ε-closure(q0)={q0,q1,q2}

---

## D6. Ciclo de ε

q0,ε,q1
q1,ε,q2
q2,ε,q0

Esperado:
ε-closure(q0)={q0,q1,q2}
Sem loop infinito.

---

## D7. Final alcançado apenas por ε

q0,ε,q1
q1 final.

Esperado:
Estado inicial do AFD já é final.

---

## D8. Fecho ε vazio

AFN sem transições.

Esperado:
1 estado
0 transições

---

## D9. Subconjunto repetido

q0,a,q1
q0,b,q1

Esperado:
{q1}
criado apenas uma vez.

---

## D10. Ordenação natural

Estados:
q1,q2,q10

Esperado:
{q1,q2,q10}
não:
{q1,q10,q2}

---

# B. Minimização

## M1. Estados equivalentes

Estados:
A,B,C,D,E,F

Transições:
A,0,B
A,1,E

B,0,C
B,1,F

E,0,D
E,1,F

C,0,C
C,1,C

D,0,D
D,1,D

F,0,F
F,1,F

Esperado:
B  E
C  D

Resultado:
6  4 estados

---

## M2. AFD já mínimo

Esperado:
n  n

---

## M3. Estado inacessível

Estado isolado:
qx

Esperado:
Removido.

---

## M4. Estado morto equivalente

qd1
qd2
Ambos mortos.

Esperado:
Fundidos.

---

## M5. Todos os estados finais

F = Q

Esperado:
Sem erro.

---

## M6. Nenhum estado final

F = 

Esperado:
Sem erro.

---

## M7. Refinamento múltiplo

Partições precisam evoluir:
P0  P1  P2

Esperado:
Refinamento completo.

---

## M8. Refinamento com mesmo número de blocos

Objetivo:
Detectar possível bug em:
len(proximas_particoes) == len(particoes)

Esperado:
Não encerrar prematuramente.

---

# C. Simulação de AFD

## S1. Palavra aceita

q0,a,q1
q1,b,q1

Testes:
ab
abb
abbb
Aceita.

---

## S2. Palavra rejeitada

Mesmo AFD.
ε
b
ba
Rejeita.

---

## S3. Palavra vazia

Estado inicial final.
ε
Aceita.

---

## S4. Símbolo inválido

Alfabeto:
a,b

Palavra:
abc

Esperado:
Erro.

---

## S5. Transição inexistente

q0,a,q1

Palavra:
ab

Esperado:
Rejeição imediata.

---

# D. Simulação de AFN

## S6. AFN com dois caminhos aceitando

q0,a,q1
q0,a,q2

q1,b,qf
q2,c,qf

Palavras:
ab
ac
Aceitas.

---

## S7. Apenas um caminho aceita

q0,a,q1
q0,a,q2

q1,b,qf

Palavra:
ab
Aceita.

---

## S8. Nenhum estado ativo

q0,a,q1

Palavra:
ab

Esperado:
Nenhum estado ativo restante

---

## S9. Palavra vazia com ε

q0,ε,q1
q1 final.

Palavra:
ε
Aceita.

---

# E. Linguagens especiais

## L1. Linguagem vazia

Sem estados finais.

Esperado:
Tudo rejeitado.

---

## L2. Linguagem {ε}

Estado inicial final.
Sem transições.

Esperado:
ε -> aceita
a -> rejeita

---

## L3. Linguagem a*

q0 final
q0,a,q0

Esperado:
ε
a
aa
aaa
Aceitas.

---

# F. Conversão Autômato  Gramática

## G1. AFD simples

q0,a,q1
q1,b,q1

Esperado:
Q0 -> aQ1
Q1 -> bQ1
Q1 -> ε

---

## G2. Estado inicial final

q0 final
q0,a,q0

Esperado:
Criação de:
S_start

---

## G3. Linguagem {ε}

Esperado:
S -> ε

---

## G4. Produções de parada

Cada estado final gera:
A -> ε

---

## G5. Conflito com S_start

Gramática já possui:
S_start

Esperado:
S_start_
S_start__
...

---

# G. Conversão Gramática  AFN

## GA1. Linear à direita

S -> aA
A -> bB
B -> c

Esperado:
AFN equivalente.

---

## GA2. Produção terminal

A -> a

Esperado:
Transição para:
q_acc

---

## GA3. Produção vazia

A -> ε

Esperado:
Estado marcado final.

---

## GA4. Linear à esquerda

S -> Aa
A -> Bb
B -> c

Esperado:
Conversão correta.

---

## GA5. Linear à esquerda com ε

Testar:
A -> ε

Esperado:
Transição ε a partir de:
q_init

---

# H. Testes de Consistência

## C1. AFD  Gramática  AFD

Comparar:
* palavras aceitas
* palavras rejeitadas

---

## C2. AFN  Gramática  AFN

Comparar linguagem.

---

## C3. Gramática  AFN  Gramática

Comparar linguagem.

---

## C4. a*

Automato:
q0 final
q0,a,q0

Fluxo:
Automato
 Gramática
 AFN
 AFD
 Minimização

Esperado:
Mesma linguagem.

---

## C5. Linguagem {ε}

Mesmo fluxo.

Esperado:
Preservação total.

---

# I. Teste de Estresse

## E1. Explosão de subconjuntos

Estados:
q0,q1,q2,q3,q4,q5,q6,q7

Para cada:
qi,a,qi
qi,a,q(i+1)

Esperado:
Grande quantidade de subconjuntos.

Valida:
* desempenho
* filas
* hashing de conjuntos
* estados duplicados

---

# Casos com maior probabilidade de revelar bugs

Se eu tivesse que escolher apenas 10 testes críticos:
1. D3 (AFN múltiplos destinos)
2. D5 (AFN-ε com ramificações)
3. D6 (ciclo ε)
4. M1 (estados equivalentes)
5. M8 (refinamento com mesma cardinalidade)
6. S8 (nenhum estado ativo)
7. G2 (estado inicial final)
8. GA4 (gramática linear à esquerda)
9. C1 (AFDGAFD)
10. C4 (`a*` completo)
