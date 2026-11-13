import { generateRandomInstance, lowerBound, runAlgorithm } from "./scheduler-live.js";

const algorithms=[
 {id:"forca",name:"Força bruta",kind:"exata",complexity:"O(n! · mⁿ · (n + |E|))",description:"Enumera ordens topológicas e atribuições de máquinas."},
 {id:"backtracking",name:"Backtracking + branch-and-bound",kind:"exata",complexity:"Exponencial, com podas",description:"Elimina ramos usando incumbente, limite inferior e simetria."},
 {id:"divisao",name:"Divisão e conquista heurística",kind:"heurística",complexity:"O(n log n + |E|)",description:"Particiona a prioridade do DAG e combina por list scheduling."},
 {id:"dp",name:"Programação dinâmica por eventos",kind:"exata",complexity:"Exponencial em estados",description:"Memoriza tarefas concluídas e configurações em execução."},
 {id:"guloso",name:"Guloso por caminho crítico",kind:"aproximação",complexity:"O(n² + |E|)",description:"Despacha a tarefa pronta com maior caminho restante."},
 {id:"grasp",name:"GRASP aleatorizado",kind:"heurística",complexity:"I · O(n² + |E|)",description:"Repete construções aleatorizadas e guarda a melhor."}
];
const exampleTasks=[{id:"A",duration:3,predecessors:[]},{id:"B",duration:2,predecessors:[]},{id:"C",duration:4,predecessors:["A"]},{id:"D",duration:2,predecessors:["A"]},{id:"E",duration:3,predecessors:["B"]},{id:"F",duration:2,predecessors:["C","D"]},{id:"G",duration:2,predecessors:["E"]},{id:"H",duration:1,predecessors:["F","G"]}];
const fixedInstances={exemplo:{name:"projeto-exemplo",seed:42,machines:2,deadline:12,density:.22,tasks:exampleTasks},inviavel:{name:"prazo-inviavel",seed:42,machines:2,deadline:7,density:.22,tasks:exampleTasks}};
const benchmarks=[["Guloso",.166,"heurística","87","10/12"],["Divisão e conquista",.220,"heurística","112","11/12"],["GRASP",33.172,"heurística","17.951","12/12"],["Backtracking",69.533,"exata","45.505","12/12"],["Programação dinâmica",128.784,"exata","29.948","12/12"],["Força bruta",880.024,"exata","887.983","3/3 (n=6)"]];
const $=s=>document.querySelector(s),fmt=(v,d=3)=>v.toLocaleString("pt-BR",{minimumFractionDigits:d,maximumFractionDigits:d});
let currentInstance,currentResult,generation=0;

function renderOptions(){
 $("#algorithm-select").innerHTML=algorithms.map(a=>`<option value="${a.id}" ${a.id==="guloso"?"selected":""}>${a.name}</option>`).join("");
 $("#algorithm-list").innerHTML=algorithms.map((a,i)=>`<article class="algorithm-row"><span class="number">0${i+1}</span><div><h3>${a.name}</h3><p>${a.description}</p></div><code>${a.complexity}</code><span>${a.kind==="exata"?"ótimo garantido":"solução rápida"}</span><span class="tag ${a.kind==="exata"?"exact":""}">${a.kind}</span></article>`).join("");
}
function renderSummary(instance,result){
 const edges=instance.tasks.reduce((sum,task)=>sum+task.predecessors.length,0),status=result.warning?result.warning:"execução concluída";
 $("#seed-value").textContent=String(instance.seed).slice(-6);
 $("#instance-summary").innerHTML=`<span>seed <strong>${instance.seed}</strong></span><span><strong>${instance.tasks.length}</strong> tarefas</span><span><strong>${instance.machines}</strong> máquinas</span><span><strong>${edges}</strong> precedências</span><span>densidade <strong>${Math.round((instance.density??0)*100)}%</strong></span><span class="fresh">${status}</span>`;
}
function renderGantt(instance,result){
 const horizon=Math.max(result.makespan,instance.deadline,6),step=100/horizon,axis=Array.from({length:horizon+1},(_,i)=>`<span>${i}</span>`).join("");let html=`<div class="gantt-axis" style="grid-template-columns:repeat(${horizon+1},1fr)">${axis}</div>`;
 for(let m=0;m<instance.machines;m++){const blocks=result.schedule.filter(s=>s.machine===m).sort((a,b)=>a.start-b.start).map(s=>`<span class="gantt-task ${m%2?"alt":""}" title="${s.task}: ${s.start}-${s.finish}" style="--start:${s.start*step};--duration:${(s.finish-s.start)*step}">${s.task}<small>&nbsp;${s.start}-${s.finish}</small></span>`).join("");html+=`<div class="gantt-lane"><strong>M${m+1}</strong><div class="gantt-track" style="--tick:${step}%">${blocks}</div></div>`}$("#gantt").innerHTML=html;
}
function renderLog(instance,result){
 const tasks=Object.fromEntries(instance.tasks.map(task=>[task.id,task])),ordered=[...result.schedule].sort((a,b)=>a.start-b.start||a.machine-b.machine);
 $("#event-log").innerHTML=ordered.map(s=>`<li><b>t = ${String(s.start).padStart(2,"0")}</b> · <strong>${s.task}</strong> (p=${tasks[s.task].duration}) inicia em M${s.machine+1}; termina em ${s.finish}.</li>`).join("");
 $("#operation-count").textContent=`${result.instructions.toLocaleString("pt-BR")} operações`;
}
function graphPositions(instance){
 const layer={},tasks=Object.fromEntries(instance.tasks.map(task=>[task.id,task]));
 const visit=id=>layer[id]??=tasks[id].predecessors.length?1+Math.max(...tasks[id].predecessors.map(visit)):0;
 instance.tasks.forEach(task=>visit(task.id));const maxLayer=Math.max(0,...Object.values(layer)),groups={};
 instance.tasks.forEach(task=>(groups[layer[task.id]]??=[]).push(task.id));const positions={};
 Object.entries(groups).forEach(([level,ids])=>ids.forEach((id,index)=>{positions[id]=[70+(Number(level)*(620/Math.max(1,maxLayer))),45+index*(220/Math.max(1,ids.length-1))]}));
 return {positions,maxLayer};
}
function renderGraph(instance){
 const {positions}=graphPositions(instance),tasks=Object.fromEntries(instance.tasks.map(task=>[task.id,task]));
 const marker=`<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10z" fill="#a6b6b1"/></marker></defs>`;
 const lines=instance.tasks.flatMap(task=>task.predecessors.map(pred=>{const[x1,y1]=positions[pred],[x2,y2]=positions[task.id];return`<path class="graph-edge" marker-end="url(#arrow)" d="M${x1+22} ${y1} C${(x1+x2)/2} ${y1},${(x1+x2)/2} ${y2},${x2-25} ${y2}"/>`})).join("");
 const nodes=Object.entries(positions).map(([id,[x,y]])=>`<g class="graph-node"><circle cx="${x}" cy="${y}" r="23"/><text x="${x}" y="${y}">${id}</text><text class="duration" x="${x}" y="${y+38}">p=${tasks[id].duration}</text></g>`).join("");
 $("#precedence-graph").innerHTML=marker+lines+nodes;const edgeCount=instance.tasks.reduce((sum,task)=>sum+task.predecessors.length,0);$(".dag-chip").textContent=`DAG · ${edgeCount} arestas`;
}
function renderBenchmarks(){const logs=benchmarks.map(b=>Math.log10(b[1]+.1)),max=Math.max(...logs);$("#benchmark-chart").innerHTML=benchmarks.map((b,i)=>`<div class="bar-row"><span>${b[0]}</span><div class="bar-track"><div class="bar" style="--w:${Math.max(3,logs[i]/max*100)}%"></div></div><strong>${fmt(b[1])} ms</strong></div>`).join("");$("#benchmark-table").innerHTML=benchmarks.map(b=>`<tr><td><strong>${b[0]}</strong></td><td>${b[2]}</td><td>${fmt(b[1])} ms</td><td>${b[3]}</td><td>${b[4]}</td></tr>`).join("")}
function renderMetrics(instance,result,algorithm){
 const feasible=result.makespan<=instance.deadline,slack=Math.abs(instance.deadline-result.makespan),lb=lowerBound(instance),decision=$("#metric-decision");
 $("#metric-makespan").textContent=result.makespan;$("#metric-deadline").textContent=instance.deadline;$("#metric-slack").textContent=`${feasible?"folga":"atraso"} de ${slack}`;$("#metric-time").textContent=result.metrics.elapsedMs<.001?"<0,001":fmt(result.metrics.elapsedMs);decision.textContent=feasible?"SIM":"NÃO";decision.className=feasible?"success":"danger";$("#metric-kind").textContent=result.exact?"solução exata":`solução ${algorithm.kind}`;
 if(lb>instance.deadline){$("#insight-title").textContent="O prazo viola um limite matemático";$("#insight-text").textContent=`O limite inferior é ${lb}, mas o prazo sorteado foi ${instance.deadline}. Nenhum algoritmo pode tornar essa instância viável.`}
 else if(result.exact&&result.makespan===lb){$("#insight-title").textContent="Ótimo certificado pelo limite inferior";$("#insight-text").textContent=`A execução ao vivo terminou em ${result.makespan}, exatamente o menor valor permitido pelo trabalho e pelo caminho crítico.`}
 else{$("#insight-title").textContent=feasible?"Escala viável encontrada ao vivo":"A busca não atingiu o prazo";$("#insight-text").textContent=`O algoritmo produziu makespan ${result.makespan} para prazo ${instance.deadline}. O limite inferior desta instância é ${lb}.`}
 $("#bound-value").textContent=`LB = ${lb} · D = ${instance.deadline} · Cmax = ${result.makespan}`;
}
function renderAll(instance,result){const algorithm=algorithms.find(item=>item.id===$("#algorithm-select").value);renderSummary(instance,result);renderMetrics(instance,result,algorithm);renderGantt(instance,result);renderLog(instance,result);renderGraph(instance)}
function nextSeed(){generation++;return (Date.now()+generation*7919)>>>0}
function execute({fresh=false}={}){
 const button=$("#run-button"),algorithmId=$("#algorithm-select").value,mode=$("#instance-select").value;button.classList.add("running");button.disabled=true;
 requestAnimationFrame(()=>setTimeout(()=>{try{if(fresh||!currentInstance){currentInstance=mode==="aleatorio"?generateRandomInstance(algorithmId,nextSeed()):structuredClone(fixedInstances[mode])}currentResult=runAlgorithm(currentInstance,algorithmId,currentInstance.seed);renderAll(currentInstance,currentResult)}catch(error){$("#instance-summary").innerHTML=`<span class="fresh">Erro: ${error.message}</span>`}finally{button.classList.remove("running");button.disabled=false}},80));
}
function init(){renderOptions();renderBenchmarks();execute({fresh:true});$("#run-button").addEventListener("click",()=>execute({fresh:$("#instance-select").value==="aleatorio"}));$("#algorithm-select").addEventListener("change",()=>execute());$("#instance-select").addEventListener("change",()=>execute({fresh:true}))}
document.addEventListener("DOMContentLoaded",init);
