<!-- Arquivo gerado por scripts/montar_relatorio.py. Edite docs/RELATORIO.md e execute o script novamente. -->

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
No paradigma classico, a etapa de combinacao deve reconstruir uma solucao do
problema original a partir dos subproblemas (CORMEN et al., 2009); neste modelo,
as dependencias cruzadas e a competicao pelas maquinas impedem que essa
combinacao preserve automaticamente a otimalidade.

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

## Apêndice A — Núcleo dos algoritmos

Arquivo: `src/scheduler.py`.

```python
"""Algoritmos para P|prec|Cmax, com metricas e validacao de escalas."""

from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable


@dataclass(frozen=True)
class Task:
    """Tarefa indivisivel, com duracao e predecessoras obrigatorias."""

    id: str
    duration: int
    predecessors: tuple[str, ...] = ()


@dataclass(frozen=True)
class Instance:
    """Instancia completa da versao de decisao de P|prec|Cmax."""

    name: str
    machines: int
    deadline: int
    tasks: tuple[Task, ...]


@dataclass(frozen=True)
class Slot:
    """Intervalo ocupado por uma tarefa em uma maquina da solucao."""

    task: str
    machine: int
    start: int
    finish: int


@dataclass
class Metrics:
    """Metricas comparaveis coletadas durante a execucao de um algoritmo."""

    states: int = 0
    branches: int = 0
    comparisons: int = 0
    prunes: int = 0
    elapsed_ms: float = 0.0

    @property
    def instructions(self) -> int:
        """Contagem didatica das operacoes dominantes instrumentadas."""
        return self.states + self.branches + self.comparisons + self.prunes


@dataclass
class Result:
    """Escala produzida, acompanhada de metricas e garantia de exatidao."""

    algorithm: str
    schedule: list[Slot]
    metrics: Metrics = field(default_factory=Metrics)
    exact: bool = False

    @property
    def makespan(self) -> int:
        return max((slot.finish for slot in self.schedule), default=0)


def load_instance(path: str | Path) -> Instance:
    """Carrega uma instancia JSON e rejeita entradas estruturalmente invalidas."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    instance = Instance(
        name=str(data.get("nome", Path(path).stem)),
        machines=int(data["maquinas"]),
        deadline=int(data["prazo"]),
        tasks=tuple(
            Task(
                id=str(item["id"]),
                duration=int(item["duracao"]),
                predecessors=tuple(map(str, item.get("predecessoras", []))),
            )
            for item in data["tarefas"]
        ),
    )
    validate_instance(instance)
    return instance


def validate_instance(instance: Instance) -> None:
    """Valida parametros, referencias e aciclicidade do grafo de precedencias."""

    if instance.machines < 1 or instance.deadline < 0:
        raise ValueError("Maquinas deve ser positivo e prazo nao pode ser negativo")
    ids = [task.id for task in instance.tasks]
    if len(ids) != len(set(ids)):
        raise ValueError("Os identificadores das tarefas devem ser unicos")
    known = set(ids)
    for task in instance.tasks:
        if task.duration <= 0:
            raise ValueError(f"Duracao invalida em {task.id}")
        unknown = set(task.predecessors) - known
        if unknown:
            raise ValueError(f"Predecessoras inexistentes em {task.id}: {unknown}")
        if task.id in task.predecessors:
            raise ValueError(f"Autodependencia em {task.id}")
    topological_order(instance)  # tambem detecta ciclo


def topological_order(instance: Instance, priority: dict[str, float] | None = None) -> list[str]:
    """Executa Kahn, usando prioridade apenas como criterio de desempate."""

    successors = {task.id: [] for task in instance.tasks}
    indegree = {task.id: len(task.predecessors) for task in instance.tasks}
    for task in instance.tasks:
        for predecessor in task.predecessors:
            successors[predecessor].append(task.id)
    ready = [task_id for task_id, degree in indegree.items() if degree == 0]
    order: list[str] = []
    while ready:
        ready.sort(key=lambda task_id: (-(priority or {}).get(task_id, 0), task_id))
        current = ready.pop(0)
        order.append(current)
        for successor in successors[current]:
            indegree[successor] -= 1
            if indegree[successor] == 0:
                ready.append(successor)
    if len(order) != len(instance.tasks):
        raise ValueError("O grafo de precedencias contem ciclo")
    return order


def graph_data(instance: Instance):
    """Constroi indices de tarefas e listas de sucessores reutilizaveis."""

    task_by_id = {task.id: task for task in instance.tasks}
    successors = {task.id: [] for task in instance.tasks}
    for task in instance.tasks:
        for predecessor in task.predecessors:
            successors[predecessor].append(task.id)
    return task_by_id, successors


def critical_path_priorities(instance: Instance) -> dict[str, int]:
    """Calcula o maior trabalho restante de cada tarefa ate uma folha do DAG."""

    task_by_id, successors = graph_data(instance)
    memo: dict[str, int] = {}

    def remaining(task_id: str) -> int:
        if task_id not in memo:
            tail = max((remaining(child) for child in successors[task_id]), default=0)
            memo[task_id] = task_by_id[task_id].duration + tail
        return memo[task_id]

    return {task.id: remaining(task.id) for task in instance.tasks}


def lower_bound(instance: Instance) -> int:
    """Combina limites por carga media e por caminho critico."""

    priorities = critical_path_priorities(instance)
    work = sum(task.duration for task in instance.tasks)
    return max(math.ceil(work / instance.machines), max(priorities.values(), default=0))


def validate_schedule(instance: Instance, schedule: Iterable[Slot]) -> tuple[bool, list[str]]:
    """Verifica uma escala sem confiar no algoritmo que a produziu."""

    slots = list(schedule)
    errors: list[str] = []
    by_task = {slot.task: slot for slot in slots}
    task_by_id, _ = graph_data(instance)
    if set(by_task) != set(task_by_id) or len(slots) != len(task_by_id):
        errors.append("Cada tarefa deve aparecer exatamente uma vez")
    for slot in slots:
        task = task_by_id.get(slot.task)
        if task is None:
            errors.append(f"Tarefa desconhecida: {slot.task}")
            continue
        if not 0 <= slot.machine < instance.machines:
            errors.append(f"Maquina invalida em {slot.task}")
        if slot.start < 0 or slot.finish - slot.start != task.duration:
            errors.append(f"Intervalo invalido em {slot.task}")
        for predecessor in task.predecessors:
            if predecessor in by_task and by_task[predecessor].finish > slot.start:
                errors.append(f"Precedencia violada: {predecessor} -> {slot.task}")
    for machine in range(instance.machines):
        intervals = sorted((slot for slot in slots if slot.machine == machine), key=lambda x: x.start)
        for left, right in zip(intervals, intervals[1:]):
            if left.finish > right.start:
                errors.append(f"Sobreposicao na maquina {machine}: {left.task}/{right.task}")
    return not errors, errors


def _serial_schedule(instance: Instance, order: list[str], assignments: list[int]) -> list[Slot]:
    """Decodifica ordem e maquinas nos primeiros inicios viaveis."""

    task_by_id, _ = graph_data(instance)
    machine_available = [0] * instance.machines
    finish: dict[str, int] = {}
    schedule: list[Slot] = []
    for task_id, machine in zip(order, assignments):
        task = task_by_id[task_id]
        predecessor_finish = max((finish[p] for p in task.predecessors), default=0)
        start = max(machine_available[machine], predecessor_finish)
        end = start + task.duration
        schedule.append(Slot(task_id, machine, start, end))
        machine_available[machine] = end
        finish[task_id] = end
    return schedule


def list_schedule(
    instance: Instance,
    priority: dict[str, float] | None = None,
    choose: Callable[[list[str]], str] | None = None,
    algorithm: str = "guloso_caminho_critico",
) -> Result:
    """Constroi uma escala orientada a eventos a partir de uma prioridade."""

    metrics = Metrics()
    started = time.perf_counter()
    task_by_id, _ = graph_data(instance)
    priority = priority or critical_path_priorities(instance)
    completed: set[str] = set()
    running: list[tuple[int, int, str]] = []  # fim, maquina, tarefa
    free_machines = list(range(instance.machines))
    scheduled: set[str] = set()
    slots: list[Slot] = []
    now = 0
    while len(completed) < len(instance.tasks):
        metrics.states += 1
        newly_finished = [item for item in running if item[0] == now]
        for finish, machine, task_id in newly_finished:
            completed.add(task_id)
            free_machines.append(machine)
            running.remove((finish, machine, task_id))
        ready = [
            task.id
            for task in instance.tasks
            if task.id not in scheduled and set(task.predecessors) <= completed
        ]
        metrics.comparisons += len(instance.tasks)
        while free_machines and ready:
            if choose:
                task_id = choose(ready)
            else:
                task_id = max(ready, key=lambda item: (priority[item], task_by_id[item].duration, item))
            machine = min(free_machines)
            free_machines.remove(machine)
            ready.remove(task_id)
            task = task_by_id[task_id]
            finish = now + task.duration
            running.append((finish, machine, task_id))
            scheduled.add(task_id)
            slots.append(Slot(task_id, machine, now, finish))
            metrics.branches += 1
        if running:
            now = min(item[0] for item in running)
        elif len(completed) < len(instance.tasks):
            raise ValueError("Nao ha tarefa pronta; o grafo possui ciclo")
    metrics.elapsed_ms = (time.perf_counter() - started) * 1000
    return Result(algorithm, slots, metrics, exact=False)


def greedy(instance: Instance) -> Result:
    """Aplica list scheduling com prioridade de caminho critico remanescente."""

    return list_schedule(instance)


def divide_and_conquer(instance: Instance) -> Result:
    """Heuristica D&C: cria prioridades por particionamento recursivo do DAG."""
    started = time.perf_counter()
    metrics = Metrics()
    base = topological_order(instance, critical_path_priorities(instance))

    def recursive_rank(items: list[str], offset: int, rank: dict[str, int]) -> None:
        metrics.states += 1
        if len(items) <= 1:
            if items:
                rank[items[0]] = offset
            return
        middle = len(items) // 2
        recursive_rank(items[:middle], offset + len(items) - middle, rank)
        recursive_rank(items[middle:], offset, rank)
        metrics.branches += 1

    rank: dict[str, int] = {}
    recursive_rank(base, 0, rank)
    result = list_schedule(instance, priority=rank, algorithm="divisao_conquista_heuristica")
    result.metrics.states += metrics.states
    result.metrics.branches += metrics.branches
    result.metrics.elapsed_ms = (time.perf_counter() - started) * 1000
    return result


def grasp(instance: Instance, iterations: int = 200, seed: int = 42, alpha: float = 0.35) -> Result:
    """Repete construcoes gulosas aleatorizadas e preserva a melhor escala."""

    started = time.perf_counter()
    rng = random.Random(seed)
    critical = critical_path_priorities(instance)
    best: Result | None = None
    aggregate = Metrics()
    for _ in range(iterations):
        def randomized_choice(ready: list[str]) -> str:
            ordered = sorted(ready, key=lambda item: critical[item], reverse=True)
            width = max(1, math.ceil(len(ordered) * alpha))
            return rng.choice(ordered[:width])

        candidate = list_schedule(instance, choose=randomized_choice, algorithm="grasp")
        aggregate.states += candidate.metrics.states
        aggregate.branches += candidate.metrics.branches
        aggregate.comparisons += candidate.metrics.comparisons
        aggregate.comparisons += 1
        if best is None or candidate.makespan < best.makespan:
            best = candidate
    assert best is not None
    aggregate.elapsed_ms = (time.perf_counter() - started) * 1000
    best.metrics = aggregate
    best.algorithm = "grasp"
    return best


def brute_force(instance: Instance, max_tasks: int = 10) -> Result:
    """Enumera ordens topologicas e atribuicoes de maquinas sem podas."""

    if len(instance.tasks) > max_tasks:
        raise ValueError(f"Forca bruta limitada a {max_tasks} tarefas")
    started = time.perf_counter()
    metrics = Metrics()
    task_by_id, _ = graph_data(instance)
    best_schedule: list[Slot] | None = None
    best_makespan = math.inf

    def visit(order: list[str], assignments: list[int], finish: dict[str, int], machine_available: list[int]) -> None:
        nonlocal best_schedule, best_makespan
        metrics.states += 1
        if len(order) == len(instance.tasks):
            makespan = max(machine_available, default=0)
            metrics.comparisons += 1
            if makespan < best_makespan:
                best_makespan = makespan
                best_schedule = _serial_schedule(instance, order, assignments)
            return
        placed = set(order)
        ready = [task for task in instance.tasks if task.id not in placed and set(task.predecessors) <= placed]
        for task in ready:
            predecessor_finish = max((finish[p] for p in task.predecessors), default=0)
            for machine in range(instance.machines):
                metrics.branches += 1
                start = max(machine_available[machine], predecessor_finish)
                end = start + task.duration
                old_available = machine_available[machine]
                machine_available[machine] = end
                finish[task.id] = end
                visit(order + [task.id], assignments + [machine], finish, machine_available)
                machine_available[machine] = old_available
                del finish[task.id]

    visit([], [], {}, [0] * instance.machines)
    metrics.elapsed_ms = (time.perf_counter() - started) * 1000
    return Result("forca_bruta", best_schedule or [], metrics, exact=True)


def backtracking(instance: Instance, max_tasks: int = 14) -> Result:
    """Busca exata com branch-and-bound, incumbente e quebra de simetria."""

    if len(instance.tasks) > max_tasks:
        raise ValueError(f"Backtracking limitado a {max_tasks} tarefas")
    started = time.perf_counter()
    metrics = Metrics()
    task_by_id, _ = graph_data(instance)
    priority = critical_path_priorities(instance)
    incumbent = greedy(instance)
    best_schedule = incumbent.schedule
    best_makespan = incumbent.makespan
    static_lower_bound = lower_bound(instance)

    def visit(order: list[str], assignments: list[int], finish: dict[str, int], machine_available: list[int]) -> None:
        nonlocal best_schedule, best_makespan
        metrics.states += 1
        current = max(machine_available, default=0)
        metrics.comparisons += 1
        if current >= best_makespan:
            metrics.prunes += 1
            return
        if len(order) == len(instance.tasks):
            best_makespan = current
            best_schedule = _serial_schedule(instance, order, assignments)
            return
        if best_makespan == static_lower_bound:
            metrics.prunes += 1
            return
        placed = set(order)
        ready = [task for task in instance.tasks if task.id not in placed and set(task.predecessors) <= placed]
        ready.sort(key=lambda task: (priority[task.id], task.duration), reverse=True)
        for task in ready:
            predecessor_finish = max((finish[p] for p in task.predecessors), default=0)
            seen_machine_times: set[int] = set()
            for machine in range(instance.machines):
                if machine_available[machine] in seen_machine_times:
                    metrics.prunes += 1
                    continue
                seen_machine_times.add(machine_available[machine])
                metrics.branches += 1
                start = max(machine_available[machine], predecessor_finish)
                end = start + task.duration
                if end >= best_makespan and len(order) + 1 < len(instance.tasks):
                    metrics.prunes += 1
                    continue
                old_available = machine_available[machine]
                machine_available[machine] = end
                finish[task.id] = end
                visit(order + [task.id], assignments + [machine], finish, machine_available)
                machine_available[machine] = old_available
                del finish[task.id]

    visit([], [], {}, [0] * instance.machines)
    metrics.elapsed_ms = (time.perf_counter() - started) * 1000
    return Result("backtracking_branch_bound", best_schedule, metrics, exact=True)


def dynamic_programming(instance: Instance, max_tasks: int = 18) -> Result:
    """DP exata por eventos; estado = concluidas + tarefas em execucao."""
    if len(instance.tasks) > max_tasks:
        raise ValueError(f"Programacao dinamica limitada a {max_tasks} tarefas")
    started = time.perf_counter()
    metrics = Metrics()
    tasks = instance.tasks
    index = {task.id: i for i, task in enumerate(tasks)}
    predecessor_masks = []
    for task in tasks:
        mask = 0
        for predecessor in task.predecessors:
            mask |= 1 << index[predecessor]
        predecessor_masks.append(mask)
    full_mask = (1 << len(tasks)) - 1
    memo: dict[tuple[int, tuple[tuple[int, int, int], ...]], int] = {}
    policy: dict[tuple[int, tuple[tuple[int, int, int], ...]], tuple[int, ...]] = {}

    def solve(completed: int, running: tuple[tuple[int, int, int], ...]) -> int:
        state = (completed, running)
        if state in memo:
            return memo[state]
        metrics.states += 1
        if completed == full_mask and not running:
            memo[state] = 0
            return 0
        running_ids = {item[0] for item in running}
        free_machines = sorted(set(range(instance.machines)) - {item[2] for item in running})
        ready = [
            i
            for i in range(len(tasks))
            if not completed & (1 << i)
            and i not in running_ids
            and predecessor_masks[i] & completed == predecessor_masks[i]
        ]
        take = min(len(free_machines), len(ready))
        choices = itertools.combinations(ready, take) if take else [()]
        best = math.inf
        best_choice: tuple[int, ...] = ()
        for choice in choices:
            metrics.branches += 1
            augmented = list(running)
            for task_index, machine in zip(choice, free_machines):
                augmented.append((task_index, tasks[task_index].duration, machine))
            if not augmented:
                continue
            delta = min(item[1] for item in augmented)
            next_completed = completed
            next_running = []
            for task_index, remaining, machine in augmented:
                if remaining == delta:
                    next_completed |= 1 << task_index
                else:
                    next_running.append((task_index, remaining - delta, machine))
            next_state = tuple(sorted(next_running))
            value = delta + solve(next_completed, next_state)
            metrics.comparisons += 1
            if value < best:
                best = value
                best_choice = tuple(choice)
        memo[state] = best
        policy[state] = best_choice
        return best

    solve(0, ())
    completed = 0
    running: tuple[tuple[int, int, int], ...] = ()
    now = 0
    starts: dict[int, tuple[int, int]] = {}
    slots: list[Slot] = []
    while completed != full_mask or running:
        state = (completed, running)
        choice = policy.get(state, ())
        free_machines = sorted(set(range(instance.machines)) - {item[2] for item in running})
        augmented = list(running)
        for task_index, machine in zip(choice, free_machines):
            starts[task_index] = (machine, now)
            augmented.append((task_index, tasks[task_index].duration, machine))
        delta = min(item[1] for item in augmented)
        now += delta
        next_running = []
        for task_index, remaining, machine in augmented:
            if remaining == delta:
                completed |= 1 << task_index
                assigned_machine, start_time = starts.pop(task_index)
                slots.append(Slot(tasks[task_index].id, assigned_machine, start_time, now))
            else:
                next_running.append((task_index, remaining - delta, machine))
        running = tuple(sorted(next_running))
    metrics.elapsed_ms = (time.perf_counter() - started) * 1000
    return Result("programacao_dinamica_eventos", slots, metrics, exact=True)


ALGORITHMS = {
    "forca-bruta": brute_force,
    "backtracking": backtracking,
    "divisao-conquista": divide_and_conquer,
    "programacao-dinamica": dynamic_programming,
    "guloso": greedy,
    "grasp": grasp,
}


def format_result(instance: Instance, result: Result) -> str:
    """Formata uma solucao da CLI e inclui o resultado do verificador."""

    valid, errors = validate_schedule(instance, result.schedule)
    status = "SIM" if result.makespan <= instance.deadline else "NAO"
    lines = [
        f"Algoritmo: {result.algorithm}",
        f"Makespan: {result.makespan} | Prazo: {instance.deadline} | Viavel: {status}",
        f"Escala valida: {'SIM' if valid else 'NAO'}",
        f"Tempo: {result.metrics.elapsed_ms:.3f} ms | Instrucoes: {result.metrics.instructions}",
    ]
    if errors:
        lines.extend(f"ERRO: {error}" for error in errors)
    for slot in sorted(result.schedule, key=lambda item: (item.start, item.machine)):
        lines.append(f"  {slot.task}: M{slot.machine + 1} [{slot.start}, {slot.finish})")
    return "\n".join(lines)


def main() -> None:
    """Processa a linha de comando e executa um ou todos os algoritmos."""

    parser = argparse.ArgumentParser(description="Escalonamento P|prec|Cmax")
    parser.add_argument("instancia", type=Path)
    parser.add_argument("--algoritmo", choices=[*ALGORITHMS, "todos"], default="todos")
    args = parser.parse_args()
    instance = load_instance(args.instancia)
    selected = ALGORITHMS.items() if args.algoritmo == "todos" else [(args.algoritmo, ALGORITHMS[args.algoritmo])]
    print(f"Instancia: {instance.name} | Limite inferior: {lower_bound(instance)}")
    for _, algorithm in selected:
        result = algorithm(instance)
        print("\n" + format_result(instance, result))


if __name__ == "__main__":
    main()
```

## Apêndice B — Automação dos experimentos

Arquivo: `scripts/run_benchmarks.py`.

```python
"""Executa experimentos deterministas e grava resultados/benchmark.csv."""

from __future__ import annotations

import csv
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scheduler import (  # noqa: E402
    Instance,
    Task,
    backtracking,
    brute_force,
    divide_and_conquer,
    dynamic_programming,
    grasp,
    greedy,
    validate_schedule,
)


def generated_instance(size: int, seed: int) -> Instance:
    rng = random.Random(seed)
    tasks = []
    for i in range(size):
        predecessors = tuple(
            f"T{j + 1}"
            for j in range(i)
            if rng.random() < 0.18 and i - j <= 5
        )
        tasks.append(Task(f"T{i + 1}", rng.randint(1, 6), predecessors))
    return Instance(f"n{size}_s{seed}", 3, 10**9, tuple(tasks))


def main() -> None:
    algorithms = [greedy, divide_and_conquer, grasp, dynamic_programming, backtracking]
    rows = []
    for size in (6, 8, 10, 12):
        for seed in (11, 22, 33):
            instance = generated_instance(size, seed)
            selected = list(algorithms)
            # Com 3 maquinas, a forca bruta ja pode explorar n! * 3^n ramos.
            # Ela e medida apenas em n=6 para manter o experimento executavel.
            if size <= 6:
                selected.insert(0, brute_force)
            for algorithm in selected:
                result = algorithm(instance)
                valid, errors = validate_schedule(instance, result.schedule)
                if not valid:
                    raise RuntimeError(f"Escala invalida em {instance.name}: {errors}")
                rows.append({
                    "instancia": instance.name,
                    "n": size,
                    "maquinas": instance.machines,
                    "algoritmo": result.algorithm,
                    "exato": result.exact,
                    "makespan": result.makespan,
                    "tempo_ms": f"{result.metrics.elapsed_ms:.6f}",
                    "instrucoes": result.metrics.instructions,
                    "estados": result.metrics.states,
                    "ramos": result.metrics.branches,
                    "podas": result.metrics.prunes,
                })
    output = ROOT / "resultados" / "benchmark.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} resultados gravados em {output}")


if __name__ == "__main__":
    main()
```
