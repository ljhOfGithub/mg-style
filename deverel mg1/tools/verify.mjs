import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p)));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
function run(args){const result=spawnSync(process.execPath,args,{cwd:root,stdio:'inherit'});if(result.status!==0)process.exit(result.status??1);}
run(['--test','tests/components.test.mjs']);
const meta=read('风格.json'),catalog=read('components/catalog.json');
if(catalog.components.length!==meta.component_count)throw Error('组件目录数量不符');
for(const preview of read('verification/previews.json').previews){
 const c=read(preview.config);if(c.media.length)throw Error('公开示例不得依赖参考片媒体');
 run(['tools/build.mjs','--config',preview.config,'--out','.build/'+preview.id]);
 if(sha(path.join(root,preview.video))!==preview.sha256)throw Error('预览哈希不符');
 const ocr=read(preview.ocr);if(ocr.length!==preview.half_second_and_last_ocr_samples||ocr.some(x=>'error'in x))throw Error('预览OCR绑定不符');
}
const manifest=read('基线文件清单.json');
for(const entry of manifest.files){const p=path.resolve(root,entry.path);if(!p.startsWith(root+path.sep)||sha(p)!==entry.sha256)throw Error('源码基线不符：'+entry.path);}
console.log(JSON.stringify({status:'PASS',components:catalog.components.length,examples:3,baseline_files:manifest.files.length}));
