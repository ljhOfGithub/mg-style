"""运行真实本地HTTP处理器，验证读配置、保存、错误回滚与上传；不执行视频渲染。"""
from pathlib import Path
import importlib.util,tempfile,threading,urllib.request,urllib.error,json,base64,copy
from urllib.parse import quote
R=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('editor_http_test',R/'编辑器.py');e=importlib.util.module_from_spec(s);s.loader.exec_module(e)
with tempfile.TemporaryDirectory(prefix='mg-editor-http-') as folder:
 root=Path(folder).resolve()
 for name in ['模板','runtime','编辑器']:(root/name).symlink_to(R/name,target_is_directory=True)
 for name in ['配置.json','基础CSS.css','精修CSS.css']:(root/name).write_bytes((R/name).read_bytes())
 (root/'assets').mkdir()
 for x in (R/'assets').iterdir():
  if x.name not in ['替换素材','导出背景']:(root/'assets'/x.name).symlink_to(x,target_is_directory=x.is_dir())
 e.ROOT=root;e.builder.ROOT=root;e.builder.build(root/'配置.json',root/'index.html')
 server=e.ThreadingHTTPServer(('127.0.0.1',0),e.Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base='http://127.0.0.1:'+str(server.server_port)
 def req(path,body=None,headers=None):
  if isinstance(body,dict):body=json.dumps(body,ensure_ascii=False).encode();headers={'Content-Type':'application/json'}
  with urllib.request.urlopen(urllib.request.Request(base+quote(path,safe='/%?=&'),data=body,headers=headers or {})) as r:return r.read()
 j=json.loads(req('/api/config'));assert len(j['config']['scenes'])==23 and len(j['metadata'])==23
 assert 'fred mg 1' in req('/editor').decode() and 'editor/预览.js' in req('/preview').decode()
 c=copy.deepcopy(j['config']);c['copy']['开场']['txt_000']='真实接口替换测试';json.loads(req('/api/save',{'config':c}));assert '真实接口替换测试' in req('/preview').decode()
 saved=(root/'配置.json').read_bytes();bad=copy.deepcopy(c);bad['data']['budget']['human'][0]=-1
 try:req('/api/save',{'config':bad})
 except urllib.error.HTTPError as err:assert err.code==400 and '非负数' in err.read().decode()
 else:raise AssertionError('错误配置保存成功')
 assert (root/'配置.json').read_bytes()==saved
 # 本地图片实际写入、下载与界面素材替换路径一致。
 data=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a5TcAAAAASUVORK5CYII=')
 uploaded=json.loads(req('/api/upload',data,{'X-Filename':'replacement.png'}));assert req('/'+uploaded['src'])==data
 c['assetOverrides']['assets/placeholders/image.svg']=uploaded['src'];req('/api/save',{'config':c});assert uploaded['src'] in req('/preview').decode()
 server.shutdown();thread.join()
print('PASS actual HTTP config, editor page, preview, save/reload, rejected save rollback, upload and media replacement')
