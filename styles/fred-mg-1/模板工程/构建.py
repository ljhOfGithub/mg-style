"""从配置、版式与动作库构建完整Hyperframes工程，不依赖原制作目录。"""
from pathlib import Path
import argparse,json,re,hashlib,copy
from bs4 import BeautifulSoup,NavigableString
ROOT=Path(__file__).resolve().parent

def text_nodes(s):return [t for t in s.find_all(string=True) if isinstance(t,NavigableString) and t.strip() and t.parent.name not in ['style','script']]
def namespaced(s,prefix):
 for e in s.select('[id]'):
  name=e['id'];e['data-mg-id']=name;e['id']=prefix+'-'+name

def build(config_path,out=None):
 c=json.loads(Path(config_path).read_text());c=copy.deepcopy(c);total=sum(c['data']['budget']['human']);W=c['canvas']['width'];H=c['canvas']['height'];duration=c['canvas']['duration'];fps=c['canvas']['fps']
 assert W==1920 and H==1080 and fps==30,'当前模板固定1920×1080/30fps；不能拉伸已批媒体'
 assert 0<duration<=600
 bodies=[];all_events=[];previous=-1;style_ids=set()
 for i,sc in enumerate(c['scenes']):
  module=sc.get('module',sc['id']);copy_key=sc.get('copyKey',module);sc['domId']='scene-'+str(i)
  assert sc['start']>=0 and sc['start']<sc['end']<=duration+1e-5 and sc['start']>=previous,sc['id'];previous=sc['start']
  s=BeautifulSoup((ROOT/sc['template']).read_text(),'html.parser')
  ns=text_nodes(s);values=c['copy'][copy_key]
  assert len(ns)==len(values),(sc['id'],'文字槽数量变化，请同步copy')
  for j,node in enumerate(ns):node.replace_with(values[f'txt_{j:03d}'])
  for media in sc.get('media',[]):
   target=s.select_one(media['target']);assert target is not None,media['target'];target['src']=media['src'];target['data-start']=str(sc['start']+media['at']);target['data-duration']=str(media['duration'])
   if media.get('leadPoster'):
    poster=s.new_tag('img',attrs={'src':media['leadPoster'],'class':'clip','id':target['id']+'-lead','data-start':str(sc['start']+media['leadFrom']),'data-duration':str(media['at']-media['leadFrom']),'data-track-index':'3','style':target.get('style','')});target.insert_before(poster)
   if media.get('tailPoster'):
    poster=s.new_tag('img',attrs={'src':media['tailPoster'],'class':'clip','id':target['id']+'-tail','data-start':str(sc['start']+media['at']+media['duration']),'data-duration':str(media['tailUntil']-media['at']-media['duration']),'data-track-index':'3','style':target.get('style','')});target.insert_after(poster)
  if module=='发布' and c['data'].get('phone_has_embedded_check',False):
   s.select_one('#publish-check').decompose();sc['events']=[e for e in sc['events'] if e['target']!='#publish-check']
  if module=='开场':
   for element,value in zip(s.select('#stats .meta b'),[c['data']['budget']['human'][j] for j in [0,3,4]]):element.string=str(value)+'分钟'
   wall=c['data'].get('wall')
   if wall:
    s.select_one('#wall')['style']=f"position:absolute;inset:0;opacity:{wall['opacity']};transform-origin:50% 50%"
    s.select_one('#wall-plane')['style']=f"position:absolute;left:{wall['left']}px;top:{wall['top']}px;width:{wall['plane_width']}px;height:{wall['plane_height']}px;transform-origin:50% 50%;transform:perspective({wall['perspective']}px) rotateX({wall['tilt_x']}deg) rotateZ({wall['tilt_z']}deg);transform-style:preserve-3d"
    for action in sc['events']:
     if action.get('binding')=='data.wall.camera':action.update(duration=wall['camera_duration'],to={'scale':wall['end_scale']})
     if action.get('binding','').startswith('data.wall.row.'):
      n=int(action['binding'].split('.')[-1]);phase=wall['phases'][n];action.update(duration=sc['visibleEnd']-sc['start'],**{'from':{'x':phase},'to':{'x':phase+wall['speeds'][n]*(sc['visibleEnd']-sc['start'])}})
  if module=='账本':
   for j,row in enumerate(s.select('.boardline')):
    human=c['data']['budget']['human'][j];label=row.select_one('b');text=next(t for t in label.find_all(string=True) if t.strip());value_node=s.new_tag('span',attrs={'class':'human-value'});value_node.string=str(human)+'分钟';text.replace_with(value_node)
    unit_width=min(c['data']['budget']['human_bar_px_per_minute'],130/max(1,max(c['data']['budget']['human'])))
    row.select_one('#humanbar-'+str(j))['style']=row.select_one('#humanbar-'+str(j)).get('style','')+';width:'+str(human*unit_width)+'px'
    row.select(':scope > span')[1].string='AI '+c['data']['budget']['ai_labels'][j]
   e=s.select_one('#equation');e.clear();e.append(' + '.join(map(str,c['data']['budget']['human']))+' = '+str(total)+'分钟')
  if module=='末卡':
   for line,groups in zip(s.select('.end-word'),c['data']['ending']):
    line.clear()
    for j,text in enumerate(groups):
     group=s.new_tag('span',attrs={'class':'end-group','style':'display:inline-block'})
     if c['data'].get('ending_granularity')=='character':
      for ch in text:
       char=s.new_tag('span',attrs={'class':'end-char','style':'display:inline-block'});char.string=ch;group.append(char)
     else:group.string=text
     line.append(group)
  if module=='写稿':s.select_one('#summary').string=c['data']['prompt_summary']
  if module.startswith('章节'):
   n=int(module[-2:])-1;ch=c['data']['chapters'][n]
   for selector in ['#ch-number','#new-num','#ch-circle']:
    e=s.select_one(selector)
    if e:e.string=ch['number'][-1] if module=='章节01' else ch['number']
   if module=='章节01':s.select_one('#flip-tens').string=ch['number'][:-1] or '0'
   for selector in ['#flip-back-top','#flip-in']:
    e=s.select_one(selector)
    if e:e.string=ch['number'][-1] if module=='章节01' else ch['number']
   e=s.select_one('#ch-title')
   if e and sc['id']!='章节02':e.string=ch['title']
   if module=='章节02':
    for key,value in zip(['#ch-first','#ch-rest'],ch['groups']):s.select_one(key).string=value
   e=s.select_one('#giant')
   if e:e.clear();e.append(ch['number'][:-1]);t=s.new_tag('span',attrs={'class':'purple'});t.string=ch['number'][-1];e.append(t)
   e=s.select_one('#ch-pill')
   if e:e.string=ch['number']+'　'+ch['title']
  for action in sc['events']:
   if action.get('binding')=='data.prompt':action['text']=c['data']['prompt']
   if action.get('binding')=='data.budget.total':
    action['to']=total
    if action.get('knots'):action['knots']=[[t,v*total/15] for t,v in action['knots']]
  for asset in s.select('[src]'):
   asset['src']=c.get('assetOverrides',{}).get(asset['src'],asset['src'])
  # 可视化编辑器只写当前场景的明确选择器，不污染其他模块。
  allowed={'font-size','line-height','letter-spacing','width','height','padding','gap','border-radius','color','background','left','top','right','bottom','margin-top','opacity','object-fit'}
  for change in c.get('layout',{}).get(sc['id'],[]):
   selected=s.select(change['target']);assert selected,('画面参数目标不存在',sc['id'],change['target'])
   assert set(change['style'])<=allowed,'画面参数包含不支持的属性'
   for element in selected:
    element['style']=element.get('style','')+';'+ ';'.join(k+':'+str(v)+'!important' for k,v in change['style'].items())
  # 静态图、视频与字体全部必须来自可移动包内。
  for e in s.select('[src]'):assert (ROOT/e['src']).is_file(),e['src']
  for action in sc['events']:
   assert action['at']>=0 and action['at']+action.get('duration',0)<=sc['visibleEnd']-sc['start']+.001,(sc['id'],action)
   if action.get('knots'):
    points=action['knots'];assert len(points)>=2 and points[0][0]==0 and all(a[0]<b[0] for a,b in zip(points,points[1:])) and points[-1][0]<=action['duration'],(sc['id'],'变化节点须从0开始、时间递增且不超过动作时长')
   selector=action['target'];assert s.select(selector) or (selector=='.page, .header' and sc['header']),(sc['id'],selector)
   all_events.append(dict(scene=sc['id'],absolute_start=sc['start']+action['at'],**action))
  style_ids.update(e['id'] for e in s.select('[id]'))
  namespaced(s,sc['domId'])
  bg=sc.get('background') or ('var(--ink)' if sc['dark'] else 'var(--paper)');bg=bg+'!important' if bg=='transparent' else bg;fg='#fff' if sc['dark'] else '#19191e'
  chapter_index=max([int(x.get('module',x['id'])[-2:])-1 for x in c['scenes'] if x.get('module',x['id']).startswith('章节') and x['start']<=sc['start']]+[0])
  markers=''.join('<i class="'+('current' if k==chapter_index else '')+'"></i>' for k in range(5))
  head=('<div class="header"><span><span class="dots">'+markers+'</span> '+sc['title']+'</span><span class="badge">时间预算算例</span></div>') if sc['header'] else ''
  content='<div class="page">'+str(s).replace('#c6a4fa',c['theme']['purple']).replace('#8050b4',c['theme']['purpleOnPaper'])+'</div>' if sc['header'] else str(s)
  import html
  bodies.append(f'<section id="host-{i}" class="scene" data-mg-start="{sc["start"]}" data-mg-duration="{sc["visibleEnd"]-sc["start"]:.6f}" data-layout-allow-overlap="true" style="z-index:{10+i}"><div id="{sc["domId"]}" data-module="{html.escape(module,quote=True)}" class="scene-root {"dark" if sc["dark"] else "light-page"}" style="background:{bg};color:{fg}">{head}{content}</div></section>')
 css=(ROOT/'基础CSS.css').read_text();css=css.replace('#c6a4fa','var(--purple)').replace('#8050b4','var(--purpleOnPaper)')
 # 将旧root规则限制在独立场景，不让各场背景互相改色。
 css=css.replace('#root','.scene-root')
 if (ROOT/'精修CSS.css').exists():css+='\n'+(ROOT/'精修CSS.css').read_text()
 css+='''html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:var(--ink)}#root{position:relative;width:1920px;height:1080px;overflow:hidden;font-family:本片中文}.clip{position:absolute}.scene{position:absolute;inset:0}.scene-root{position:absolute;inset:0;opacity:0}.scene-root .panel.light .label{color:#655d70}.scene-root .panel.light .purple{color:var(--purpleOnPaper)}.scene-root .panel.light .unit{color:#19191e}.caption{z-index:9999;bottom:34px;font-size:37px;line-height:1.3;padding:14px 25px;max-width:1770px}.end-char,.end-group{display:inline-block}.scene-root .page{isolation:isolate;z-index:1}.scene-root .header{z-index:2}.scene-root [data-mg-id="wall"]{z-index:-1}.check{z-index:15}.bar-human{transform-origin:left}.progress-current{transform-origin:left}'''
 # 场景ID已经隔离，CSS同样绑定原始语义ID；只匹配真实ID，不碰十六进制色值。
 for key in sorted(style_ids,key=len,reverse=True):
  css=re.sub(r'#'+re.escape(key)+r'(?![\w-])','[data-mg-id="'+key+'"]',css)
 theme=':root{'+''.join('--'+k+':'+v+';' for k,v in c['theme'].items())+'}'
 captions=[]
 for row in c.get('captions',[]):
  parts=re.split(r'(?<=[，。？！；：])',row['text']);lines=[];current=''
  for part in parts:
   if len(current+part)>30 and current:lines.append(current);current=part
   else:current+=part
  if current:lines.append(current)
  import html
  d=(row['end']-row['start'])/max(1,len(lines))
  for j,line in enumerate(lines):captions.append(f'<div id="caption-{row["id"]}-{j}" class="clip caption" data-start="{row["start"]+j*d:.6f}" data-duration="{d:.6f}" data-track-index="8" data-track-kind="captions">{html.escape(line)}</div>')
 background_html=''.join('<video id="'+b['id']+'" class="clip" src="'+b['src']+'" muted playsinline data-start="'+str(b['start'])+'" data-duration="'+str(b['duration'])+'" data-track-index="0" style="'+b['style']+'"></video>' for b in c.get('backgrounds',[]))
 ambient_code=[]
 for wall in c.get('ambient_walls',[]):
  wid=wall['id'];start=wall['start'];end=start+wall['duration'];rows=[]
  for row in range(4):
   tiles=[]
   for col in range(7):
    original='assets/ambient/clip-'+str((row*3+col)%4+1)+'.mp4';src=c.get('assetOverrides',{}).get(original,original)
    assert (ROOT/src).is_file(),src
    tiles.append(f'<div style="position:absolute;left:{col*548}px;top:0;width:520px;height:292px;overflow:hidden;border-radius:18px"><video id="{wid}-v-{row}-{col}" class="clip" src="{src}" muted playsinline data-start="{start}" data-duration="{wall["duration"]}" data-track-index="0" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover"></video></div>')
   rows.append(f'<div id="{wid}-row-{row}" style="position:absolute;left:-548px;top:{row*320}px;width:4000px;height:292px">'+''.join(tiles)+'</div>')
   phase=wall.get('phases',[0,0,0,0])[row]
   ambient_code.append(f'tl.fromTo("#{wid}-row-{row}",{{x:{phase}}},{{x:{phase+wall["speeds"][row]*wall["duration"]},duration:{wall["duration"]},ease:"none",immediateRender:false}},{start});')
  background_html+=f'<div id="{wid}" style="position:absolute;inset:0;opacity:0;z-index:4;overflow:hidden"><div style="position:absolute;left:-300px;top:-100px;width:3300px;height:1300px;transform:perspective(2600px) rotateX(14deg) rotateZ(-11deg) scale(.84);transform-origin:50% 50%">'+''.join(rows)+'</div></div>'
  ambient_code.append(f'tl.set("#{wid}",{{opacity:0}},0);tl.set("#{wid}",{{opacity:{wall["opacity"]}}},{start});tl.set("#{wid}",{{opacity:0}},{end});')
 audio=''
 if c.get('audio'):
  assert (ROOT/c['audio']).is_file()
  audio=f'<audio id="narration" class="clip" src="{c["audio"]}" data-start="0" data-duration="{duration:.9f}" data-volume="1" data-track-index="9"></audio>'
 code='const SPECS='+json.dumps(c['scenes'],ensure_ascii=False)+';const tl=RefMG.build(gsap,SPECS);'+''.join(ambient_code)+'tl.to({t:0},{t:1,duration:'+str(duration)+',ease:"none"},0);window.__timelines=window.__timelines||{};window.__timelines.main=tl;'
 document='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=1920,height=1080"><script src="assets/vendor/gsap.min.js"></script><script src="运行库/motions.js"></script><style>'+theme+css+'</style></head><body><div id="root" data-composition-id="main" data-width="1920" data-height="1080" data-fps="30" data-start="0" data-duration="'+str(duration)+'">'+background_html+''.join(bodies)+''.join(captions)+audio+'</div><script>'+code+'</script></body></html>'
 destination=Path(out) if out else ROOT/'index.html';destination.write_text(document)
 report=dict(config=str(Path(config_path).resolve()),config_sha256=hashlib.sha256(Path(config_path).read_bytes()).hexdigest(),html=str(destination),html_sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),scene_count=len(c['scenes']),event_count=len(all_events),events=all_events)
 (destination.parent/'构建记录.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));return report
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--config',default=str(ROOT/'配置.json'));ap.add_argument('--out');a=ap.parse_args();r=build(a.config,a.out);print(json.dumps({k:r[k] for k in ['html','scene_count','event_count','html_sha256']},ensure_ascii=False,indent=2))
