# Arquitetura do projeto

## Visao geral

O projeto possui dois componentes separados:

1. **Nucleo cientifico em Python (`src/`)**: implementa e mede os algoritmos. E a fonte dos resultados do trabalho.
2. **Camada de apresentacao web (`web/`)**: explica e visualiza os resultados. Nao substitui os algoritmos nem fabrica novas medidas no navegador.

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

A interface usa HTML semantico, CSS responsivo e JavaScript sem framework. Vite fornece o servidor de desenvolvimento, recarregamento automatico e a compilacao. Isso reduz dependencias e deixa o projeto simples de apresentar com Node.js.

## Reprodutibilidade

- Instancias JSON versionadas.
- Semente do GRASP fixa em 42.
- Benchmark bruto em CSV.
- Forca bruta limitada por tamanho.
- Interface sem API externa e sem envio de dados.

