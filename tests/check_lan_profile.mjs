// Run with Node.js; no browser, network or model requests are needed.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const html=fs.readFileSync(new URL('../lan_room.html',import.meta.url),'utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
class Element {
  constructor(tag='div') { this.tag=tag; this.children=[]; this.textContent=''; this.value=''; this.listeners={}; this.scrollTop=0; this.scrollHeight=200; this.clientHeight=100;
    this.classes=new Set(); this.classList={add:c=>this.classes.add(c)}; this.lastChild={textContent:''}; }
  append(...items){this.children.push(...items)}
  prepend(item){this.children.unshift(item)}
  replaceChildren(...items){this.children=items}
  setAttribute(key,value){this[key]=value}
  addEventListener(key,callback){this.listeners[key]=callback}
}
const elements=new Map();
const document={documentElement:{},getElementById:id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id)},
  createElement:tag=>new Element(tag),createTextNode:text=>({textContent:text})};
const storage={getItem:()=>null,setItem(){},removeItem(){}};
const context=vm.createContext({document,navigator:{language:'en-US'},location:{pathname:'/room/public-test'},
  localStorage:storage,sessionStorage:storage,setInterval(){},fetch(){throw Error('Unexpected network request')}});
new vm.Script(script).runInContext(context);
const state={name:'Fixture group',host_name:'Alice',you:'Guest',guests:[],members:['Fixture AI'],status:'就绪',messages:[
  {id:1,is_host:true,author:'讨论',body:'Original user message',time:'2026-11-11T12:34:00',avatar:'data:image/png;base64,iVBORw0KGgo='},
  {id:2,is_host:true,author:'Alice',body:'No external image fetch',time:'2026-11-11T12:35:00',avatar:'https://example.invalid/private.png'}]};
for(const language of ['zh-Hans','zh-Hant','en','ja','ko']){
  document.getElementById('language').value=language;
  document.getElementById('language').listeners.change();
  context.fixture=state;
  vm.runInContext('render(fixture)',context);
  const rows=document.getElementById('feed').children;
  assert.equal(rows.length,2);
  assert(!rows[0].classes.has('round'),'A host nickname matching a system role must remain a normal message');
  assert(rows[0].children[0].textContent.startsWith('讨论'),'Do not translate custom nicknames');
  assert.equal(rows[0].children[0].children[0].tag,'img');
  assert.equal(rows[0].children[1].textContent,'Original user message');
  assert.equal(rows[1].children[0].children.length,0,'External avatar URLs must be ignored');
  assert(document.getElementById('members').children[0].children.some(child=>child.textContent==='Alice'));
  document.getElementById('feed').replaceChildren();
  vm.runInContext('rendered=0',context);
}
export const result='PASS: LAN profile names and PNG avatars, no external avatar loads, preserved message text and custom names in all five languages.';
