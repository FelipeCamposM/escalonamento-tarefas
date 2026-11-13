# Implementação e Análise de Estratégias de Algoritmos para Escalonamento de Tarefas

**Instituição:** Universidade Federal de Goiás (UFG)<br>
**Disciplina:** Análise e Projeto de Algoritmos<br>
**Professor:** André Luiz Moura<br>
**Integrantes (ordem alfabética):** Felipe Campos Macedo - 202501133; Gabriel Guimarães Naves - 202503292

## Resumo

Este trabalho investiga o problema de escalonamento de tarefas em máquinas paralelas idênticas, com restrições de precedência, execução não preemptiva e prazo global. A formulação estudada corresponde a `P|prec|Cmax`. São implementadas e comparadas seis estratégias: força bruta, backtracking com branch-and-bound, divisão e conquista heurística, programação dinâmica orientada a eventos, escalonamento guloso e GRASP. A versão de decisão é demonstrada como pertencente a NP e NP-completa por redução de PARTITION. Os métodos são avaliados por tempo de execução, operações dominantes instrumentadas, qualidade da solução e validade da escala. Os resultados evidenciam o contraste entre a garantia de otimalidade dos métodos exatos e a escalabilidade dos métodos heurísticos.

**Palavras-chave:** escalonamento de tarefas; complexidade; NP-completude; máquinas paralelas; heurísticas.

## 1. Introdução

Escalonar tarefas significa decidir quando e em qual recurso cada atividade será executada. O problema aparece na alocação de processos em processadores, no planejamento de projetos, em linhas de produção, na computação em nuvem e na organização de equipes. Mesmo pequenas alterações no modelo podem mudar sua complexidade; por isso, este trabalho fixa formalmente a variante estudada.

São dadas `n` tarefas. Cada tarefa `j` possui duração inteira positiva `p_j`. Há `m >= 2` máquinas idênticas, cada uma capaz de executar no máximo uma tarefa por vez. Uma relação de precedência `i -> j` obriga a conclusão de `i` antes do início de `j`. As tarefas não podem ser interrompidas e cada tarefa usa exatamente uma máquina. Dado um prazo global `D`, a pergunta de decisão é: existe um escalonamento válido cujo tempo de conclusão da última tarefa (`C_max`, ou *makespan*) seja menor ou igual a `D`? Na notação clássica, a versão de otimização é `P|prec|C_max`.

Essa formulação evita uma ambiguidade do enunciado. Com apenas uma máquina, nenhuma data de liberação e um único prazo global, a ordem não altera a soma das durações: depois de verificar que o grafo é acíclico, bastaria testar `sum(p_j) <= D`. A existência de máquinas paralelas e a decisão de como distribuir tarefas entre elas tornam o problema combinatório.

## 2. Prova de que o problema pertence a NP

### 2.1 Pertinência a NP

Um certificado é uma lista com, para cada tarefa, a máquina escolhida e os tempos inteiros de início e fim. Um verificador confere em tempo polinomial:

1. se cada tarefa aparece exatamente uma vez;
2. se `fim_j - inicio_j = p_j` e os tempos são não negativos;
3. se intervalos na mesma máquina não se sobrepõem;
4. se, para toda precedência `i -> j`, vale `fim_i <= inicio_j`;
5. se o maior tempo de fim é no máximo `D`.

Ordenando os intervalos de cada máquina, a verificação custa `O(n log n + |E|)`, onde `E` é o conjunto de precedências. Logo, o problema pertence a NP.

### 2.2 NP-dificuldade

Usa-se uma redução polinomial de **PARTITION**. Dada uma coleção de inteiros positivos `a_1, ..., a_n` cuja soma é `2B`, constrói-se uma instância de escalonamento com duas máquinas, uma tarefa de duração `p_i = a_i` para cada inteiro, nenhuma precedência e prazo `D = B`.

Se PARTITION possui dois subconjuntos de soma `B`, basta atribuir um subconjunto a cada máquina; ambas terminam no instante `B`. Reciprocamente, se existe uma escala com prazo `B`, as duas máquinas juntas executam trabalho total `2B` em capacidade total exatamente `2B`. Portanto, cada máquina recebe tarefas cuja soma é `B`, induzindo uma partição. A transformação cria `n` tarefas e é polinomial.

O caso sem precedências é um caso particular de `P|prec|C_max`. Assim, a versão de decisão é NP-difícil. Como também pertence a NP, é NP-completa. A literatura clássica apresenta resultados ainda mais fortes para escalonamento com processadores paralelos e precedências (ULLMAN, 1975; LENSTRA; RINNOOY KAN, 1978).

## 3. Implementação

O programa foi escrito em Python 3, sem dependências externas. A entrada JSON informa nome, número de máquinas, prazo e tarefas. Antes da solução, o programa valida identificadores, durações, predecessoras e a aciclicidade do grafo. Toda escala produzida passa por um verificador independente. A aplicação web em JavaScript é um recurso complementar de visualização; os experimentos científicos utilizam o núcleo Python.

### 3.1 Força bruta

A força bruta enumera todas as ordens topológicas possíveis e, para cada ordem, todas as atribuições das tarefas às `m` máquinas. Cada tarefa é colocada no primeiro instante permitido pela máquina e pelas predecessoras. O melhor *makespan* é mantido. Esse método é completo, mas serve apenas para instâncias pequenas.

### 3.2 Backtracking com branch-and-bound

O backtracking percorre o mesmo espaço de busca, mas corta ramos cujo *makespan* parcial já não melhora a melhor solução conhecida. A primeira solução incumbente vem do algoritmo guloso. Máquinas com o mesmo instante de disponibilidade são simétricas, portanto somente uma delas é explorada. Também se usa o limite inferior `max(ceil(sum p_j / m), caminho_critico)`.

### 3.3 Divisão e conquista

Uma decomposição exata genérica não é natural: uma aresta de precedência pode atravessar a partição e todas as partes competem pelas mesmas máquinas. A implementação, portanto, usa divisão e conquista como heurística: ordena o DAG por prioridade de caminho crítico, divide recursivamente a lista, atribui prioridades aos blocos e combina o resultado por *list scheduling*. O método é rápido, mas não possui garantia de otimalidade.

No paradigma clássico, a etapa de combinação deve reconstruir uma solução do problema original a partir dos subproblemas (CORMEN et al., 2009); neste modelo, as dependências cruzadas e a competição pelas máquinas impedem que essa combinação preserve automaticamente a otimalidade. Essa limitação é apresentada explicitamente, em vez de afirmar incorretamente que os subproblemas são independentes.

### 3.4 Programação dinâmica

A programação dinâmica é orientada a eventos. Um estado registra o conjunto de tarefas concluídas e as tarefas em execução, com tempo restante e máquina. Em cada evento são iniciadas combinações de tarefas prontas nas máquinas livres; o relógio avança até a próxima conclusão. Estados repetidos são memorizados. O método é exato, mas o número de subconjuntos e configurações cresce exponencialmente.

### 3.5 Algoritmo guloso

O *list scheduling* mantém as tarefas prontas e, sempre que uma máquina fica livre, escolhe a tarefa com maior caminho crítico remanescente. A implementação é polinomial. Para o problema em máquinas idênticas com precedências, o *list scheduling* clássico possui limite de aproximação `2 - 1/m` para o *makespan* (GRAHAM, 1966).

### 3.6 Heurística GRASP

O GRASP repete construções gulosas aleatorizadas. Em cada decisão, escolhe uma tarefa dentro de uma lista restrita formada pelas melhores prioridades de caminho crítico. A melhor escala entre 200 iterações é devolvida. A semente fixa torna o experimento reproduzível.

## 4. Análise de complexidade

Sejam `n` o número de tarefas, `m` o número de máquinas, `E` o conjunto de precedências e `I` o número de iterações do GRASP.

| Estratégia | Tempo no pior caso | Espaço | Exata? |
|---|---:|---:|:---:|
| Força bruta | `O(n! * m^n * (n+|E|))` | `O(n+m)` | Sim |
| Backtracking | exponencial; mesmo limite da força bruta | `O(n+m)` | Sim |
| Divisão e conquista heurística | `O(n log n + |E|)` | `O(n+|E|)` | Não |
| DP por eventos | exponencial no número de estados | exponencial | Sim |
| Guloso | `O(n^2 + |E|)` nesta implementação | `O(n+|E|)` | Não |
| GRASP | `I * O(n^2 + |E|)`, com `I=200` | `O(n+|E|)` | Não |

A contagem de instruções foi instrumentada nas operações dominantes: estados visitados, ramos explorados, comparações e podas. Ela não representa instruções nativas do processador, mas permite comparar o crescimento dos algoritmos sob a mesma implementação.

## 5. Análise de resultados

Os experimentos usam três instâncias pseudoaleatórias para cada tamanho `n = 6, 8, 10, 12`, sempre com três máquinas. As durações variam de 1 a 6 e as precedências formam um DAG. A semente é fixa. A força bruta é executada somente com seis tarefas: uma tentativa com oito tarefas e três máquinas ultrapassou um minuto, comportamento coerente com o limite `n! * m^n`.

Os testes foram executados em Windows 11 Pro, processador AMD Ryzen 7 5700U e 23,4 GB de memória, usando Python 3.14.10. A tabela apresenta médias sobre 12 instâncias por método, exceto a força bruta, medida nas três instâncias de seis tarefas. Os tempos são de uma única execução por instância e, portanto, devem ser lidos como indicativos.

| Algoritmo | Execuções | Tempo médio (ms) | Tempo máximo (ms) | *Makespan* médio | Instruções médias |
|---|---:|---:|---:|---:|---:|
| Guloso por caminho crítico | 12 | 0,166 | 0,398 | 11,58 | 87 |
| Divisão e conquista heurística | 12 | 0,220 | 0,396 | 11,50 | 112 |
| GRASP | 12 | 33,172 | 52,728 | 11,42 | 17.951 |
| Backtracking com B&B | 12 | 69,533 | 448,944 | 11,42 | 45.505 |
| Programação dinâmica | 12 | 128,784 | 522,347 | 11,42 | 29.948 |
| Força bruta (`n=6`) | 3 | 880,024 | 988,243 | 9,00 | 887.983 |

Os métodos exatos concordaram em todas as instâncias em que foram comparados. Usando a programação dinâmica como referência, o guloso encontrou o ótimo em 10 de 12 casos, com desvio médio de 1,53% e máximo de 10%. A divisão e conquista encontrou o ótimo em 11 de 12, com desvio médio de 0,83% e máximo de 10%. O GRASP encontrou o ótimo nas 12 instâncias, embora isso seja um resultado empírico desta amostra e não uma garantia teórica.

A força bruta foi, em média, mais de cinco mil vezes mais lenta que o guloso mesmo sendo medida apenas nas menores instâncias. O branch-and-bound foi muito rápido quando a solução gulosa coincidiu com o limite inferior, pois a otimalidade ficou provada imediatamente; em instâncias menos favoráveis chegou a 448,944 ms. A programação dinâmica atingiu 522,347 ms no pior caso e consumiu mais estados conforme aumentou `n`. Medidas abaixo de um milissegundo sofrem ruído do sistema, por isso a contagem instrumentada é importante para complementar o tempo.

Os resultados confirmaram as seguintes tendências:

- os três métodos exatos concordaram no *makespan*;
- branch-and-bound visitou menos ramos que a força bruta;
- a programação dinâmica trocou tempo por memória e perdeu escalabilidade conforme aumentaram os estados;
- guloso e divisão e conquista foram muito rápidos, mas perderam qualidade em pelo menos um caso;
- GRASP igualou ou melhorou a solução gulosa, ao custo de 200 construções.

### 5.1 Limitações e ameaças à validade

A amostra experimental é deliberadamente pequena para permitir a comparação com métodos exatos. Os tempos dependem do hardware, do sistema operacional e de ruídos de execução; por isso, não devem ser generalizados como valores absolutos. A contagem instrumentada também é uma aproximação de operações dominantes, e não uma contagem de instruções de máquina. Por fim, o fato de o GRASP ter encontrado todos os ótimos da amostra não demonstra que o método sempre produzirá a solução ótima. As sementes, instâncias e dados brutos são preservados para permitir reprodução e extensão dos testes.

## 6. Aplicações práticas

O mesmo modelo representa tarefas de um projeto distribuído entre equipes, *jobs* de computação em processadores, operações de produção em máquinas equivalentes e lotes em servidores de nuvem. As precedências modelam dependências técnicas; as máquinas representam recursos equivalentes; e o prazo global representa um acordo de entrega. Na prática, também podem existir custos de troca, máquinas diferentes, datas de liberação, prioridades e múltiplos recursos. Essas extensões tornam o modelo mais realista e, em geral, ainda mais difícil.

Uma aplicação direta é o planejamento de uma compilação paralela: um módulo só pode ser compilado depois de suas dependências, cada núcleo executa uma compilação por vez e deseja-se terminar o projeto antes de um limite. Outra aplicação é a execução de um fluxo de dados em nuvem, no qual extração, limpeza, treinamento e avaliação possuem dependências e competem por *workers*.

## 7. Conclusão

O trabalho mostra por que uma formulação precisa é indispensável na análise de algoritmos. A versão com máquinas paralelas, precedências e prazo pertence a NP e é NP-completa por conter PARTITION como caso particular. Métodos exatos encontram o ótimo, mas apresentam crescimento exponencial. O algoritmo guloso e as heurísticas escalam melhor e produzem soluções válidas rapidamente, embora possam não ser ótimas. A comparação experimental evidencia o compromisso entre qualidade, tempo e memória.

As principais dificuldades foram representar corretamente execuções paralelas, garantir as precedências, evitar sobreposições e comparar paradigmas que não se ajustam igualmente bem ao problema. O verificador independente e os testes automatizados reduziram o risco de aceitar escalas inválidas. Como continuidade, o estudo pode incluir instâncias maiores, máquinas heterogêneas, datas de liberação, custos de troca e novos métodos meta-heurísticos.

## 8. Referências

CORMEN, T. H.; LEISERSON, C. E.; RIVEST, R. L.; STEIN, C. *Introduction to Algorithms*. 3. ed. Cambridge: MIT Press, 2009.

GRAHAM, R. L. Bounds for certain multiprocessing anomalies. *Bell System Technical Journal*, v. 45, n. 9, p. 1563-1581, 1966. DOI: 10.1002/j.1538-7305.1966.tb01709.x.

LENSTRA, J. K.; RINNOOY KAN, A. H. G. Complexity of scheduling under precedence constraints. *Operations Research*, v. 26, n. 1, p. 22-35, 1978. DOI: 10.1287/opre.26.1.22.

ULLMAN, J. D. NP-complete scheduling problems. *Journal of Computer and System Sciences*, v. 10, n. 3, p. 384-393, 1975. DOI: 10.1016/S0022-0000(75)80008-0.

ZIVIANI, N. *Projeto de algoritmos com implementações em Java e C++*. São Paulo: Cengage Learning, 2006.

## Apêndice A - Código-fonte

O arquivo `docs/RELATORIO_COM_CODIGO.md` incorpora automaticamente o conteúdo integral de `src/scheduler.py` e `scripts/run_benchmarks.py`, conforme exigido pelo enunciado. Ele deve ser regenerado com `python scripts/montar_relatorio.py` depois de qualquer alteração no texto ou no código. Na diagramação do PDF, o código é apresentado em páginas paisagem, com fonte monoespaçada e numeração de linhas; não são utilizadas capturas de tela do código.
