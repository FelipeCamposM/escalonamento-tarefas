# Roteiro de apresentação — 20 minutos

Este roteiro foi dimensionado para 20 minutos. Conforme a recomendação do
enunciado, o grupo pode escolher um ou dois integrantes com maior aptidão para
apresentar, mantendo a presença obrigatória dos quatro. Os nomes podem ser
associados aos blocos depois que o grupo definir a divisão.

## Distribuição do tempo

| Tempo | Bloco | Objetivo |
|---:|---|---|
| 0:00–2:00 | Abertura e motivação | apresentar o problema e duas aplicações reais |
| 2:00–5:00 | Modelo formal e complexidade | explicar `P|prec|Cmax`, certificado e redução de `PARTITION` |
| 5:00–10:00 | Estratégias | contrastar os seis algoritmos sem entrar em cada linha de código |
| 10:00–14:00 | Experimentos | explicar instâncias, métricas, limites e resultados |
| 14:00–18:00 | Demonstração ao vivo | gerar um teste aleatório, ler Gantt/DAG e trocar o algoritmo |
| 18:00–20:00 | Conclusões | sintetizar compromissos, dificuldades e aprendizados |

## 1. Abertura e motivação — 2 minutos

- Começar com a pergunta: “como distribuir tarefas dependentes entre recursos
  paralelos para terminar o mais cedo possível?”
- Citar compilação paralela e execução de fluxos de dados em nuvem.
- Mostrar rapidamente a tela inicial do ScheduleLab.
- Declarar o objetivo: comparar paradigmas exatos e heurísticos usando tempo,
  operações instrumentadas e qualidade da solução.

## 2. Modelo e NP-completude — 3 minutos

- Definir tarefas, durações, máquinas idênticas, precedências, não preempção,
  *makespan* e prazo.
- Explicar por que duas ou mais máquinas tornam a distribuição combinatória.
- Pertinência a NP: a escala informa máquina e intervalo; o verificador confere
  tudo em tempo polinomial.
- NP-dificuldade: transformar `PARTITION` em tarefas sem precedência, duas
  máquinas e prazo `B`.
- Concluir: pertence a NP e é NP-difícil, portanto é NP-completo.

## 3. Seis estratégias — 5 minutos

Agrupar a explicação por comportamento:

- **Exatos:** força bruta, backtracking e programação dinâmica. Garantem o ótimo,
  mas têm crescimento exponencial.
- **Rápidos:** guloso e divisão e conquista heurística. Entregam soluções válidas
  rapidamente, mas podem não atingir o ótimo.
- **Busca heurística:** GRASP. Explora múltiplas construções aleatorizadas e
  preserva a melhor solução.

Pontos importantes:

- o backtracking reduz a busca com limite inferior, incumbente e simetria;
- a DP evita recalcular estados, trocando tempo por memória;
- o guloso escolhe maior caminho crítico remanescente;
- divisão e conquista não é exata neste modelo, porque partições ainda compartilham
  máquinas e podem ter precedências cruzadas;
- a semente torna os experimentos reproduzíveis.

## 4. Metodologia e resultados — 4 minutos

- Três instâncias para cada `n = 6, 8, 10, 12`, três máquinas.
- Mesmas instâncias para todos os métodos; força bruta somente para `n = 6`.
- Métricas: tempo, operações dominantes, *makespan*, validade e diferença do ótimo.
- Destacar os resultados:
  - métodos exatos concordaram quando comparados;
  - guloso encontrou 10 de 12 ótimos;
  - divisão e conquista encontrou 11 de 12;
  - GRASP encontrou os 12 ótimos da amostra, sem garantia teórica;
  - força bruta foi mais de cinco mil vezes mais lenta que o guloso mesmo nas
    instâncias pequenas.
- Ressalvar que tempo abaixo de um milissegundo sofre ruído e por isso a contagem
  de operações complementa a medição.

## 5. Demonstração ao vivo — 4 minutos

1. Abrir `http://127.0.0.1:5173` com o servidor já iniciado.
2. Escolher o guloso e clicar em **Gerar e executar**.
3. Mostrar que semente, tarefas, durações, DAG e prazo mudaram.
4. Ler o gráfico de Gantt e indicar duas relações de precedência no DAG.
5. Apontar *makespan*, prazo, validade, operações e tempo.
6. Trocar para backtracking ou GRASP e gerar outro caso.
7. Abrir a instância fixa inviável para explicar a versão de decisão.

Evitar gastar tempo esperando força bruta em uma instância grande. O laboratório
reduz automaticamente o tamanho desse caso, mas a demonstração principal deve
usar guloso, backtracking ou GRASP.

## 6. Conclusão — 2 minutos

- Não existe um único vencedor para todos os cenários.
- Métodos exatos são referência de qualidade em entradas pequenas.
- Heurísticas e guloso são adequados quando a resposta precisa ser rápida.
- Representação correta, validação independente e experimento reproduzível foram
  tão importantes quanto implementar os algoritmos.
- Dificuldades: paralelismo, precedências, explosão de estados, comparação justa
  e adaptação honesta de divisão e conquista.

## Perguntas prováveis

**Por que não usar apenas o guloso?**  
Porque ele é rápido, mas não garante o ótimo. Os métodos exatos quantificam a
perda de qualidade nas instâncias pequenas.

**O GRASP sempre encontra o ótimo?**  
Não. Encontrou o ótimo nas 12 instâncias avaliadas, mas é uma observação
experimental, não uma garantia.

**Por que a força bruta só usa seis tarefas?**  
O espaço inclui até `n!` ordens e `m^n` atribuições; o crescimento inviabiliza a
comparação em entradas maiores dentro de um tempo razoável.

**A divisão e conquista é exata?**  
Não nesta implementação. As partes não são independentes devido às precedências
cruzadas e às máquinas compartilhadas; por isso o método produz prioridades para
uma combinação heurística.

**Como vocês sabem que uma escala é válida?**  
Um verificador independente confere unicidade, durações, máquinas, sobreposições,
precedências e prazo.

## Plano de contingência

- Deixar a aplicação e o terminal abertos antes de começar.
- Manter `prints/02-laboratorio.png`, `prints/03-prazo-inviavel.png` e
  `prints/04-experimentos.png` disponíveis caso o navegador falhe.
- Levar o CSV e uma cópia local do repositório; a demonstração não depende de internet.
- Cronometrar pelo menos dois ensaios e cortar detalhes antes de cortar a conclusão.
