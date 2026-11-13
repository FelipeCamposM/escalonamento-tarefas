import test from "node:test";
import assert from "node:assert/strict";
import { generateRandomInstance, lowerBound, runAlgorithm, validateSchedule } from "../scheduler-live.js";

const small={name:"teste",seed:42,machines:2,deadline:20,tasks:[
  {id:"A",duration:3,predecessors:[]},{id:"B",duration:2,predecessors:[]},
  {id:"C",duration:4,predecessors:["A"]},{id:"D",duration:2,predecessors:["A"]},
  {id:"E",duration:1,predecessors:["B","C","D"]}
]};

test("gerador e deterministico por semente e varia entre sementes",()=>{
  assert.deepEqual(generateRandomInstance("guloso",123),generateRandomInstance("guloso",123));
  assert.notDeepEqual(generateRandomInstance("guloso",123),generateRandomInstance("guloso",124));
});

test("os seis algoritmos produzem escalas validas",()=>{
  for(const algorithm of ["forca","backtracking","divisao","dp","guloso","grasp"]){
    const result=runAlgorithm(small,algorithm,42);
    assert.equal(validateSchedule(small,result.schedule).valid,true,algorithm);
  }
});

test("metodos exatos concordam na instancia pequena",()=>{
  const values=["forca","backtracking","dp"].map(id=>runAlgorithm(small,id,42).makespan);
  assert.equal(new Set(values).size,1);
});

test("limite inferior nunca supera o otimo exato",()=>{
  assert.ok(lowerBound(small)<=runAlgorithm(small,"dp",42).makespan);
});
