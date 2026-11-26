"""本地构建、预览、检查与渲染入口。"""
from pathlib import Path
import argparse,subprocess,json,datetime,hashlib,wave,sys
R=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('operation',choices=['build','check','preview','render']);ap.add_argument('--config',default=str(R/'配置.json'));ap.add_argument('--launcher',default=str(Path.home()/'.agents/skills/hyperframes/scripts/plugin-cli.mjs'));ap.add_argument('--port',type=int,default=64066);ap.add_argument('--name',default='模板演示');a=ap.parse_args()
subprocess.run([sys.executable,str(R/'构建.py'),'--config',a.config],check=True)
if a.operation=='build':raise SystemExit(0)
launcher=Path(a.launcher);assert launcher.is_file(),'找不到Hyperframes启动器，请用--launcher指定已安装的plugin-cli.mjs'
now=datetime.datetime.now().strftime('%Y%m%d-%H%M%S');logs=R/'执行记录';logs.mkdir(exist_ok=True)
records=[]
def run(argv,label):
 log=logs/(now+'-'+label+'.log')
 with log.open('wb') as stream:r=subprocess.run(argv,cwd=R,stdout=stream,stderr=subprocess.STDOUT)
 records.append(dict(argv=argv,log=str(log.relative_to(R)),exit_code=r.returncode));print(label,'退出',r.returncode,'日志',log)
 (logs/(now+'-任务.json')).write_text(json.dumps(records,ensure_ascii=False,indent=2));assert r.returncode==0,'执行失败，保留原任务和日志'
base=['node',str(launcher),'--cli-version','0.9.94']
if a.operation=='preview':
 run(base+['preview','--background','--no-open','--port',str(a.port),'--json'],'预览');print('从预览日志读取实际studioUrl，用系统Chrome打开；这是可编辑工程。')
elif a.operation=='check':run(base+['check','--json'],'检查')
else:
 c=json.loads(Path(a.config).read_text());audio=R/c['audio'] if c.get('audio') else None
 if audio:
  with wave.open(str(audio),'rb') as w:
   assert w.getsampwidth()==2,'请使用16位PCM WAV源'
   assert abs(w.getnframes()/w.getframerate()-c['canvas']['duration'])<1/c['canvas']['fps'],'音轨与成片长度不同；请提供对应原速音轨或将audio设为null'
 run(base+['check','--json'],'检查')
 out=R/'输出';out.mkdir(exist_ok=True);native=out/(a.name+'-'+now+'-Hyperframes原生.mp4');run(base+['render','--fps','30','--quality','looks','--output',str(native)],'原生渲染')
 view=out/(a.name+'-'+now+('-原速原声.mp4' if audio else '-观看版.mp4'))
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=pix_fmt,color_space,color_range','-of','json',str(native)]))['streams'][0]
 source_rgb=probe.get('color_space')=='gbr' or probe.get('pix_fmt','').startswith(('gbr','rgb'))
 conversion='scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p' if source_rgb else 'format=yuv420p'
 argv=['ffmpeg','-nostdin','-v','error','-xerror','-i',str(native)]
 if audio:argv+=['-i',str(audio)]
 argv+=['-map','0:v:0']
 if audio:argv+=['-map','1:a:0','-c:a','flac','-strict','-2']
 else:argv+=['-an']
 argv+=['-vf',conversion,'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv','-map_metadata','-1','-movflags','+faststart',str(view)]
 run(argv,'观看版封装')
 run(['ffmpeg','-nostdin','-v','error','-xerror','-i',str(view),'-f','null','-'],'完整解码')
 digest=hashlib.sha256(view.read_bytes()).hexdigest();print('已生成',view,'SHA256',digest);print('可在Hyperframes桌面应用继续编辑；本命令不替代视觉/OCR审核。')
