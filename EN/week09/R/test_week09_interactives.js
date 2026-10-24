// Simulated DOM smoke-test of SVG lab code; no browser dependencies.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const qmd=fs.readFileSync(__dirname+'/../week09/week09.qmd','utf8');
const code=qmd.split('<script>\n')[1].split('\n</script>')[0];
const ids=[...qmd.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
const controls={oddsP:50,logB0:-2.3,logB1:.34,logB2:.68,logB3:.26};
const elements={};
for(const id of ids)elements[id]={id,value:controls[id]??'',textContent:'',innerHTML:'',listeners:{},addEventListener(name,fn){this.listeners[name]=fn;}};
const document={readyState:'complete',getElementById:id=>elements[id]||null,querySelectorAll:()=>[]};
const window={addEventListener(){}};
vm.runInNewContext(code,{window,document,Math,Number,Array,String,console});
function testP(p){elements.oddsP.value=p;elements.oddsP.listeners.input();assert(!/NaN|undefined/.test(elements.oddsSvg.innerHTML),`bad svg odds p=${p}`);assert(elements.oddsSvg.innerHTML.includes('circle'));}
[0,1,10,20,50,80,99,100].forEach(testP);
assert.equal(elements.oddsOddsOut.textContent,'∞');assert.equal(elements.oddsLogitOut.textContent,'+∞');
function testBetas(b0,b1,b2,b3){Object.entries({logB0:b0,logB1:b1,logB2:b2,logB3:b3}).forEach(([k,v])=>elements[k].value=v);elements.logB3.listeners.input();assert(!/NaN|undefined|Infinity/.test(elements.logisticSvg.innerHTML),'bad logistic SVG');assert(elements.logisticSvg.innerHTML.includes('w9-smoker-line'));}
[[-2.3,.34,.68,.26],[-4,-.6,-2,-.8],[0,1.2,2,.8],[-2,0,0,0]].forEach(args=>testBetas(...args));
assert.equal(elements.logOrNon.textContent,'1.00');assert.equal(elements.logRatio.textContent,'1.00');
console.log('PASS: odds endpoints; live readouts; logistic slope/interactions; SVG finite; init once');
