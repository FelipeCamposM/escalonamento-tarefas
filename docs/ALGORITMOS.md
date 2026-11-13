# Guia detalhado dos algoritmos

## Representacao comum

Cada tarefa possui identificador, duracao inteira positiva e predecessoras. Uma escala e uma lista `(tarefa, maquina, inicio, fim)`. O objetivo e minimizar o maior tempo de fim, o `makespan`.

## Forca bruta

Enumera toda tarefa pronta e toda maquina. A enumeracao gera ordens topologicas e aplica a geracao serial. E exata, mas custa `O(n! * m^n * (n + |E|))` no pior caso. Serve como oraculo para instancias pequenas.

## Backtracking com branch-and-bound

Percorre o mesmo espaco, usando incumbente gulosa, poda pelo makespan parcial, quebra de simetria entre maquinas igualmente disponiveis e limite inferior pelo trabalho/caminho critico. Continua exponencial, mas frequentemente prova o otimo com poucos ramos.

## Divisao e conquista

Precedencias cruzadas e maquinas compartilhadas impedem subproblemas independentes. A implementacao e, portanto, uma heuristica: ordena o DAG por caminho critico, particiona a ordem recursivamente e combina por list scheduling. E polinomial, sem garantia de otimalidade.

## Programacao dinamica por eventos

O estado guarda a mascara das tarefas concluidas e as tarefas em execucao. O relogio salta para a proxima conclusao. Estados repetidos sao calculados uma vez. E exata, mas exponencial em tempo e memoria.

## Guloso por caminho critico

Quando uma maquina fica livre, escolhe a tarefa pronta com maior caminho restante. E polinomial; o list scheduling classico possui limite `2 - 1/m` para este modelo. Na amostra, o desvio medio foi 1,53%.

## GRASP

Cria uma lista restrita das melhores tarefas prontas, escolhe aleatoriamente dentro dela e repete 200 vezes. A semente fixa garante reproducao. Encontrou todos os otimos da amostra, sem que isso seja garantia geral.

