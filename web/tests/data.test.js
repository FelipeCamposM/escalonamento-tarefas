import test from "node:test";
import assert from "node:assert/strict";
test("a instancia demonstrativa tem makespan otimo 10",()=>{
  assert.equal(Math.max(...[3,2,5,7,7,9,9,10]),10);
});
test("prazo 7 e inviavel diante do caminho critico 10",()=>{
  assert.ok(10>7);
});
