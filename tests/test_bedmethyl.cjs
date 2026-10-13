const test = require("node:test");
const assert = require("node:assert/strict");
const {parse, toCSV} = require("../web/bedmethyl.js");
const row = (chrom,start,code,cov,modified,canonical,other=0)=>
  [chrom,start,start+1,code,cov,"+",start,start+1,"255,0,0",
   cov,(100*modified/cov).toFixed(2),modified,canonical,other,0,0,0,0].join("\t");

test("aggregation uses summed valid counts rather than average percentages",()=>{
  const r=parse([row("chr1",1,"m",10,6,4),row("chr1",2,"m",20,5,15)].join("\n"),{minimumCoverage:1});
  assert.equal(r.accepted,2);
  assert.equal(r.summary.length,1);
  assert.equal(r.summary[0].validCoverage,30);
  assert.equal(r.summary[0].modifiedCalls,11);
  assert.ok(Math.abs(r.summary[0].percentModified-36.66666667)<1e-6);
});
test("codes are never pooled, even for the same chromosome",()=>{
  const r=parse([row("chr1",1,"m",10,6,4),row("chr1",1,"h",10,1,9)].join("\n"),{modification:"all"});
  assert.equal(r.summary.length,2);
  assert.deepEqual(r.summary.map(x=>x.modification),["h","m"]);
});
test("coverage filter and invalid records are tracked",()=>{
  const r=parse([row("chr1",1,"m",2,1,1),"chr1\t1",row("chr2",9,"m",10,9,1)].join("\n"),{minimumCoverage:5});
  assert.equal(r.filtered,1);assert.equal(r.malformed,1);assert.equal(r.accepted,1);
});
test("rejects inconsistent counts and percentages",()=>{
  const bad=row("chr1",1,"m",10,5,5).replace("\t50.00\t","\t70.00\t");
  const badCount=row("chr1",2,"m",10,5,5).replace("\t5\t5\t0\t","\t7\t5\t0\t");
  const r=parse([bad,badCount].join("\n"));
  assert.equal(r.malformed,2);assert.equal(r.accepted,0);
});
test("invalid input and nonfinite settings fail",()=>{
  assert.throws(()=>parse("a",{minimumCoverage:NaN}));
  assert.throws(()=>parse("a",{minimumCoverage:0}));
  assert.throws(()=>parse("a",{modification:"x"}));
});
test("CSV exports protect untrusted spreadsheet cells",()=>{
  const csv=toCSV([{chromosome:"=HYPERLINK(1)",modification:"m",sites:1,validCoverage:4,modifiedCalls:2,percentModified:50}]);
  assert.ok(csv.includes("\"'=HYPERLINK(1)\""));
});
