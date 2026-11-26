"""将一个组件配置构建为独立Hyperframes工程。Python标准库，无整片依赖。"""
from pathlib import Path
import argparse,copy,hashlib,importlib,json,math,os,re,shutil,sys,subprocess

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import runtime
CATALOG=json.loads((ROOT/'目录.json').read_text())['components']
REGISTRY={x['id']:x for x in CATALOG}

def load(path):
    return json.loads(Path(path).read_text())

def check_text(value,path,limit):
    if not isinstance(value,str) or not value.strip() or len(value)>limit:
        raise ValueError(f'{path}须为1至{limit}字的文字，不能自动截掉超出的内容')

def validate(spec):
    if not isinstance(spec,dict):raise ValueError('配置须为JSON对象')
    if spec.get('format')!='nana-component@1':raise ValueError('format须为nana-component@1')
    ident=spec.get('component')
    if ident not in REGISTRY:raise ValueError('component须为目录中的15个组件之一')
    unknown=set(spec)-{'format','component','duration','content','media','theme','options'}
    if unknown:raise ValueError('不支持的配置字段：'+','.join(sorted(unknown)))
    dur=spec.get('duration',4)
    minimum=REGISTRY[ident]['duration_range'][0]
    if type(dur) not in (int,float) or not math.isfinite(dur) or not minimum<=dur<=12 or abs(dur*30-round(dur*30))>1e-5:
        raise ValueError(f'duration须为{minimum}至12秒，并按1/30秒对齐')
    content=spec.get('content',{});media=spec.get('media',{});theme=spec.get('theme',{});options=spec.get('options',{})
    if not all(isinstance(x,dict) for x in [content,media,theme,options]):raise ValueError('content、media、theme、options须为对象')
    allowed=set(REGISTRY[ident]['content_fields'])
    if set(content)-allowed:raise ValueError('此组件不接受内容字段：'+','.join(sorted(set(content)-allowed)))
    if ident=='13-badge' and options.get('layout')=='overlay' and set(content)-{'badge_text'}:raise ValueError('叠加描勾只接受badge_text，底图中的标题不由组件改写')
    if ident=='07-takeaway' and options.get('exit_mode','peel')=='peel' and dur<3:raise ValueError('双层翻页至少3秒；共同溶出可用1至12秒')
    limits={'title':24,'subtitle':35,'body':48,'badge_text':10,'eyebrow':30,'usage_label':12,'input_label':24,'output_label':24}
    if ident=='07-takeaway':limits['title']=22
    if ident=='11-storyboard':limits['title']=25
    if ident=='12-smash':limits['title']=16
    for key,value in content.items():
        if key in limits:check_text(value,key,limits[key])
        elif isinstance(value,list):
            counts={'03-grid':{'items':6,'item_bodies':6},'06-fan':{'items':5,'card_bodies':5},'08-nodes':{'items':4,'node_titles':3},'09-media-board':{'items':6,'list_items':5},'11-storyboard':{'labels':3},'14-pipeline':{'items':5},'15-nav':{'sections':6}}
            count=counts.get(ident,{}).get(key)
            if count and len(value)!=count:raise ValueError(f'{key}须恰好{count}项')
            for j,item in enumerate(value):check_text(item,f'{key}[{j}]',8 if key=='node_titles' else 24 if key=='item_bodies' else 56 if key=='card_bodies' else 10 if key=='sections' else 15)
        else:raise ValueError(f'{key}须为文字或列表')
    for key,value in media.items():
        if key not in REGISTRY[ident]['media_slots']:raise ValueError(f'未知媒体插槽：{key}')
        if not isinstance(value,str) or Path(value).is_absolute() or '..' in Path(value).parts or not value:raise ValueError('媒体须为media-root内的相对文件路径')
        ext=Path(value).suffix.lower()
        if ext not in ['.png','.jpg','.jpeg','.webp','.svg'] and not (ident=='13-badge' and key=='background' and ext in ['.mp4','.webm']):raise ValueError('图片接受PNG/JPG/WebP/SVG；仅13背景另支持原速MP4/WebM')
    if set(theme)-{'accent','nav_accent'}:raise ValueError('theme仅支持accent、nav_accent')
    for value in theme.values():
        if not isinstance(value,str) or not re.fullmatch('#[0-9a-fA-F]{6}',value):raise ValueError('颜色须为六位十六进制值')
    if set(options)-{'motions','show_nav','chapter','slot_options','layout','exit_mode'}:raise ValueError('未知options字段')
    layouts={'06-fan':['default','reference'],'07-takeaway':['default','reference'],'11-storyboard':['default','reference'],'13-badge':['default','overlay']}
    if 'layout' in options and options['layout'] not in layouts.get(ident,[]):raise ValueError('layout不适用于此组件')
    if 'exit_mode' in options and (ident!='07-takeaway' or options['exit_mode'] not in ['peel','dissolve']):raise ValueError('exit_mode只用于07，值为peel或dissolve')
    if 'show_nav' in options and type(options['show_nav']) is not bool:raise ValueError('show_nav须为true或false')
    if 'chapter' in options and (type(options['chapter']) is not int or not 1<=options['chapter']<=6):raise ValueError('chapter须为1至6的整数')
    if not isinstance(options.get('motions',{}),dict) or not isinstance(options.get('slot_options',{}),dict):raise ValueError('motions和slot_options须为对象')
    if ident=='15-nav' and options.get('show_nav',True) is False:raise ValueError('导航组件须保留导航，其他组件可关闭导航')
    if ident=='07-takeaway' and options.get('chapter',5 if options.get('exit_mode')=='dissolve' else 2)!=(5 if options.get('exit_mode')=='dissolve' else 2):raise ValueError('chapter须与翻页或共同溶出结构一致')
    for key,window in options.get('motions',{}).items():
        if not re.fullmatch('[a-z0-9-]+:[0-9]+',key) or not isinstance(window,dict) or not set(window)<={'start','duration'}:raise ValueError('motions使用对象:次数及start/duration')
        for val in window.values():
            if type(val) not in (int,float) or not math.isfinite(val) or val<0:raise ValueError('动作时窗须为非负有限秒数')
        if 'duration' in window and window['duration']<=0:raise ValueError('动作duration须大于0')
        if key=='badge-reset:0' and 'duration' in window:raise ValueError('badge-reset是瞬时清空，只设置start')
        if window.get('start',0)+window.get('duration',0)>dur:raise ValueError('动作时窗超出组件总长')
    for key,opt in options.get('slot_options',{}).items():
        if key not in REGISTRY[ident]['media_slots'] or not isinstance(opt,dict) or set(opt)-{'fit','position','background','radius','border'}:raise ValueError('媒体显示参数无效')
        if opt.get('fit','contain') not in ['contain','cover']:raise ValueError('fit须为contain或cover')
        if opt.get('position','center') not in ['center','top center','bottom center','left center','right center']:raise ValueError('图片位置无效')
        for k in ['background','border']:
            if k in opt and (not isinstance(opt[k],str) or not re.fullmatch(r'[a-zA-Z0-9# .,()%/-]{1,80}',opt[k])):raise ValueError('媒体样式只接受颜色和边框值')
        if 'radius' in opt and (type(opt['radius']) not in (int,float) or not math.isfinite(opt['radius']) or not 0<=opt['radius']<=120):raise ValueError('radius须为0至120像素')
    return spec

def copy_file(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists() and dst.read_bytes()==src.read_bytes() and not os.path.samestat(src.stat(),dst.stat()):return
    # 用独立inode的副本原子替换，修改导出图片不会改到其他项目或源素材。
    temp=dst.with_name(dst.name+'.copy-tmp')
    shutil.copy2(src,temp);temp.replace(dst)

def build(spec,out,media_root=None):
    spec=copy.deepcopy(validate(spec));spec.setdefault('duration',4);ident=spec['component'];out=Path(out).resolve();media_root=Path(media_root or ROOT/'assets').resolve()
    preset=load(ROOT/'presets'/(ident+'.json'));preset['content'].update(spec.get('content',{}));preset['media'].update(spec.get('media',{}));preset['options'].update(spec.get('options',{}));preset['theme'].update(spec.get('theme',{}))
    if ident=='13-badge' and preset['options'].get('layout')=='overlay':preset['content']={k:v for k,v in preset['content'].items() if k=='badge_text'}
    spec.update(content=preset['content'],media=preset['media'],options=preset['options'],theme=preset['theme']);validate(spec)
    for f in (ROOT/'shared').rglob('*'):
        if f.is_file():copy_file(f,out/'assets'/f.relative_to(ROOT/'shared'))
    media={}
    for key,value in spec['media'].items():
        src=(media_root/value).resolve()
        if not src.is_relative_to(media_root) or not src.is_file():raise ValueError(f'图片不存在或超出素材目录：{key}={value}')
        if src.suffix.lower() in ['.mp4','.webm']:
            info=json.loads(subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(src)],capture_output=True,text=True,check=True).stdout)
            track=next((t for t in info['streams'] if t['codec_type']=='video'),None)
            if track is None or float(track.get('duration',info.get('format',{}).get('duration',0)))+1/30<spec['duration']:raise ValueError('背景视频短于组件时长，不能冻结末帧补齐')
        filename=hashlib.sha256(src.read_bytes()).hexdigest()[:12]+src.suffix.lower();copy_file(src,out/'assets/content'/filename);media[key]='assets/content/'+filename
    content=dict(spec['content']);options=spec['options'];chapter=options.get('chapter',(5 if options.get('exit_mode')=='dissolve' else 2) if ident=='07-takeaway' else 1)
    content.update(media=media,motions=options.get('motions',{}),slot_options=options.get('slot_options',{}),layout=options.get('layout','default'))
    if ident=='07-takeaway':
        content.update(summary_rect=[94,205,660,454],media_rect={'screen':[795,180,1090,670],'underlay':[1100,230,755,556]},summary_track=True,line_duration=spec['duration']-.65,page_peel={'start':spec['duration']-.6,'duration':.32,'ease':'none'},exit={'summary_start':spec['duration']-.22,'fade_duration':.18})
        content['page_peel'].update(options.get('motions',{}).get('screen-peel:0',{}))
        if options.get('exit_mode')=='dissolve':
            content['page_peel']=None;content['exit']['screen_start']=spec['duration']-.22
        if options.get('layout')=='reference':content['media_rect']['screen']=[1100,230,755,556]
    if ident=='11-storyboard' and options.get('layout')=='reference':content['media_rect']={'idea':[150,398,365,405],'frames':[637,500,601,297],'result':[1330,475,470,327]}
    config={'templates':{ident:content},'show_nav':options.get('show_nav',ident=='15-nav'),**spec['theme']}
    module=importlib.import_module('modules.'+REGISTRY[ident]['module'])
    previous=runtime.NAMES[:]
    if ident=='15-nav':runtime.NAMES[:]=content.get('sections',previous)
    try:
        scene=runtime.Scene('component',spec['duration'],ident,config,chapter)
        module.build(scene)
        # 配置拼错动作名应报错，不能静默忽略。
        known={x['id'] for x in scene.events}
        if set(options.get('motions',{}))-known:raise ValueError('未找到动作键：'+','.join(set(options['motions'])-known))
        body=scene.finish()
    finally:runtime.NAMES[:]=previous
    folder=out/'compositions';folder.mkdir(parents=True,exist_ok=True);(folder/'component.html').write_text(body)
    root=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>nana mg1 · {REGISTRY[ident]['name']}</title><script src="assets/vendor/gsap.min.js"></script><script src="assets/runtime/diagonal-peel.js"></script><style>html,body{{margin:0;width:1920px;height:1080px;background:#090f1f;overflow:hidden}}</style></head><body><div id="root" data-composition-id="main" data-duration="{spec['duration']}" data-width="1920" data-height="1080" data-fps="30"><div class="clip" data-composition-id="component" data-composition-src="compositions/component.html" data-start="0" data-duration="{spec['duration']}" data-width="1920" data-height="1080" data-track-index="1" data-track-kind="graphics"></div></div><script>window.__timelines=window.__timelines||{{}};window.__timelines.main=gsap.timeline({{paused:true}});</script></body></html>'''
    (out/'index.html').write_text(root)
    (out/'配置.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
    events={'component':ident,'duration':spec['duration'],'events':scene.events}
    (out/'动作参数.json').write_text(json.dumps(events,ensure_ascii=False,indent=2)+'\n')
    (out/'hyperframes.json').write_text(json.dumps({'authoringSkill':'hyperframes','paths':{'assets':'assets','blocks':'compositions','components':'compositions/components'}},indent=2)+'\n')
    (out/'package.json').write_text(json.dumps({'name':'nana-component','private':True,'type':'module','scripts':{'preview':'npx hyperframes@0.9.97 preview','render':'npx hyperframes@0.9.97 render'}},indent=2)+'\n')
    return {'component':ident,'duration':spec['duration'],'frames':round(spec['duration']*30),'event_count':len(scene.events),'project':str(out)}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--component',choices=REGISTRY);p.add_argument('--config',type=Path);p.add_argument('--duration',type=float);p.add_argument('--media-root',type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    if not a.config and not a.component:p.error('指定--component或--config')
    spec=load(a.config or ROOT/'presets'/(a.component+'.json'))
    if a.component:spec['component']=a.component
    if a.duration is not None:spec['duration']=a.duration
    try:print(json.dumps(build(spec,a.output,a.media_root),ensure_ascii=False))
    except (ValueError,OSError) as e:p.exit(2,str(e)+'\n')
