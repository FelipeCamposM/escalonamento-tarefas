# Manual de execucao

## Visualizacao no navegador

```powershell
npm install
npm run dev
```

Abrir `http://127.0.0.1:5173`. E possivel escolher estrategia e alternar entre prazo viavel e inviavel. O botao atualiza metricas, Gantt, rastreio e interpretacao.

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

