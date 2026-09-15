'use strict';
const {test}=require('node:test'),fs=require('node:fs'),vm=require('node:vm');
test('all shipped JavaScript parses, including the DOM-only editor',()=>{
 for(const name of fs.readdirSync('src').filter(n=>n.endsWith('.js')))new vm.Script(fs.readFileSync('src/'+name,'utf8'),{filename:name});
});
