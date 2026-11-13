# Implementacao e Analise de Estrategias de Algoritmos para Escalonamento de Tarefas

**Integrantes (ordem alfabetica):** [NOME COMPLETO - MATRICULA]; [NOME COMPLETO - MATRICULA]; [NOME COMPLETO - MATRICULA]; [NOME COMPLETO - MATRICULA]

## 1. Introducao

Escalonar tarefas significa decidir quando e em qual recurso cada atividade sera executada. O problema aparece na alocacao de processos em processadores, no planejamento de projetos, em linhas de producao, na computacao em nuvem e na organizacao de equipes. Mesmo pequenas alteracoes no modelo podem mudar sua complexidade; por isso, este trabalho fixa formalmente a variante estudada.

Sao dadas `n` tarefas. Cada tarefa `j` possui uma duracao inteira positiva `p_j`. Ha `m >= 2` maquinas identicas, cada uma capaz de executar no maximo uma tarefa por vez. Uma relacao de precedencia `i -> j` obriga a conclusao de `i` antes do inicio de `j`. As tarefas nao podem ser interrompidas e cada tarefa usa exatamente uma maquina. Dado um prazo global `D`, a pergunta de decisao e: existe um escalonamento valido cujo tempo de conclusao da ultima tarefa (`C_max`, ou *makespan*) seja menor ou igual a `D`? Na notacao classica, a versao de otimizacao e `P|prec|C_max`.

Essa formulacao evita uma ambiguidade do enunciado. Com apenas uma maquina, nenhuma data de liberacao e um unico prazo global, a ordem nao altera a soma das duracoes: depois de verificar que o grafo e aciclico, bastaria testar `sum(p_j) <= D`. A existencia de maquinas paralelas e a decisao de como distribuir tarefas entre elas tornam o problema combinatorio.

## 2. Prova de que o problema pertence a NP

### 2.1 Pertinencia a NP

Um certificado e uma lista com, para cada tarefa, a maquina escolhida e os tempos inteiros de inicio e fim. Um verificador confere em tempo polinomial:

1. se cada tarefa aparece exatamente uma vez;
2. se `fim_j - inicio_j = p_j` e os tempos sao nao negativos;
3. se intervalos na mesma maquina nao se sobrepoem;
4. se, para toda precedencia `i -> j`, vale `fim_i <= inicio_j`;
5. se o maior tempo de fim e no maximo `D`.

Ordenando os intervalos de cada maquina, a verificacao custa `O(n log n + |E|)`, onde `E` e o conjunto de precedencias. Logo, o problema pertence a NP.

### 2.2 NP-dificuldade

Usa-se uma reducao polinomial de **PARTITION**. Dada uma colecao de inteiros positivos `a_1, ..., a_n` cuja soma e `2B`, constroi-se uma instancia de escalonamento com duas maquinas, uma tarefa de duracao `p_i = a_i` para cada inteiro, nenhuma precedencia e prazo `D = B`.

Se PARTITION possui dois subconjuntos de soma `B`, basta atribuir um subconjunto a cada maquina; ambas terminam no instante `B`. Reciprocamente, se existe uma escala com prazo `B`, as duas maquinas juntas executam trabalho total `2B` em capacidade total exatamente `2B`. Portanto, cada maquina recebe tarefas cuja soma e `B`, induzindo uma particao. A transformacao cria `n` tarefas e e polinomial.

O caso sem precedencias e um caso particular de `P|prec|C_max`. Assim, a versao de decisao e NP-dificil. Como tambem pertence a NP, e NP-completa. A literatura classica apresenta resultados ainda mais fortes para escalonamento com processadores paralelos e precedencias (ULLMAN, 1975; LENSTRA; RINNOOY KAN, 1978).

## 3. Implementacao

O programa foi escrito em Python 3, sem dependencias externas. A entrada JSON informa nome, numero de maquinas, prazo e tarefas. Antes da solucao, o programa valida identificadores, duracoes, predecessoras e a aciclicidade do grafo. Toda escala produzida passa por um verificador independente.

### 3.1 Forca bruta

A forca bruta enumera todas as ordens topologicas possiveis e, para cada ordem, todas as atribuicoes das tarefas as `m` maquinas. Cada tarefa e colocada no primeiro instante permitido pela maquina e pelas predecessoras. O melhor *makespan* e mantido. Esse metodo e completo, mas serve apenas para instancias pequenas.

### 3.2 Backtracking com branch-and-bound

O backtracking percorre o mesmo espaco de busca, mas corta ramos cujo *makespan* parcial ja nao melhora a melhor solucao conhecida. A primeira solucao incumbente vem do algoritmo guloso. Maquinas com o mesmo instante de disponibilidade sao simetricas, portanto somente uma delas e explorada. Tambem se usa o limite inferior `max(ceil(sum p_j / m), caminho_critico)`.

### 3.3 Divisao e conquista

Uma decomposicao exata generica nao e natural: uma aresta de precedencia pode atravessar a particao e todas as partes competem pelas mesmas maquinas. A implementacao, portanto, usa divisao e conquista como heuristica: ordena o DAG por prioridade de caminho critico, divide recursivamente a lista, atribui prioridades aos blocos e combina o resultado por *list scheduling*. O metodo e rapido, mas nao possui garantia de otimalidade. Essa limitacao deve ser discutida, em vez de afirmar incorretamente que os subproblemas sao independentes.

### 3.4 Programacao dinamica

A programacao dinamica e orientada a eventos. Um estado registra o conjunto de tarefas concluidas e as tarefas em execucao, com tempo restante e maquina. Em cada evento sao iniciadas combinacoes de tarefas prontas nas maquinas livres; o relogio avanca ate a proxima conclusao. Estados repetidos sao memorizados. O metodo e exato, mas o numero de subconjuntos e configuracoes cresce exponencialmente.

### 3.5 Algoritmo guloso

O *list scheduling* mantem as tarefas prontas e, sempre que uma maquina fica livre, escolhe a tarefa com maior caminho critico remanescente. A implementacao e polinomial. Para o problema em maquinas identicas com precedencias, o *list scheduling* classico possui limite de aproximacao `2 - 1/m` para o *makespan* (GRAHAM, 1966).

### 3.6 Heuristica GRASP

O GRASP repete construcoes gulosas aleatorizadas. Em cada decisao, escolhe uma tarefa dentro de uma lista restrita formada pelas melhores prioridades de caminho critico. A melhor escala entre 200 iteracoes e devolvida. A semente fixa torna o experimento reproduzivel.

## 4. Analise de complexidade

Sejam `n` o numero de tarefas, `m` o numero de maquinas, `E` o conjunto de precedencias e `D` o prazo.

| Estrategia | Tempo (pior caso) | Espaco | Exata? |
|---|---:|---:|:---:|
| Forca bruta | `O(n! * m^n * (n+|E|))` | `O(n+m)` | Sim |
| Backtracking | exponencial; mesmo limite da forca bruta | `O(n+m)` | Sim |
| Divisao e conquista heuristica | `O(n log n + |E|)` | `O(n+|E|)` | Nao |
| DP por eventos | exponencial no numero de estados | exponencial | Sim |
| Guloso | `O(n^2 + |E|)` nesta implementacao | `O(n+|E|)` | Nao |
| GRASP | `I * O(n^2 + |E|)`, com `I=200` | `O(n+|E|)` | Nao |

A contagem de instrucoes foi instrumentada nas operacoes dominantes: estados visitados, ramos explorados, comparacoes e podas. Ela nao representa instrucoes de maquina, mas permite comparar o crescimento dos algoritmos sob a mesma implementacao.

## 5. Analise de resultados

Os experimentos usam tres instancias pseudoaleatorias para cada tamanho `n = 6, 8, 10, 12`, sempre com tres maquinas. Duracoes variam de 1 a 6 e as precedencias formam um DAG. A semente e fixa. Forca bruta e executada somente com seis tarefas: uma tentativa com oito tarefas e tres maquinas ultrapassou um minuto, comportamento coerente com o limite `n! * m^n`.

Os testes foram executados em Windows 11 Pro, processador AMD Ryzen 7 5700U e 23,4 GB de memoria, usando Python 3.14.10. A tabela apresenta medias sobre 12 instancias por metodo, exceto a forca bruta, medida nas tres instancias de seis tarefas. Os tempos sao de uma unica execucao por instancia e, portanto, devem ser lidos como indicativos.

| Algoritmo | Execucoes | Tempo medio (ms) | Tempo maximo (ms) | *Makespan* medio | Instrucoes medias |
|---|---:|---:|---:|---:|---:|
| Guloso por caminho critico | 12 | 0,166 | 0,398 | 11,58 | 87 |
| Divisao e conquista heuristica | 12 | 0,220 | 0,396 | 11,50 | 112 |
| GRASP | 12 | 33,172 | 52,728 | 11,42 | 17.951 |
| Backtracking com B&B | 12 | 69,533 | 448,944 | 11,42 | 45.505 |
| Programacao dinamica | 12 | 128,784 | 522,347 | 11,42 | 29.948 |
| Forca bruta (`n=6`) | 3 | 880,024 | 988,243 | 9,00 | 887.983 |

Os metodos exatos concordaram em todas as instancias em que foram comparados. Usando a programacao dinamica como referencia, o guloso encontrou o otimo em 10 de 12 casos, com desvio medio de 1,53% e maximo de 10%. A divisao e conquista encontrou o otimo em 11 de 12, com desvio medio de 0,83% e maximo de 10%. O GRASP encontrou o otimo nas 12 instancias, embora isso seja um resultado empirico desta amostra e nao uma garantia teorica.

A forca bruta foi, em media, mais de cinco mil vezes mais lenta que o guloso mesmo sendo medida apenas nas menores instancias. O branch-and-bound foi muito rapido quando a solucao gulosa coincidiu com o limite inferior, pois a otimalidade ficou provada imediatamente; em instancias menos favoraveis chegou a 448,944 ms. A programacao dinamica atingiu 522,347 ms no pior caso e consumiu mais estados conforme aumentou `n`. Medidas abaixo de um milissegundo sofrem ruido do sistema, por isso a contagem instrumentada e importante para complementar o tempo.

Os resultados confirmaram as seguintes tendencias:

- os tres metodos exatos concordaram no *makespan*;
- branch-and-bound visitou menos ramos que a forca bruta;
- a DP trocou tempo por memoria e perdeu escalabilidade conforme aumentaram os estados;
- guloso e divisao e conquista foram muito rapidos, mas perderam qualidade em pelo menos um caso;
- GRASP igualou ou melhorou a solucao gulosa, ao custo de 200 construcoes.

## 6. Aplicacoes praticas

O mesmo modelo representa tarefas de um projeto distribuido entre equipes, *jobs* de computacao em processadores, operacoes de producao em maquinas equivalentes e lotes em servidores de nuvem. As precedencias modelam dependencias tecnicas; as maquinas representam recursos equivalentes; e o prazo global representa um acordo de entrega. Na pratica, tambem podem existir custos de troca, maquinas diferentes, datas de liberacao, prioridades e multiplos recursos. Essas extensoes tornam o modelo mais realista e, em geral, ainda mais dificil.

Uma aplicacao direta e o planejamento de uma compilacao paralela: um modulo so pode ser compilado depois de suas dependencias, cada nucleo executa uma compilacao por vez, e deseja-se terminar o projeto antes de um limite. Outra aplicacao e a execucao de um fluxo de dados em nuvem, no qual extracao, limpeza, treinamento e avaliacao possuem dependencias e competem por *workers*.

## 7. Conclusao

O trabalho mostra por que uma formulacao precisa e indispensavel na analise de algoritmos. A versao com maquinas paralelas, precedencias e prazo pertence a NP e e NP-completa por conter PARTITION como caso particular. Metodos exatos encontram o otimo, mas apresentam crescimento exponencial. O algoritmo guloso e as heuristicas escalam melhor e produzem solucoes validas rapidamente, embora possam nao ser otimas. A comparacao experimental deve evidenciar o compromisso entre qualidade, tempo e memoria.

As principais dificuldades foram representar corretamente execucoes paralelas, garantir as precedencias, evitar sobreposicoes e comparar paradigmas que nao se ajustam igualmente bem ao problema. O verificador independente e os testes automatizados reduziram o risco de aceitar escalas invalidas.

## 8. Referencias

CORMEN, T. H.; LEISERSON, C. E.; RIVEST, R. L.; STEIN, C. *Introduction to Algorithms*. 3. ed. Cambridge: MIT Press, 2009.

GRAHAM, R. L. Bounds for certain multiprocessing anomalies. *Bell System Technical Journal*, v. 45, n. 9, p. 1563-1581, 1966. DOI: 10.1002/j.1538-7305.1966.tb01709.x.

LENSTRA, J. K.; RINNOOY KAN, A. H. G. Complexity of scheduling under precedence constraints. *Operations Research*, v. 26, n. 1, p. 22-35, 1978. DOI: 10.1287/opre.26.1.22.

ULLMAN, J. D. NP-complete scheduling problems. *Journal of Computer and System Sciences*, v. 10, n. 3, p. 384-393, 1975. DOI: 10.1016/S0022-0000(75)80008-0.

ZIVIANI, N. *Projeto de algoritmos com implementacoes em Java e C++*. Sao Paulo: Cengage Learning, 2006.

## Apendice A - Codigo-fonte

Na versao final em PDF, inserir o conteudo integral de `src/scheduler.py`, conforme exigido pelo enunciado. Usar fonte monoespacada entre 8 e 9 pontos e quebra de linhas; nao utilizar capturas de tela do codigo.
