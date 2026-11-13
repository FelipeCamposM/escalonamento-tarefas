# Manual de execucao

## Visualizacao no navegador

```powershell
npm install
npm run dev
```

Abrir `http://127.0.0.1:5173`. No modo aleatorio, cada clique em **Gerar e
executar** sorteia quantidade de tarefas, duracoes, precedencias, maquinas e
prazo. Em seguida, o algoritmo selecionado roda no navegador e atualiza
metricas, Gantt, DAG, rastreio e interpretacao. As instancias fixas continuam
disponiveis para uma demonstracao reproduzivel.

Para proteger a apresentacao contra travamentos, a forca bruta recebe
instancias menores e possui um limite didatico de estados. Se o limite for
atingido, a interface informa que a busca foi interrompida e nao chama o
resultado de otimo.

## Algoritmos Python

```powershell
python src/scheduler.py instances/exemplo.json --algoritmo todos
python scripts/run_benchmarks.py
python -m unittest discover -s tests -v
```

## Validacao web

```powershell
npm run check
```

O comando executa testes e cria `dist/`.

## Roteiro de demonstracao

1. Apresentar a definicao formal do topo.
2. Comparar Forca bruta, Guloso e GRASP no laboratorio.
3. Trocar para prazo inviavel e explicar o limite inferior.
4. Mostrar benchmark e crescimento exponencial.
5. Encerrar com a reducao de PARTITION.
