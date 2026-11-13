# ScheduleLab - Trabalho final de APA

Projeto completo sobre **Escalonamento de Tarefas (Job Scheduling)**. A
formulacao adotada e `P|prec|Cmax`: duracoes inteiras, precedencias, maquinas
paralelas identicas, execucao nao preemptiva e prazo global.

## Ver no navegador

Requer Node.js 20 ou superior:

```powershell
npm install
npm run dev
```

Acesse `http://127.0.0.1:5173`. Cada clique em **Gerar e executar** cria uma
instancia nova, executa o algoritmo selecionado no navegador e reconstrói
Gantt, grafo de precedencias, rastreio e metricas. A interface tambem apresenta
o benchmark controlado e a prova de NP-completude.

## Executar os algoritmos

Requer Python 3.10 ou superior e nao usa bibliotecas externas:

```powershell
python src/scheduler.py instances/exemplo.json --algoritmo todos
python scripts/run_benchmarks.py
python -m unittest discover -s tests -v
```

## Validar tudo

```powershell
npm run check
python -m unittest discover -s tests -v
```

## Estrutura

- `src/scheduler.py`: seis algoritmos, metricas e verificador.
- `instances/`: instancias JSON reproduziveis.
- `scripts/`: automacao do benchmark.
- `tests/`: testes do nucleo Python.
- `web/`: aplicacao visual servida pelo Vite.
- `web/scheduler-live.js`: implementacao de demonstracao executada ao vivo.
- `resultados/`: dados brutos em CSV.
- `docs/`: relatorio e documentacao tecnica.
- `prints/`: evidencias visuais da aplicacao executada.

## Documentacao

- [Relatorio academico](docs/RELATORIO.md)
- [Arquitetura](docs/ARQUITETURA.md)
- [Algoritmos](docs/ALGORITMOS.md)
- [Metodologia experimental](docs/METODOLOGIA_EXPERIMENTAL.md)
- [Manual de uso](docs/MANUAL_USUARIO.md)

## Algoritmos

1. Forca bruta por ordens topologicas e atribuicoes de maquinas.
2. Backtracking com branch-and-bound e quebra de simetria.
3. Divisao e conquista como heuristica de prioridade.
4. Programacao dinamica exata orientada a eventos.
5. List scheduling guloso por caminho critico.
6. GRASP aleatorizado com semente fixa.

Os metodos exatos sao apropriados para instancias pequenas. A divisao e
conquista e descrita honestamente como heuristica porque precedencias entre
particoes e maquinas compartilhadas impedem composicao independente de otimos.
