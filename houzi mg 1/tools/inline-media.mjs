import fs from'node:fs';
import path from'node:path';
import{createHash}from'node:crypto';
/** Embed original image bytes without changing the source file or crop contract.
 * SVG paint resources must not depend on compiler/worker-local currentSrc URLs. */
export function embedMedia(c,root){
 const types={'.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp','.gif':'image/gif','.svg':'image/svg+xml'};
 for(const m of Object.values(c.media||{}))for(const part of m.parts){
  const mime=types[path.extname(part.file).toLowerCase()];
  if(!mime)throw Error('Unsupported static media type: '+part.file);
  const bytes=fs.readFileSync(path.resolve(root,part.file));
  part.paintUrl=`data:${mime};base64,${bytes.toString('base64')}`;
  part.paintSha256=createHash('sha256').update(bytes).digest('hex');
 }
 return c;
}
