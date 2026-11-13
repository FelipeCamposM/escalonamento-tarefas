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
    id: str
    duration: int
    predecessors: tuple[str, ...] = ()


@dataclass(frozen=True)
class Instance:
    name: str
    machines: int
    deadline: int
    tasks: tuple[Task, ...]


@dataclass(frozen=True)
class Slot:
    task: str
    machine: int
    start: int
    finish: int


@dataclass
class Metrics:
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
    algorithm: str
    schedule: list[Slot]
    metrics: Metrics = field(default_factory=Metrics)
    exact: bool = False

    @property
    def makespan(self) -> int:
        return max((slot.finish for slot in self.schedule), default=0)


def load_instance(path: str | Path) -> Instance:
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
    task_by_id = {task.id: task for task in instance.tasks}
    successors = {task.id: [] for task in instance.tasks}
    for task in instance.tasks:
        for predecessor in task.predecessors:
            successors[predecessor].append(task.id)
    return task_by_id, successors


def critical_path_priorities(instance: Instance) -> dict[str, int]:
    task_by_id, successors = graph_data(instance)
    memo: dict[str, int] = {}

    def remaining(task_id: str) -> int:
        if task_id not in memo:
            tail = max((remaining(child) for child in successors[task_id]), default=0)
            memo[task_id] = task_by_id[task_id].duration + tail
        return memo[task_id]

    return {task.id: remaining(task.id) for task in instance.tasks}


def lower_bound(instance: Instance) -> int:
    priorities = critical_path_priorities(instance)
    work = sum(task.duration for task in instance.tasks)
    return max(math.ceil(work / instance.machines), max(priorities.values(), default=0))


def validate_schedule(instance: Instance, schedule: Iterable[Slot]) -> tuple[bool, list[str]]:
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

