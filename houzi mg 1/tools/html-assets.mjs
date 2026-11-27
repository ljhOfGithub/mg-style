export const escape=s=>String(s).replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;');
/** Give every reusable media group a permanent SVG identity. Parts remain separate;
 * no source holes are filled and no labels or frames are baked into a bitmap. */
export function bindMediaIds(c){let i=0;for(const[key,m]of Object.entries(c.media||{})){m.svgAssetId=`mg-media-${key.replace(/[^a-zA-Z0-9_-]/g,'-')}-${i++}`;}return c;}
export function svgAssetDefs(c){return `<defs id="mg-asset-definitions">`+Object.entries(c.media||{}).map(([key,m])=>{if(!m.svgAssetId)throw Error('bindMediaIds must precede svgAssetDefs');return `<g id="${escape(m.svgAssetId)}" data-mg-media-key="${escape(key)}"><rect width="${m.width}" height="${m.height}" fill="#fff"/>`+m.parts.map((p,i)=>`<image id="${escape(m.svgAssetId)}-part-${i}" data-mg-asset="${escape(p.file)}" href="${escape(p.file)}" x="${p.rect[0]}" y="${p.rect[1]}" width="${p.rect[2]}" height="${p.rect[3]}"/>`).join('')+`</g>`;}).join('')+`</defs>`;}
export function assetPreloads(c){const files=[...new Set(Object.values(c.media||{}).flatMap(m=>m.parts.map(p=>p.file)))];return `<div id="mg-assets" style="display:none">`+files.map((file,i)=>`<img id="mg-image-${i}" data-layout-ignore data-asset="${escape(file)}" src="${escape(file)}" alt="">`).join('')+`</div>`;}

/** Mount persistent SVG paint nodes at runtime, outside the seek-updated layer. */
export const svgAssetMount=()=>`<defs id="mg-asset-definitions"></defs><g id="mg-dynamic-art"></g>`;
