# Manual de execução

## Requisitos

- Node.js 20 ou superior, acompanhado do npm;
- navegador atualizado;
- Python 3.10 ou superior somente para executar o núcleo científico, os testes
  Python e os benchmarks.

O laboratório web não precisa de banco de dados, conta externa ou conexão com a
internet depois que as dependências forem instaladas.

## Visualização no navegador

1. Extrair o ZIP completo.
2. Abrir o PowerShell ou terminal na pasta `escalonamento_tarefas`.
3. Instalar as dependências:

```powershell
npm install
```

4. Iniciar o servidor:

```powershell
npm run dev
```

5. Abrir `http://127.0.0.1:5173` no navegador.

O terminal deve permanecer aberto. Para encerrar, pressionar `Ctrl + C`.

No modo aleatório, cada clique em **Gerar e executar** sorteia quantidade de
tarefas, durações, precedências, máquinas, prazo e semente. O algoritmo
selecionado roda no próprio navegador e atualiza métricas, Gantt, DAG, rastreio e
interpretação. As instâncias fixas continuam disponíveis para uma demonstração
reproduzível.

Para proteger a apresentação contra travamentos, a força bruta recebe instâncias
menores e possui um limite didático de estados. Se o limite for atingido, a
interface informa que a busca foi interrompida e não chama o resultado de ótimo.

## Execução dos algoritmos Python

Executar todos os algoritmos na instância de exemplo:

```powershell
python src/scheduler.py instances/exemplo.json --algoritmo todos
```

Executar apenas um algoritmo:

```powershell
python src/scheduler.py instances/exemplo.json --algoritmo guloso
```

Valores aceitos por `--algoritmo`:

- `forca-bruta`;
- `backtracking`;
- `divisao-conquista`;
- `programacao-dinamica`;
- `guloso`;
- `grasp`;
- `todos`.

## Benchmark e testes

```powershell
# Reproduz os experimentos e atualiza resultados/benchmark.csv
python scripts/run_benchmarks.py

# Testa o núcleo Python
python -m unittest discover -s tests -v

# Testa a aplicação web e cria o build de produção
npm run check
```

## Formato de uma instância

```json
{
  "nome": "exemplo",
  "maquinas": 3,
  "prazo": 12,
  "tarefas": [
    {"id": "A", "duracao": 3, "predecessoras": []},
    {"id": "B", "duracao": 2, "predecessoras": ["A"]}
  ]
}
```

Os identificadores devem ser únicos, as durações devem ser positivas e as
precedências precisam formar um grafo acíclico.

## Gerar novamente o relatório

```powershell
python scripts/montar_relatorio.py
python -m pip install -r requirements-pdf.txt
python scripts/gerar_pdf.py
```

O PDF será salvo em `output/pdf/Relatorio_Escalonamento_Tarefas.pdf`.

## Problemas comuns

### `npm` não é reconhecido

Instalar Node.js 20 ou superior e reabrir o terminal.

### O PowerShell bloqueia `npm.ps1`

Usar os executáveis com extensão `.cmd`:

```powershell
npm.cmd install
npm.cmd run dev
```

### `python` não é reconhecido

Instalar Python 3.10 ou superior e habilitar a opção de adicionar Python ao
`PATH`. Em instalações que disponibilizam o iniciador `py`, os comandos também
podem ser executados como `py src/scheduler.py ...`.

### A porta 5173 está ocupada

Encerrar a execução anterior com `Ctrl + C` e iniciar o servidor novamente.

## Roteiro rápido de demonstração

1. Apresentar a definição formal exibida na página inicial.
2. Gerar uma instância aleatória com o algoritmo guloso.
3. Interpretar o Gantt, o DAG, o *makespan* e o prazo.
4. Comparar força bruta, guloso e GRASP.
5. Abrir a instância de prazo inviável e explicar o limite inferior.
6. Mostrar o benchmark e o crescimento exponencial.
7. Encerrar com a redução de PARTITION.
