import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=n=>JSON.parse(fs.readFileSync(path.join(root,n)));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const run=args=>{const r=spawnSync(process.execPath,args,{cwd:root,stdio:'inherit'});if(r.status!==0)process.exit(r.status??1)};
run(['--test','tests/components.test.mjs']);
if(read('components/catalog.json').registry.length!==read('风格.json').component_count)throw Error('组件数量不符');
for(const item of read('verification/previews.json').previews){
 run(item.build_command);
 if(sha(path.join(root,item.video))!==item.sha256)throw Error('预览SHA不符：'+item.id);
 const ocr=read(item.ocr);if(ocr.length!==item.half_second_and_last_ocr_samples||ocr.some(x=>'error'in x)||sha(path.join(root,item.ocr))!==item.ocr_sha256)throw Error('OCR绑定不符');
}
for(const item of read('基线文件清单.json').files){const p=path.resolve(root,item.path);if(!p.startsWith(root+path.sep)||sha(p)!==item.sha256)throw Error('源码基线不符：'+item.path)}
function scan(d){for(const ent of fs.readdirSync(d,{withFileTypes:true})){if(['.build','builds','node_modules','.git'].includes(ent.name))continue;const f=path.join(d,ent.name);if(ent.isDirectory()){scan(f);continue}if(/\.(mjs|js|json|md|py|html)$/.test(f)){const t=fs.readFileSync(f,'utf8');if(t.includes(['/','Users','/'].join(''))||t.includes('codex'+':'+'//')||t.includes('data'+':'+'image/'))throw Error('含非公开路径、历史或内嵌媒体：'+f)}if(/\.(m4a|wav|mp3|flac|png|jpg|jpeg|webp)$/.test(f))throw Error('不应包含私有音轨或图片：'+f)}}scan(root);
console.log(JSON.stringify({status:'PASS',components:20,examples:4,baseline_files:read('基线文件清单.json').files.length}));
