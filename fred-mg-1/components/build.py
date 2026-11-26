"""导出独立fred MG组件；只读取所选组件预设，不依赖整片配置。"""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,math,re,shutil,subprocess
ROOT=Path(__file__).resolve().parent
CATALOG=json.loads((ROOT/'catalog.json').read_text())['components'];REGISTRY={x['id']:x for x in CATALOG}
def load(p):return json.loads(Path(p).read_text())
def safe_media(root,relative):
 if not isinstance(relative,str) or Path(relative).is_absolute():raise ValueError('素材请填写媒体根目录内的相对路径')
 p=(Path(root)/relative).resolve()
 if not p.is_relative_to(Path(root).resolve()) or not p.is_file():raise ValueError('素材不存在或超出媒体根目录：'+relative)
 if p.suffix.lower() not in ['.svg','.png','.jpg','.jpeg','.webp','.mp4','.webm','.mov']:raise ValueError('素材仅支持图片或视频')
 return p

def validate(spec):
 if not isinstance(spec,dict) or set(spec)-{'format','component','duration','content','data','media','theme','motions'}:raise ValueError('配置存在不支持的字段')
 if spec.get('format','fred-component@1')!='fred-component@1' or spec.get('component') not in REGISTRY:raise ValueError('请选择catalog.json内的组件ID')
 record=REGISTRY[spec['component']];dur=spec.get('duration',record['duration'])
 if type(dur) not in [int,float] or not math.isfinite(dur) or not record['duration']-1e-6<=dur<=30 or abs(dur*30-round(dur*30))>1e-5:raise ValueError(f'时长须在{record["duration"]:.3f}至30秒，并按1/30秒对齐；不能截断原动作')
 for key in ['content','data','media','theme','motions']:
  if not isinstance(spec.get(key,{}),dict):raise ValueError(key+'须为对象')
 fields={x['key']:x for x in record['fields']}
 if set(spec.get('content',{}))-set(fields):raise ValueError('文字字段不在当前组件的可编辑列表内；数据驱动字段请使用data')
 base=load(ROOT/'presets'/(record['id']+'.json'))
 for k,v in spec.get('content',{}).items():
  default=base['copy'][record['name']][k];limit=fields[k].get('max_length',max(12,len(default.strip())+6))
  if not isinstance(v,str) or not v.strip() or len(v)>limit:raise ValueError(f'{k}须为1至{limit}字，不自动截字')
 if set(spec.get('data',{}))-set(record['data_fields']):raise ValueError('data存在当前组件不使用的字段')
 if set(spec.get('media',{}))-set(record['media']):raise ValueError('媒体插槽不存在')
 for k,v in spec.get('theme',{}).items():
  if k not in base['theme'] or not isinstance(v,str) or not re.fullmatch('#[0-9a-fA-F]{6}',v):raise ValueError('主题使用现有颜色字段和六位十六进制色值')
 actions={e['id']:e for e in base['scenes'][0]['events']}
 for k,v in spec.get('motions',{}).items():
  if k not in actions or not isinstance(v,dict) or set(v)-{'at','duration'}:raise ValueError('动作只接受已登记ID与at/duration')
  if any(type(n) not in [int,float] or not math.isfinite(n) or n<0 for n in v.values()):raise ValueError('动作时间须为非负有限数值')
  if 'duration' in v and (actions[k].get('binding','').startswith('data.wall.') or actions[k].get('knots')):raise ValueError('此动作时长由视频墙绑定或变化节点控制，不能用duration覆盖')
  if 'duration' in v and v['duration']==0 and actions[k]['type']!='state':raise ValueError('连续动作时长须大于0')
 return record,dur

def build(spec,output,media_root=None):
 record,dur=validate(spec);out=Path(output).resolve();out.mkdir(parents=True,exist_ok=True)
 if out==ROOT or ROOT.is_relative_to(out):raise ValueError('输出目录不能覆盖组件源码')
 cfg=load(ROOT/'presets'/(record['id']+'.json'));sc=cfg['scenes'][0];base=record['duration'];delta=dur-base
 cfg['canvas']['duration']=dur;sc.update(end=dur,visibleEnd=dur)
 cfg['copy'][record['name']].update(spec.get('content',{}));cfg['theme'].update(spec.get('theme',{}))
 for k,v in spec.get('data',{}).items():
  if k=='chapter':
   required=set(record['data_fields']['chapter'])
   if not isinstance(v,dict) or set(v)!=required or not isinstance(v.get('number'),str) or not re.fullmatch(r'\d{2}',v['number']):raise ValueError('章节参数须使用catalog登记的字段与两位number')
   if 'title' in v and (not isinstance(v['title'],str) or not 1<=len(v['title'])<=8):raise ValueError('章节title须为1至8字')
   if 'groups' in v and (not isinstance(v['groups'],list) or len(v['groups'])!=2 or any(not isinstance(t,str) or not t or len(t)>6 for t in v['groups'])):raise ValueError('章节groups须为两个1至6字短句，总共不超过9字')
   if 'groups' in v and sum(map(len,v['groups']))>9:raise ValueError('章节两组文字总共不能超过9字')
   cfg['data']['chapters'][int(record['name'][-2:])-1].update(copy.deepcopy(v))
  elif k=='budget':
   required=set(record['data_fields']['budget'])
   if not isinstance(v,dict) or set(v)!=required or not isinstance(v.get('human'),list) or len(v['human'])!=5 or any(type(x) not in [int,float] or not math.isfinite(x) or x<0 or x>999 for x in v['human']):raise ValueError('预算须使用catalog登记的字段与5个非负human数值')
   if 'ai_labels' in v and (not isinstance(v['ai_labels'],list) or len(v['ai_labels'])!=5 or any(not isinstance(x,str) or len(x)>16 for x in v['ai_labels'])):raise ValueError('ai_labels须为5个短标签')
   if 'human_bar_px_per_minute' in v and (type(v['human_bar_px_per_minute']) not in [int,float] or not 0<v['human_bar_px_per_minute']<=30):raise ValueError('条宽须大于0且不超过30')
   cfg['data']['budget'].update(copy.deepcopy(v))
  elif k=='ending':
   if not isinstance(v,list) or len(v)!=len(cfg['data']['ending']) or any(not isinstance(row,list) or len(row)!=len(cfg['data']['ending'][j]) or any(not isinstance(x,str) or not x or len(x)>10 for x in row) for j,row in enumerate(v)) or sum(len(x) for row in v for x in row)>40:raise ValueError('末卡保持原行/组数，总共不超过40字，每组1至10字')
   cfg['data']['ending']=copy.deepcopy(v)
  elif k.startswith('state:'):
   if not isinstance(v,str) or len(v)>24:raise ValueError('状态文字最多24字')
   next(e for e in sc['events'] if e['id']==k[6:])['values']['textContent']=v
  else:
   if not isinstance(v,str) or not v.strip() or len(v)>(100 if k=='prompt' else 48):raise ValueError('提示词最多100字，摘要最多48字')
   cfg['data'][k]=v
 for e in sc['events']:
  if e['id'] in record['tail_events']:e['at']+=delta
  if e.get('binding','').startswith('data.wall.row.'):e['duration']=dur
  e.update(spec.get('motions',{}).get(e['id'],{}))
  if e['at']+e.get('duration',0)>dur+1e-5:raise ValueError('动作时窗超出组件总长：'+e['id'])
 for m in sc.get('media',[]):
  if not m.get('tailPoster') and -.04<=base-m['at']-m['duration']<=max(.6,sc.get('fadeOut',0))+1/30:m['duration']=dur-m['at']
  if m.get('tailUntil') is not None and abs(m['tailUntil']-base)<.05:m['tailUntil']+=delta
  m['duration']=min(m['duration'],dur-m['at'])
 for group in ['backgrounds','ambient_walls']:
  for m in cfg[group]:
   if abs(m['start']+m['duration']-base)<.05:m['duration']+=delta
 # 只复制本组件会使用的资源；复制后的文件有独立inode，不污染输入。
 shared=ROOT/'shared';overrides={};sources={};media_root=Path(media_root or shared)
 for slot,info in record['media'].items():
  source=safe_media(media_root,spec['media'][slot]) if slot in spec.get('media',{}) else safe_media(shared,info['default'])
  kind='video' if source.suffix.lower() in ['.mp4','.mov','.webm'] else 'image'
  if kind!=info['kind']:raise ValueError(slot+'须使用'+info['kind']+'素材，不能把视频写入图片标签')
  name=hashlib.sha256(source.read_bytes()).hexdigest()[:16]+source.suffix.lower();rel='assets/media/'+name;dest=out/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);overrides[info['source']]=rel;sources[rel]=source
 cfg['assetOverrides']=overrides
 for m in sc.get('media',[]):
  m['src']=overrides.get(m['src'],m['src'])
  for k in ['leadPoster','tailPoster']:
   if m.get(k):m[k]=overrides.get(m[k],m[k])
 for m in cfg['backgrounds']:m['src']=overrides.get(m['src'],m['src'])
 for source,dest in [(ROOT/'modules'/(record['id']+'.tpl'),out/sc['template']),(ROOT/'runtime.py',out/'runtime.py'),(shared/'base.css',out/'base.css'),(shared/'refinements.css',out/'refinements.css')]:dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
 for folder in ['fonts','vendor','runtime']:shutil.copytree(shared/'assets'/folder,out/'assets'/folder,dirs_exist_ok=True)
 (out/'config.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
 module_spec=importlib.util.spec_from_file_location('fred_export_runtime',out/'runtime.py');runtime=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(runtime);runtime.rebuild(out)
 # 按真实元素数计入stagger，拒绝截断动作；不是只校验duration字段。
 from bs4 import BeautifulSoup
 soup=BeautifulSoup((out/'compositions/component.html').read_text(),'html.parser')
 for e in sc['events']:
  selector=e['target'];count=len(soup.select(selector.replace('#','[data-mg-id="',1)+'"]')) if selector.startswith('#') and ',' not in selector and ' ' not in selector else None
  if count is None:
   converted=re.sub(r'#([\w\u3400-\u9fff-]+)',r'[data-mg-id="\1"]',selector);count=len(soup.select(converted))
  actual=e.get('duration',0)+max(0,count-1)*e.get('stagger',0)
  if e['at']+actual>dur+1e-5:raise ValueError('动作及交错时窗超出组件长度：'+e['id'])
 probes={}
 for el in soup.select('video[src]'):
  src=out/el['src'];offset=float(el.get('data-media-start',0));length=float(el.get('data-duration',dur))
  if src not in probes:probes[src]=float(json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(src)]))['format']['duration'])
  available=probes[src]
  if available+1/30<offset+length:raise ValueError('视频长度不足原速播放时窗：'+el['src'])
 (out/'build.py').write_text('from pathlib import Path\nfrom runtime import rebuild\nrebuild(Path(__file__).resolve().parent)\n')
 for name in ['LICENSE','LICENSE-MG-styles-15.txt']:shutil.copyfile(shared/name,out/name)
 (out/'requirements.txt').write_text('beautifulsoup4==4.14.3\n')
 (out/'hyperframes.json').write_text(json.dumps({'width':1920,'height':1080,'fps':30},indent=2)+'\n')
 (out/'package.json').write_text(json.dumps({'private':True,'scripts':{'build':'python3 build.py'}},indent=2)+'\n')
 (out/'spec.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
 return {'component':record['id'],'duration':dur,'frames':round(dur*30),'events':len(sc['events']),'scene_count':1}

if __name__=='__main__':
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--component',choices=REGISTRY);a.add_argument('--config',type=Path);a.add_argument('--duration',type=float);a.add_argument('--media-root',type=Path);a.add_argument('--output',type=Path,required=True);o=a.parse_args();s=load(o.config) if o.config else {'format':'fred-component@1','component':o.component}
 if o.duration is not None:s['duration']=o.duration
 print(json.dumps(build(s,o.output,o.media_root),ensure_ascii=False,indent=2))
