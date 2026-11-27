/** Explicit reusable binding wins; retain the existing source-ID fallback. */
export function componentMediaKey(component,media){if(component.mediaKey!=null){if(!Object.hasOwn(media,component.mediaKey))throw Error('组件mediaKey不存在：'+component.mediaKey);return component.mediaKey;}return Object.keys(media).find(k=>component.id.includes(k==='create'?'s03':k==='publish'?'s04':'s05'));}
