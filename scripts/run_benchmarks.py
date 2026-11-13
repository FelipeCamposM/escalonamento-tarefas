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
