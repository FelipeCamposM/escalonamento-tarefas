<!-- Arquivo gerado por scripts/montar_relatorio.py. Edite docs/RELATORIO.md e execute o script novamente. -->

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
