// Nucleo de demonstracao executado inteiramente no navegador.
// Mantem a mesma formulacao P|prec|Cmax usada pela implementacao Python.

export function seededRandom(seed) {
  let value = seed >>> 0;
  return () => {
    value += 0x6d2b79f5;
    let t = value;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const randint = (rng, min, max) => Math.floor(rng() * (max - min + 1)) + min;
const taskMap = instance => Object.fromEntries(instance.tasks.map(task => [task.id, task]));
const makespan = schedule => Math.max(0, ...schedule.map(slot => slot.finish));

export function topologicalOrder(instance, priority = {}) {
  const indegree = Object.fromEntries(instance.tasks.map(task => [task.id, task.predecessors.length]));
  const successors = Object.fromEntries(instance.tasks.map(task => [task.id, []]));
  for (const task of instance.tasks) for (const pred of task.predecessors) successors[pred].push(task.id);
  const ready = instance.tasks.filter(task => indegree[task.id] === 0).map(task => task.id);
  const order = [];
  while (ready.length) {
    ready.sort((a, b) => (priority[b] ?? 0) - (priority[a] ?? 0) || a.localeCompare(b));
    const current = ready.shift();
    order.push(current);
    for (const child of successors[current]) if (--indegree[child] === 0) ready.push(child);
  }
  if (order.length !== instance.tasks.length) throw new Error("O grafo gerado possui ciclo");
  return order;
}

export function criticalPriorities(instance) {
  const tasks = taskMap(instance);
  const successors = Object.fromEntries(instance.tasks.map(task => [task.id, []]));
  for (const task of instance.tasks) for (const pred of task.predecessors) successors[pred].push(task.id);
  const memo = {};
  const visit = id => memo[id] ??= tasks[id].duration + Math.max(0, ...successors[id].map(visit));
  return Object.fromEntries(instance.tasks.map(task => [task.id, visit(task.id)]));
}

export function lowerBound(instance) {
  const work = instance.tasks.reduce((sum, task) => sum + task.duration, 0);
  return Math.max(Math.ceil(work / instance.machines), ...Object.values(criticalPriorities(instance)));
}

export function validateSchedule(instance, schedule) {
  const errors = [];
  const tasks = taskMap(instance);
  const byTask = Object.fromEntries(schedule.map(slot => [slot.task, slot]));
  if (schedule.length !== instance.tasks.length || Object.keys(byTask).length !== instance.tasks.length) errors.push("tarefas ausentes ou repetidas");
  for (const slot of schedule) {
    const task = tasks[slot.task];
    if (!task || slot.finish - slot.start !== task.duration) errors.push(`duracao invalida em ${slot.task}`);
    if (slot.machine < 0 || slot.machine >= instance.machines) errors.push(`maquina invalida em ${slot.task}`);
    for (const pred of task?.predecessors ?? []) if (!byTask[pred] || byTask[pred].finish > slot.start) errors.push(`precedencia ${pred} -> ${slot.task}`);
  }
  for (let machine = 0; machine < instance.machines; machine++) {
    const lane = schedule.filter(slot => slot.machine === machine).sort((a, b) => a.start - b.start);
    for (let i = 1; i < lane.length; i++) if (lane[i - 1].finish > lane[i].start) errors.push(`sobreposicao em M${machine + 1}`);
  }
  return { valid: errors.length === 0, errors };
}

function listSchedule(instance, { priority = criticalPriorities(instance), choose } = {}) {
  const startClock = performance.now();
  const tasks = taskMap(instance), completed = new Set(), scheduled = new Set();
  const free = Array.from({ length: instance.machines }, (_, index) => index);
  const running = [], schedule = [], metrics = { states: 0, branches: 0, comparisons: 0, prunes: 0 };
  let now = 0;
  while (completed.size < instance.tasks.length) {
    metrics.states++;
    for (const item of running.filter(item => item.finish === now)) {
      completed.add(item.task); free.push(item.machine); running.splice(running.indexOf(item), 1);
    }
    const ready = instance.tasks.filter(task => !scheduled.has(task.id) && task.predecessors.every(pred => completed.has(pred))).map(task => task.id);
    metrics.comparisons += instance.tasks.length;
    while (free.length && ready.length) {
      const id = choose ? choose([...ready], priority) : ready.sort((a, b) => priority[b] - priority[a] || tasks[b].duration - tasks[a].duration)[0];
      const machine = Math.min(...free); free.splice(free.indexOf(machine), 1); ready.splice(ready.indexOf(id), 1);
      const finish = now + tasks[id].duration;
      running.push({ task: id, machine, finish }); scheduled.add(id); schedule.push({ task: id, machine, start: now, finish }); metrics.branches++;
    }
    if (running.length) now = Math.min(...running.map(item => item.finish));
    else if (completed.size < instance.tasks.length) throw new Error("Nenhuma tarefa pronta");
  }
  metrics.elapsedMs = performance.now() - startClock;
  return { schedule, metrics, exact: false };
}

function serialSchedule(instance, order, assignments) {
  const tasks = taskMap(instance), machineAvailable = Array(instance.machines).fill(0), finish = {}, schedule = [];
  order.forEach((id, index) => {
    const machine = assignments[index], predFinish = Math.max(0, ...tasks[id].predecessors.map(pred => finish[pred]));
    const start = Math.max(machineAvailable[machine], predFinish), end = start + tasks[id].duration;
    schedule.push({ task: id, machine, start, finish: end }); machineAvailable[machine] = end; finish[id] = end;
  });
  return schedule;
}

function greedy(instance) { return listSchedule(instance); }

function divideConquer(instance) {
  const start = performance.now(), metrics = { states: 0, branches: 0, comparisons: 0, prunes: 0 };
  const base = topologicalOrder(instance, criticalPriorities(instance)), rank = {};
  const assign = (items, offset) => {
    metrics.states++;
    if (items.length <= 1) { if (items.length) rank[items[0]] = offset; return; }
    const middle = Math.floor(items.length / 2);
    assign(items.slice(0, middle), offset + items.length - middle); assign(items.slice(middle), offset); metrics.branches++;
  };
  assign(base, 0);
  const result = listSchedule(instance, { priority: rank });
  for (const key of ["states", "branches", "comparisons", "prunes"]) result.metrics[key] += metrics[key];
  result.metrics.elapsedMs = performance.now() - start;
  return result;
}

function grasp(instance, rng, iterations = 120) {
  const start = performance.now(), priority = criticalPriorities(instance);
  let best = null; const aggregate = { states: 0, branches: 0, comparisons: 0, prunes: 0 };
  for (let iteration = 0; iteration < iterations; iteration++) {
    const result = listSchedule(instance, { priority, choose: ready => {
      ready.sort((a, b) => priority[b] - priority[a]);
      return ready[randint(rng, 0, Math.max(0, Math.ceil(ready.length * .35) - 1))];
    }});
    for (const key of ["states", "branches", "comparisons", "prunes"]) aggregate[key] += result.metrics[key];
    if (!best || makespan(result.schedule) < makespan(best.schedule)) best = result;
  }
  best.metrics = { ...aggregate, elapsedMs: performance.now() - start }; return best;
}

function bruteForce(instance, stateBudget = 750000) {
  const start = performance.now(), tasks = taskMap(instance), metrics = { states: 0, branches: 0, comparisons: 0, prunes: 0 };
  let best = null, bestValue = Infinity, cutoff = false;
  const visit = (order, assignments, finish, machineAvailable) => {
    if (++metrics.states > stateBudget) { cutoff = true; return; }
    if (order.length === instance.tasks.length) {
      metrics.comparisons++; const value = Math.max(...machineAvailable);
      if (value < bestValue) { bestValue = value; best = serialSchedule(instance, order, assignments); }
      return;
    }
    const placed = new Set(order), ready = instance.tasks.filter(task => !placed.has(task.id) && task.predecessors.every(pred => placed.has(pred)));
    for (const task of ready) for (let machine = 0; machine < instance.machines; machine++) {
      if (cutoff) return; metrics.branches++;
      const old = machineAvailable[machine], end = Math.max(old, Math.max(0, ...task.predecessors.map(pred => finish[pred]))) + task.duration;
      machineAvailable[machine] = end; finish[task.id] = end;
      visit([...order, task.id], [...assignments, machine], finish, machineAvailable);
      machineAvailable[machine] = old; delete finish[task.id];
    }
  };
  visit([], [], {}, Array(instance.machines).fill(0));
  if (!best) best = greedy(instance).schedule;
  metrics.elapsedMs = performance.now() - start;
  return { schedule: best, metrics, exact: !cutoff, warning: cutoff ? "limite didatico de busca atingido" : "" };
}

function backtracking(instance) {
  const start = performance.now(), tasks = taskMap(instance), priority = criticalPriorities(instance), lb = lowerBound(instance);
  const incumbent = greedy(instance); let best = incumbent.schedule, bestValue = makespan(best);
  const metrics = { states: 0, branches: 0, comparisons: 0, prunes: 0 };
  const visit = (order, assignments, finish, machineAvailable) => {
    metrics.states++; const current = Math.max(0, ...machineAvailable); metrics.comparisons++;
    if (current >= bestValue) { metrics.prunes++; return; }
    if (order.length === instance.tasks.length) { bestValue = current; best = serialSchedule(instance, order, assignments); return; }
    if (bestValue === lb) { metrics.prunes++; return; }
    const placed = new Set(order), ready = instance.tasks.filter(task => !placed.has(task.id) && task.predecessors.every(pred => placed.has(pred))).sort((a, b) => priority[b.id] - priority[a.id]);
    for (const task of ready) {
      const seen = new Set();
      for (let machine = 0; machine < instance.machines; machine++) {
        if (seen.has(machineAvailable[machine])) { metrics.prunes++; continue; } seen.add(machineAvailable[machine]); metrics.branches++;
        const old = machineAvailable[machine], end = Math.max(old, Math.max(0, ...task.predecessors.map(pred => finish[pred]))) + task.duration;
        if (end >= bestValue && order.length + 1 < instance.tasks.length) { metrics.prunes++; continue; }
        machineAvailable[machine] = end; finish[task.id] = end;
        visit([...order, task.id], [...assignments, machine], finish, machineAvailable);
        machineAvailable[machine] = old; delete finish[task.id];
      }
    }
  };
  visit([], [], {}, Array(instance.machines).fill(0)); metrics.elapsedMs = performance.now() - start;
  return { schedule: best, metrics, exact: true };
}

const combinations = (items, count) => {
  if (count === 0) return [[]]; const output = [];
  const walk = (start, chosen) => { if (chosen.length === count) { output.push([...chosen]); return; } for (let i = start; i < items.length; i++) { chosen.push(items[i]); walk(i + 1, chosen); chosen.pop(); } };
  walk(0, []); return output;
};

function dynamicProgramming(instance) {
  const started = performance.now(), tasks = instance.tasks, index = Object.fromEntries(tasks.map((task, i) => [task.id, i]));
  const predMasks = tasks.map(task => task.predecessors.reduce((mask, pred) => mask | (1 << index[pred]), 0));
  const full = (1 << tasks.length) - 1, memo = new Map(), policy = new Map(), metrics = { states: 0, branches: 0, comparisons: 0, prunes: 0 };
  const keyOf = (completed, running) => `${completed}|${running.map(item => item.join(",")).join(";")}`;
  const solve = (completed, running) => {
    const key = keyOf(completed, running); if (memo.has(key)) return memo.get(key); metrics.states++;
    if (completed === full && !running.length) { memo.set(key, 0); return 0; }
    const runningIds = new Set(running.map(item => item[0])), usedMachines = new Set(running.map(item => item[2]));
    const free = Array.from({ length: instance.machines }, (_, i) => i).filter(i => !usedMachines.has(i));
    const ready = tasks.map((_, i) => i).filter(i => !(completed & (1 << i)) && !runningIds.has(i) && (predMasks[i] & completed) === predMasks[i]);
    const take = Math.min(free.length, ready.length), choices = take ? combinations(ready, take) : [[]];
    let best = Infinity, bestChoice = [];
    for (const choice of choices) {
      metrics.branches++; const augmented = running.map(item => [...item]);
      choice.forEach((taskIndex, i) => augmented.push([taskIndex, tasks[taskIndex].duration, free[i]]));
      if (!augmented.length) continue;
      const delta = Math.min(...augmented.map(item => item[1])); let nextCompleted = completed; const nextRunning = [];
      for (const [taskIndex, remaining, machine] of augmented) remaining === delta ? nextCompleted |= 1 << taskIndex : nextRunning.push([taskIndex, remaining - delta, machine]);
      nextRunning.sort((a, b) => a[0] - b[0]); const value = delta + solve(nextCompleted, nextRunning); metrics.comparisons++;
      if (value < best) { best = value; bestChoice = choice; }
    }
    memo.set(key, best); policy.set(key, bestChoice); return best;
  };
  solve(0, []);
  let completed = 0, running = [], now = 0; const starts = new Map(), schedule = [];
  while (completed !== full || running.length) {
    const choice = policy.get(keyOf(completed, running)) ?? [], usedMachines = new Set(running.map(item => item[2]));
    const free = Array.from({ length: instance.machines }, (_, i) => i).filter(i => !usedMachines.has(i)); const augmented = running.map(item => [...item]);
    choice.forEach((taskIndex, i) => { starts.set(taskIndex, [free[i], now]); augmented.push([taskIndex, tasks[taskIndex].duration, free[i]]); });
    const delta = Math.min(...augmented.map(item => item[1])); now += delta; const next = [];
    for (const [taskIndex, remaining, machine] of augmented) {
      if (remaining === delta) { completed |= 1 << taskIndex; const [assigned, start] = starts.get(taskIndex); schedule.push({ task: tasks[taskIndex].id, machine: assigned, start, finish: now }); starts.delete(taskIndex); }
      else next.push([taskIndex, remaining - delta, machine]);
    }
    running = next.sort((a, b) => a[0] - b[0]);
  }
  metrics.elapsedMs = performance.now() - started; return { schedule, metrics, exact: true };
}

export function generateRandomInstance(algorithmId = "guloso", seed = Date.now()) {
  const rng = seededRandom(seed), exactSmall = ["forca", "backtracking", "dp"].includes(algorithmId);
  const taskCount = algorithmId === "forca" ? randint(rng, 5, 6) : exactSmall ? randint(rng, 6, 8) : randint(rng, 7, 11);
  const machines = algorithmId === "forca" ? 2 : randint(rng, 2, exactSmall ? 3 : 4), density = .18 + rng() * .22;
  const tasks = [];
  for (let i = 0; i < taskCount; i++) {
    const predecessors = [];
    for (let j = 0; j < i && predecessors.length < 3; j++) if (rng() < density && i - j <= 5) predecessors.push(`T${j + 1}`);
    tasks.push({ id: `T${i + 1}`, duration: randint(rng, 1, 6), predecessors });
  }
  const draft = { name: "", machines, deadline: 9999, tasks }, base = greedy(draft), optimumHint = makespan(base.schedule);
  const pressure = .78 + rng() * .47, deadline = Math.max(1, Math.round(optimumHint * pressure));
  return { name: `aleatoria-${String(seed).slice(-6)}`, seed, machines, deadline, density, tasks };
}

export function runAlgorithm(instance, algorithmId, seed = instance.seed ?? 42) {
  const rng = seededRandom(seed ^ 0x9e3779b9);
  const runners = { forca: bruteForce, backtracking, divisao: divideConquer, dp: dynamicProgramming, guloso: greedy, grasp: value => grasp(value, rng) };
  const result = runners[algorithmId](instance); const check = validateSchedule(instance, result.schedule);
  if (!check.valid) throw new Error(`Escala invalida: ${check.errors.join(", ")}`);
  return { ...result, makespan: makespan(result.schedule), instructions: result.metrics.states + result.metrics.branches + result.metrics.comparisons + result.metrics.prunes };
}
