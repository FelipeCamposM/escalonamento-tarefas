# Metodologia experimental

## Objetivo

Comparar qualidade da escala, tempo observado e operacoes dominantes sob a mesma implementacao e no mesmo computador.

## Ambiente

- Windows 11 Pro; AMD Ryzen 7 5700U; 23,4 GB de memoria.
- Python 3.14.10 para o benchmark; Node.js 22 para a visualizacao.

## Instancias e variaveis

Foram usados `n = 6, 8, 10, 12`, tres sementes por tamanho e tres maquinas. Duracoes variam de 1 a 6. Registram-se makespan, tempo, estados, ramos, comparacoes e podas. A soma dessas contagens e uma metrica didatica, nao instrucoes reais de processador.

## Controle de validade

Cada escala passa por um verificador independente. Os metodos exatos devem concordar no makespan; divergencias interrompem a coleta.

## Ameacas a validade

- Uma execucao por instancia nao sustenta inferencia estatistica forte.
- Tempos menores que um milissegundo sofrem ruido.
- A amostra pseudoaleatoria e pequena.
- O GRASP atingir 12 de 12 otimos nao prova desempenho futuro.
- Conclusoes valem para `P|prec|Cmax`, nao automaticamente para outras variantes.

