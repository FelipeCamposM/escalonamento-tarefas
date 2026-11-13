# Arquitetura do projeto

## Visao geral

O projeto possui dois componentes separados:

1. **Nucleo cientifico em Python (`src/`)**: implementa e mede os algoritmos. E a fonte dos resultados do trabalho.
2. **Laboratorio web (`web/`)**: gera instancias e executa os seis paradigmas ao vivo no navegador. Essa versao serve para demonstracao interativa; o nucleo Python continua sendo a referencia dos experimentos do relatorio.

Essa separacao impede que detalhes visuais contaminem os experimentos e permite executar os algoritmos em modo texto antes de apresentar os resultados.

## Fluxo de dados

```text
instances/*.json
       |
       v
src/scheduler.py ---> verificador independente
       |
       v
scripts/run_benchmarks.py
       |
       v
resultados/benchmark.csv ---> relatorio + aplicacao web
```

## Nucleo Python

`scheduler.py` concentra os modelos imutaveis `Task`, `Instance` e `Slot`, as metricas instrumentadas e os seis algoritmos. Todos devolvem `Result`, evitando comparacoes entre formatos incompatíveis.

O verificador `validate_schedule` nao confia no algoritmo produtor. Ele confirma cobertura das tarefas, duracoes, limites de maquina, precedencias e ausencia de sobreposicao.

## Interface web

A interface usa HTML semantico, CSS responsivo e JavaScript sem framework. O
modulo `scheduler-live.js` contem gerador pseudoaleatorio deterministico,
verificador e seis algoritmos. Cada execucao sorteia duracoes, DAG, maquinas e
prazo; depois valida a escala antes de renderiza-la. Vite fornece servidor,
recarregamento automatico e compilacao.

A duplicacao entre Python e JavaScript e intencional: Python preserva a base
cientifica e o benchmark; JavaScript permite demonstracao sem depender de um
servidor ou de Python instalado. Testes de concordancia verificam os metodos
exatos em instancias pequenas.

## Reprodutibilidade

- Instancias JSON versionadas.
- Semente do GRASP fixa em 42.
- Benchmark bruto em CSV.
- Forca bruta limitada por tamanho.
- Interface sem API externa e sem envio de dados.
