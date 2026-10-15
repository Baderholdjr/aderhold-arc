// Runs collector/Code.gs against an in-memory fake of the Google Sheet (no Google account needed).
// Checks setup() migration and that each survey version writes the right columns.
// Run: node tests/collector.test.js
const fs = require('fs'), vm = require('vm'), assert = require('assert'), path = require('path');
const R = path.join(__dirname, '..', 'collector') + '/';
function Sheet(name, rows) { this.name = name; this.rows = rows || []; }
Sheet.prototype = { getName(){return this.name}, setName(n){this.name=n}, getLastRow(){return this.rows.length}, getLastColumn(){return this.rows[0]?this.rows[0].length:0},
  appendRow(v){this.rows.push(v.slice())}, getDataRange(){const s=this;return{getValues(){return s.rows.map(r=>r.slice())}}},
  getRange(r,c,nr,nc){const s=this;nr=nr||1;nc=nc||1;return{getValues(){const o=[];for(let i=0;i<nr;i++){o.push([]);for(let j=0;j<nc;j++)o[i].push((s.rows[r-1+i]||[])[c-1+j]??'')}return o},
    setValues(v){v.forEach((row,i)=>{s.rows[r-1+i]=s.rows[r-1+i]||[];row.forEach((x,j)=>s.rows[r-1+i][c-1+j]=x)});return this},setValue(x){return this.setValues([[x]])},
    setFontWeight(){return this},setBackground(){return this},setNumberFormat(){return this},setDataValidation(){return this}}},
  setFrozenRows(){}, autoResizeColumns(){}, clear(){this.rows=[]}, hideSheet(){}, protect(){return{setDescription(){return this},setWarningOnly(){return this}}}, setColumnWidth(){}, getMaxColumns(){return 100}};
const sheets = [new Sheet('Responses', [['response_id','campaign','submitted_date','role'], ['x','OLD','2026-10-01','IC']]),
                new Sheet('Campaigns', [['code','display_name','active','notes'], ['ACME-1','Acme','TRUE',''], ['TEST-0001','Test','TRUE','']])];
const ss = { getName(){return 'test'}, getSheets(){return sheets}, getSheetByName(n){return sheets.find(s=>s.name===n)||null},
  insertSheet(n){const s=new Sheet(n);sheets.push(s);return s}, setActiveSheet(){} };
const logs=[]; const g = { console, Logger:{log:m=>logs.push(m)}, SpreadsheetApp:{getActiveSpreadsheet:()=>ss, newDataValidation(){const o={requireCheckbox(){return o},requireValueInList(){return o},setAllowInvalid(){return o},build(){return o}};return o}},
  Utilities:{getUuid:()=>'uuid-'+Math.random().toString(36).slice(2,8), formatDate:()=> '2026-10-14'}, LockService:{getScriptLock:()=>({waitLock(){},tryLock(){return true},releaseLock(){}})},
  ScriptApp:{getService:()=>({getUrl:()=> 'https://script.google.com/macros/s/X/exec'})}, HtmlService:{} };
vm.createContext(g); vm.runInContext(fs.readFileSync(R+'Items.gs','utf8')+'\n'+fs.readFileSync(R+'Code.gs','utf8'), g);
g.setup(); g.setup();
const hdr = ss.getSheetByName('Responses').rows[0];
const all = {}; ['A','R','C','F'].forEach(p=>{for(let d=1;d<=4;d++)for(let i=1;i<=4;i++)all[p+d+'.'+i]='4'});
for (let m=1;m<=12;m++) all['X.M'+m]='1'; for (let i=1;i<=5;i++) all['P'+i]='-1'; for (let i=1;i<=6;i++) all['L'+i]='5'; all.L7='2'; all.role='IC'; all.use_freq='3';
const expect = {
  'TEST-0001': { wave: 'T1', audience: 'staff', role: 'IC', X: [], P: false, L: false },
  'TEST-LEAD': { wave: 'T1', audience: 'leader', role: 'LEAD', X: [], P: false, L: true },
  'TEST-T2': { wave: 'T2', audience: 'staff', role: 'IC', X: ['X.M3', 'X.M6', 'X.M7'], P: false, L: false },
  'TEST-T3': { wave: 'T3', audience: 'staff', role: 'IC', X: ['X.M3', 'X.M6', 'X.M7'], P: true, L: false },
};
assert.ok(ss.getSheetByName('Responses (earlier version)'), 'old responses kept in a renamed tab');
assert.strictEqual(ss.getSheetByName('Campaigns').rows.filter(r => /^TEST-/.test(r[0])).length, 4, 'test campaigns added once');
assert.deepStrictEqual(ss.getSheetByName('Campaigns').rows[0].slice(4), ['engagement', 'wave', 'audience', 'modules']);
assert.deepStrictEqual(ss.getSheetByName('Campaigns').rows[2].slice(4, 7), ['TEST', 'T1', 'staff'], 'old TEST-0001 row filled in');
assert.deepStrictEqual(ss.getSheetByName('Campaigns').rows[1].slice(4), [], 'client rows untouched');
for (const code of Object.keys(expect)) {
  g.submitResponse({ campaign: code, consentResearch: true, answers: Object.assign({}, all), website: '' });
  const row = ss.getSheetByName('Responses').rows.slice(-1)[0]; const o = {}; hdr.forEach((h, i) => o[h] = row[i]);
  const e = expect[code];
  assert.strictEqual(o.wave, e.wave, code); assert.strictEqual(o.audience, e.audience, code); assert.strictEqual(o.role, e.role, code);
  assert.strictEqual(o.engagement, 'TEST', code); assert.strictEqual(o['A1.1'], 4, code);
  assert.deepStrictEqual(Object.keys(o).filter(k => /^X\./.test(k) && o[k] !== '' && o[k] != null), e.X, code);
  assert.strictEqual(o.P1 === -1, e.P, code + ' P items'); assert.strictEqual(o.L1 === 5, e.L, code + ' L items');
  console.log('ok', code);
}
assert.throws(() => g.submitResponse({ campaign: 'NOPE', answers: {}, website: '' }), /not active/);
console.log('collector tests passed');
