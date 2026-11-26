"""MG模板本地编辑入口。仅监听本机，配置保存前先实际编译。"""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs,unquote
import argparse,copy,datetime,hashlib,importlib.util,json,mimetypes,re,subprocess,sys,threading,uuid,shutil
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('mg_build',ROOT/'构建.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
LOCK=threading.RLock();JOBS={}
TYPE_NAMES={'fade':'透明度','move':'分组移动','mask':'遮罩展开','state':'状态切换','style':'样式变化','bar':'进度条','draw':'线条描绘','wordFall':'分词落入','counter':'数字累计','typing':'逐字输入','wavefill':'波形填色','flip':'上下翻页','giant':'数字放大','tiles':'分块退场'}

def read_config():return json.loads((ROOT/'配置.json').read_text())
def write_json(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2))
def package_path(rel):
 p=(ROOT/rel).resolve()
 if not p.is_relative_to(ROOT):raise ValueError('请选择模板文件夹内的素材')
 return p
def stamp():return datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')

def metadata(c):
 result={}
 for sc in c['scenes']:
  soup=BeautifulSoup((ROOT/sc['template']).read_text(),'html.parser');nodes=builder.text_nodes(soup)
  fields=[]
  bound=[];module=sc.get('module',sc['id'])
  selectors={'开场':'#stats .meta b','账本':'.boardline b,.boardline>span:nth-of-type(2),#equation','末卡':'.end-word','写稿':'#summary','审片':'.review-extra'}.get(module)
  if module.startswith('章节'):selectors='*'
  if selectors:bound=soup.select(selectors)
  for action in sc.get('events',[]):
   if action['type'] in ['counter','typing'] or (action['type']=='state' and 'textContent' in action.get('values',{})):bound+=soup.select(action['target'])
  for i,n in enumerate(nodes):
   key=f'txt_{i:03d}';value=c['copy'][sc.get('copyKey',sc.get('module',sc['id']))][key]
   if not any(n.parent is e or e in n.parents for e in bound):fields.append(dict(key=key,label=value.strip()[:26] or '空白文字',tag=n.parent.name))
  media=[]
  for m in sc.get('media',[]):
   target=soup.select_one(m['target'])
   if target:target['src']=m['src']
  for i,el in enumerate(soup.select('video[src],img[src]')):
   rel=el['src'];media.append(dict(src=rel,label=Path(rel).stem,kind='视频' if el.name=='video' else '图片',id=el.get('id')))
  if any(w['start']<sc['visibleEnd'] and w['start']+w['duration']>sc['start'] for w in c.get('ambient_walls',[])):
   for i in range(4):media.append(dict(src=f'assets/ambient/clip-{i+1}.mp4',label=f'共享背景片段{i+1}',kind='视频',id=f'ambient-media-{i}'))
  targets=[]
  for e in soup.select('[id]'):
   if e.name in ['video','img','path','i','span']:continue
   text=' '.join(e.stripped_strings)[:24] or e['id']
   targets.append(dict(target='#'+e['id'],label=text))
  for selector,label in [('.title','主标题'),('.panel','内容面板'),('.media-slot','媒体窗口'),('.number','大数字'),('.body','说明文字')]:
   if soup.select(selector):targets.append(dict(target=selector,label=label))
  result[sc['id']]=dict(fields=fields,media=media,targets=targets,event_names=TYPE_NAMES)
 return result

def scene_config(c,index):
 """导出单个模块时搬移其所有媒体、字幕和背景，保留自身原速。"""
 c=copy.deepcopy(c);sc=c['scenes'][index];offset=sc['start'];end=sc['visibleEnd'];duration=end-offset
 sc.update(start=0,end=min(sc['end'],end)-offset,visibleEnd=duration)
 c['scenes']=[sc];c['canvas']['duration']=duration;c['audio']=None
 c['captions']=[dict(row,start=max(row['start'],offset)-offset,end=min(row['end'],end)-offset) for row in c['captions'] if row['end']>offset and row['start']<end]
 backgrounds=[]
 for row in c.get('backgrounds',[]):
  lo=max(offset,row['start']);hi=min(end,row['start']+row['duration'])
  if hi<=lo:continue
  row['source_offset']=lo-row['start'];row['start']=lo-offset;row['duration']=hi-lo;backgrounds.append(row)
 c['backgrounds']=backgrounds
 walls=[]
 for wall in c.get('ambient_walls',[]):
  lo=max(offset,wall['start']);hi=min(end,wall['start']+wall['duration'])
  if hi>lo:wall.update(media_offset=lo-wall['start'],start=lo-offset,duration=hi-lo);walls.append(wall)
 c['ambient_walls']=walls
 return c

def save_config(c):
 with LOCK:
  if any(not isinstance(v,(int,float)) or v<0 for v in c['data']['budget']['human']):raise ValueError('人工预算请填写非负数')
  if len(c['data']['budget']['human'])!=5:raise ValueError('完整流程需要五个人工预算数值')
  required={}
  for sc in c['scenes']:
   for media in sc.get('media',[]):required[media['src']]=max(required.get(media['src'],0),media['duration'])
  for wall in c.get('ambient_walls',[]):
   for i in range(4):
    rel=f'assets/ambient/clip-{i+1}.mp4';required[rel]=max(required.get(rel,0),wall['duration'])
  for old,new in c.get('assetOverrides',{}).items():
   if old in required and old!=new and Path(new).suffix.lower() in ['.mp4','.mov','.webm']:
    result=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(package_path(new))],capture_output=True,text=True,check=True)
    seconds=float(json.loads(result.stdout)['format']['duration'])
    if seconds+1/30<required[old]:raise ValueError(f'替换视频只有{seconds:.2f}秒，这个素材槽需要至少{required[old]:.2f}秒；请换足够长的原速素材')
  temp=ROOT/'编辑暂存.json';write_json(temp,c)
  try:builder.build(temp,ROOT/'编辑暂存.build')
  except Exception as e:raise ValueError('保存未完成：'+str(e)) from e
  backups=ROOT/'saved';backups.mkdir(exist_ok=True)
  (backups/(stamp()+'-配置.json')).write_bytes((ROOT/'配置.json').read_bytes())
  write_json(ROOT/'配置.json',c);builder.build(ROOT/'配置.json',ROOT/'index.html')
 return dict(ok=True,sha256=hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest())

def start_export(c,index=None):
 job_id=stamp();folder=ROOT/'exports'/job_id;folder.mkdir(parents=True)
 if index is not None:c=scene_config(c,index)
 workspace=folder/'project';workspace.mkdir()
 for name in ['命令.py','构建.py','基础CSS.css','精修CSS.css']:shutil.copy2(ROOT/name,workspace/name)
 for name in ['templates','runtime']:shutil.copytree(ROOT/name,workspace/name)
 # 渲染器不执行工程外的脚本；素材与GSAP一起复制进独立工程。
 shutil.copytree(ROOT/'assets',workspace/'assets')
 # 单模块只截取跨模块背景的实际原速时窗，不能把背景从头重播。
 for bg in c.get('backgrounds',[]):
  cut=bg.pop('source_offset',0)
  if cut>0:
   dest=ROOT/'assets/export-backgrounds'/f'{job_id}-{bg["id"]}.mp4';dest.parent.mkdir(exist_ok=True)
   subprocess.run(['ffmpeg','-nostdin','-v','error','-ss',str(cut),'-i',str(package_path(bg['src'])),'-t',str(bg['duration']),'-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(dest)],check=True)
   bg['src']=str(dest.relative_to(ROOT))
   output_asset=workspace/bg['src'];output_asset.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,output_asset)
 for wall in c.get('ambient_walls',[]):
  cut=wall.pop('media_offset',0)
  if cut>0:
   wall['phases']=[v*cut for v in wall['speeds']]
   for i in range(4):
    original=f'assets/ambient/clip-{i+1}.mp4';source=c.get('assetOverrides',{}).get(original,original)
    rel=f'assets/export-backgrounds/{job_id}-{wall["id"]}-{i}.mp4';dest=workspace/rel;dest.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(['ffmpeg','-nostdin','-v','error','-ss',str(cut),'-i',str(package_path(source)),'-t',str(wall['duration']),'-an','-c:v','libx264','-crf','20','-pix_fmt','yuv420p',str(dest)],check=True)
    c.setdefault('assetOverrides',{})[original]=rel
 cfg=workspace/'配置.json';write_json(cfg,c)
 name='整片' if index is None else c['scenes'][0]['id']
 argv=[sys.executable,str(workspace/'命令.py'),'render','--config',str(cfg),'--name',name]
 log=(folder/'导出.log').open('wb');proc=subprocess.Popen(argv,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 info=dict(id=job_id,pid=proc.pid,status='running',name=name,log=str((folder/'导出.log').relative_to(ROOT)),files=[])
 JOBS[job_id]=info;write_json(folder/'状态.json',info)
 def watch():
  code=proc.wait();log.close();info.update(exit_code=code,status='succeeded' if code==0 else 'failed')
  info['files']=[str(p.relative_to(ROOT)) for p in (workspace/'output').glob(name+'-*.mp4')]
  if code==0 and not info['files']:info.update(status='failed',error='命令退出但未找到本次MP4')
  write_json(folder/'状态.json',info)
 threading.Thread(target=watch,daemon=True).start();return info

class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def reply(self,obj,status=200):
  raw=json.dumps(obj,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
 def do_GET(self):
  url=urlparse(self.path)
  if url.path=='/api/config':
   c=read_config();return self.reply(dict(config=c,metadata=metadata(c)))
  if url.path=='/api/jobs':
   jobs=[]
   for p in sorted((ROOT/'exports').glob('*/状态.json'),reverse=True) if (ROOT/'exports').exists() else []:jobs.append(json.loads(p.read_text()))
   return self.reply(jobs[:12])
  if url.path=='/preview':
   html=(ROOT/'index.html').read_text().replace('</body>','<script src="editor/预览.js"></script></body>')
   raw=html.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(raw);return
  if url.path in ['/','/editor']:self.path='/editor/index.html'
  return super().do_GET()
 def do_POST(self):
  try:
   url=urlparse(self.path);raw=self.rfile.read(int(self.headers.get('Content-Length','0')))
   if url.path=='/api/upload':
    name=Path(unquote(self.headers.get('X-Filename','素材'))).name;ext=Path(name).suffix.lower()
    if ext not in ['.png','.jpg','.jpeg','.webp','.mp4','.mov','.webm','.wav','.mp3']:raise ValueError('请使用PNG/JPG/WebP、MP4/MOV/WebM或WAV/MP3')
    dest=ROOT/'assets/替换素材'/(stamp()+'-'+re.sub(r'[^\w.\-一-龥]','_',name));dest.parent.mkdir(exist_ok=True);dest.write_bytes(raw)
    return self.reply(dict(src=str(dest.relative_to(ROOT)),bytes=len(raw)))
   body=json.loads(raw or b'{}')
   if url.path=='/api/metadata':return self.reply(metadata(body['config']))
   if url.path=='/api/save':
    if any(v['status']=='running' for v in JOBS.values()):raise ValueError('正在导出，请完成后再保存，避免改动本次画面')
    return self.reply(save_config(body['config']))
   if url.path=='/api/export':
    if any(v['status']=='running' for v in JOBS.values()):raise ValueError('当前导出尚未结束，请查看导出记录')
    c=body['config'];save_config(c);return self.reply(start_export(c,body.get('index')))
   raise ValueError('没有这个操作')
  except Exception as e:self.reply(dict(error=str(e)),400)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--port',type=int,default=64066);a=ap.parse_args()
 builder.build(ROOT/'配置.json');server=ThreadingHTTPServer(('127.0.0.1',a.port),Handler)
 print('用系统Chrome打开：http://127.0.0.1:'+str(a.port)+'/editor',flush=True)
 server.serve_forever()
