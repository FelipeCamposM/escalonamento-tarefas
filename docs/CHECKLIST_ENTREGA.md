# Checklist de entrega e auditoria do trabalho

Auditoria realizada com base em `Estrutura_Requisitos_TrabalhoFinalv16.pdf`.
Este documento separa o que já está implementado do que ainda exige decisão ou
informação do grupo.

## Resumo executivo

O projeto está **tecnicamente implementado e testado**, mas ainda não deve ser
enviado como versão final. Os bloqueios obrigatórios são: identificação dos
quatro integrantes, revisão coletiva, geração do PDF e criação do pacote final
no formato pedido pela disciplina.

Legenda: ✅ concluído · ⚠️ requer revisão/ação do grupo · ⛔ pendente obrigatório

## Requisitos acadêmicos

| Requisito do enunciado | Estado | Evidência ou ação necessária |
|---|:---:|---|
| Tema e problema definidos | ✅ | `P|prec|Cmax`, com prazo global na versão de decisão |
| Implementação em linguagem aceita | ✅ | Python 3 em `src/scheduler.py` |
| Força bruta | ✅ | enumeração de ordens topológicas e máquinas |
| Backtracking | ✅ | branch-and-bound, incumbente gulosa e quebra de simetria |
| Divisão e conquista | ✅ | implementada e justificada como heurística |
| Programação dinâmica | ✅ | estados orientados a eventos e memoização |
| Algoritmo guloso | ✅ | *list scheduling* por caminho crítico |
| Aproximação/heurística | ✅ | GRASP com 200 construções e semente controlada |
| Contagem de instruções/operações | ✅ | instrumentação das operações dominantes |
| Medição de tempo | ✅ | `perf_counter`, CSV e tabela no relatório |
| Comparação experimental | ✅ | tamanhos 6, 8, 10 e 12; três instâncias por tamanho |
| Prova de pertinência a NP | ✅ | certificado e verificador polinomial |
| Discussão de NP-dificuldade | ✅ | redução polinomial de `PARTITION` |
| Referências teóricas | ✅ | Cormen, Graham, Lenstra, Ullman e Ziviani |
| Aplicações práticas | ✅ | compilação paralela, nuvem, produção e projetos |

## Conteúdo exigido na documentação

| Seção | Estado | Localização ou ação necessária |
|---|:---:|---|
| Integrantes em ordem alfabética e matrículas | ⛔ | substituir os quatro marcadores no início do relatório |
| Introdução e descrição do problema | ✅ | seção 1 de `RELATORIO.md` |
| Prova de que pertence a NP | ✅ | seção 2.1 |
| Descrição das implementações | ✅ | seção 3 |
| Código-fonte inserido na documentação | ✅ | gerado em `RELATORIO_COM_CODIGO.md` |
| Complexidade de tempo e espaço | ✅ | seção 4 |
| Análise dos resultados | ✅ | seção 5 e `resultados/benchmark.csv` |
| Conclusão e dificuldades | ✅ | seção 7 |
| Bibliografia e citações no texto | ✅ | seções 2, 3, 8 |
| PDF final | ⛔ | gerar somente depois de preencher e revisar os dados do grupo |

## Qualidade do software

| Verificação | Estado | Evidência |
|---|:---:|---|
| Validação da entrada e do DAG | ✅ | núcleo rejeita IDs, durações e dependências inválidas |
| Verificador independente das escalas | ✅ | checa tarefas, máquinas, durações, precedências e sobreposição |
| Testes Python | ✅ | `python -m unittest discover -s tests -v` |
| Testes JavaScript | ✅ | `npm run test:web` |
| Build de produção | ✅ | `npm run build` |
| Integração contínua | ✅ | `.github/workflows/ci.yml` |
| Instâncias reproduzíveis | ✅ | `instances/` e sementes controladas |
| Interface executada ao vivo | ✅ | motor em `web/scheduler-live.js` |
| Evidências visuais | ✅ | cinco imagens em `prints/` |
| README para GitHub | ✅ | instalação, prints, teoria, resultados e documentação |

## Pontos que merecem revisão humana

1. **Autores:** preencher os quatro nomes completos e matrículas em ordem
   alfabética no relatório e no README.
2. **Turma e capa:** confirmar professor, instituição, disciplina, cidade, turma
   e ano que devem aparecer na versão diagramada.
3. **Resultados:** decidir se o grupo repetirá o benchmark na máquina usada para
   a entrega. Se repetir, atualizar o CSV e a tabela do relatório.
4. **Divisão e conquista:** manter a classificação de heurística e sua
   justificativa; não apresentar o método como exato.
5. **Demonstração:** ensaiar uma instância aleatória e uma instância de prazo
   inviável; manter os prints como plano de contingência.
6. **Referências:** aplicar a norma bibliográfica exigida pelo professor, caso
   exista uma norma além do que consta no enunciado.

## Sequência recomendada para finalizar

- [ ] Receber os dados dos quatro integrantes e colocá-los em ordem alfabética.
- [ ] Fazer uma leitura coletiva e ajustar a linguagem para refletir a autoria do grupo.
- [ ] Executar `python scripts/montar_relatorio.py` após a última edição.
- [ ] Diagramar `RELATORIO_COM_CODIGO.md` e gerar o PDF final.
- [ ] Verificar visualmente todas as páginas, tabelas, quebras e código do PDF.
- [ ] Ensaiar o roteiro de 20 minutos com um ou dois apresentadores e presença do grupo completo.
- [ ] Publicar o repositório remoto e confirmar a execução verde do GitHub Actions.
- [ ] Criar o ZIP apenas depois da aprovação visual, usando o nome exigido.
- [ ] Abrir o ZIP em outra pasta e testar os comandos do README.

## Critério de pronto

A entrega estará realmente pronta quando os dados do grupo estiverem corretos,
o PDF tiver sido revisado página por página, a apresentação tiver sido ensaiada,
o CI remoto estiver verde e o ZIP final abrir e executar em uma pasta limpa.
