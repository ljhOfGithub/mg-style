"""将同一份配置编译为独立、可定位时间的 Hyperframes 场景。仅使用标准库。"""
from pathlib import Path
from html import escape
import argparse
import json
import re
import shutil

P = Path(__file__).resolve().parents[1]
ENGINE = P
TEMPLATES = json.loads((P / "模板索引.json").read_text())
PLAN = json.loads((P / "整片计划.json").read_text())
NAMES = ["HyperFrames", "Video Use", "Remotion", "Generative Media", "Video Cut", "Seedance 2"]

CSS = r"""+@font-face{font-family:'MG Sans';src:url('assets/fonts/PingFangSC-Medium.ttf')}*{box-sizing:border-box}#root{position:absolute;inset:0;color:#f4f7ff;font-family:'MG Sans',sans-serif;overflow:hidden;background:#080e1a}h1,h2,h3,p{margin:0} .stage{position:absolute;inset:0;overflow:hidden;background:radial-gradient(ellipse at 9% 85%,#12404965,transparent 48%),radial-gradient(ellipse at 92% 66%,#391f6766,transparent 52%),#090f1f}.grid-bg{position:absolute;inset:0;background-image:linear-gradient(#78b0ca14 1px,transparent 1px),linear-gradient(90deg,#78b0ca14 1px,transparent 1px);background-size:72px 72px}.eyebrow{color:var(--accent);font-size:22px;letter-spacing:4px}.heading{font-size:52px;font-weight:700;line-height:1.2}.sub{color:#c0cce1;font-size:27px;line-height:1.6}.tiny{font-size:22px;color:#acb6cb}.panel{border:2px solid #6a789b75;border-radius:14px;background:#10182be6}.slot{width:100%;height:100%;object-fit:contain;display:block}.slot-box{position:absolute;overflow:hidden;border:2px solid #798caa8a;border-radius:16px;background:#101a2d}.window-bar{position:absolute;top:0;left:0;right:0;height:32px;display:flex;align-items:center;gap:9px;padding-left:18px;background:#101625;border-bottom:1px solid #5d70935c}.window-bar i{width:8px;height:8px;border-radius:100%;background:#b39af4}.window-body{position:absolute;inset:34px 0 0}.card-title{font-size:32px;font-weight:700;line-height:1.3}.card-copy{font-size:24px;line-height:1.5;color:#d3daeb}.line{height:2px;background:var(--accent);transform-origin:left center}.footer{position:absolute;left:110px;right:110px;bottom:70px;height:2px;background:linear-gradient(90deg,#64bfd3,#7454bb)}.label{display:inline-block;padding:10px 20px;border:1px solid #8c7ed777;border-radius:7px;background:#6651bc33;font-size:23px}.chip{padding:9px 17px;border:1px solid #6d8ca777;color:#d4ebf2;font-size:22px}.placeholder-base{position:absolute;inset:0;background:#101a2d}.placeholder-base img{width:100%;height:100%;object-fit:cover}.surface{position:absolute;inset:0;background:#090d16e8}.heading-wrap{position:absolute;left:120px;right:120px;top:150px}.grid-card{position:absolute;border:2px solid #566b9477;background:linear-gradient(145deg,#0c1e35,#1c1435);padding:52px 35px}.grid-card .n{font-size:29px;color:var(--accent);margin-bottom:22px}.grid-card .rule{margin:22px 0;width:88px;height:2px;background:#8b72dc}.nav{position:absolute;left:78px;right:78px;top:20px;height:40px;display:flex;align-items:center;border:1px solid #518a9b88;border-radius:7px;background:#08131de8;padding:4px;gap:6px}.nav span{flex:1;text-align:center;font-size:18px;color:#becbe0;padding:5px 3px;border-radius:4px}.nav .active{background:var(--accent);color:#101423}.ribbon{position:absolute;border-radius:50%;background:#1b1643;border:1px solid #7d65a94d}.white-card{background:#fffef3;color:#1c2432;border-radius:14px;border:2px solid #c6cad3;padding:30px}.white-card .card-copy{color:#495166}.outline-number{font-size:270px;line-height:1;color:transparent;-webkit-text-stroke:2px #a995ff}.chapter-title{font-size:70px;line-height:1.1;letter-spacing:-2px;font-weight:700;white-space:nowrap}.media-caption{position:absolute;bottom:12px;left:18px;font-size:20px;color:#b5c2db}.badge{position:absolute;width:700px;height:174px;right:120px;top:92px;background:#fffdf7;border-radius:16px;display:flex;align-items:center;padding:28px 190px 28px 42px;color:#12151b}.badge-text{font-size:50px;font-weight:900;white-space:nowrap;font-style:italic}.badge-square{position:absolute;right:26px;top:24px;width:126px;height:126px;background:#252930;border-radius:14px}.badge-check{position:absolute;right:12px;top:16px;width:140px;height:140px}.badge-check path{fill:none;stroke:#8bf96b;stroke-width:19;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1}.takeaway{position:absolute;left:94px;top:205px;width:585px;min-height:450px;background:#0e1722f2;border:2px solid #53677b88;border-radius:18px;padding:72px 42px 30px}.takeaway .eyebrow{font-size:40px;font-weight:700}.takeaway .heading{font-size:42px;margin:27px 0}.takeaway .line{margin-top:30px}.source-hold{position:absolute;right:110px;bottom:62px;color:#a8b7ce;font-size:20px}
""".replace("+@font", "@font").replace("PingFangSC-Medium.ttf", "NotoSansSC.ttf").replace(".heading-wrap{position:absolute;left:120px;right:120px;top:150px}", ".heading-wrap{position:absolute;left:120px;right:120px;top:120px}")

def text(value, limit=100):
    value = str(value)
    if len(value) > limit:
        raise ValueError(f"文字过长（最多{limit}字）：{value[:30]}")
    return escape(value)

def read_config(path):
    data = json.loads(Path(path).read_text())
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", data.get("accent", "#90ddf1")):
        raise ValueError("accent 必须是六位十六进制颜色")
    for section, values in data.get("templates", {}).items():
        if section not in {t["id"] for t in TEMPLATES}|{"media-slot"}:
            raise ValueError(f"未知模板：{section}")
        for key, value in values.get("media", {}).items():
            path_value = Path(value)
            if path_value.is_absolute() or ".." in path_value.parts or not value.startswith("assets/"):
                raise ValueError(f"媒体只接受工程 assets/ 内的相对路径：{key}")
        for key in ("title", "subtitle", "body"):
            if key in values:
                text(values[key], 28 if key == "title" else 90)
        for key, window in values.get("motions", {}).items():
            if not re.fullmatch(r"[a-z0-9-]+:[0-9]+", key):
                raise ValueError(f"动作键需为 对象:次数，例如 screen:0：{key}")
            if not set(window)<= {"start","duration"} or any(not isinstance(v,(int,float)) or v<0 for v in window.values()):
                raise ValueError(f"动作时窗必须使用非负秒数：{key}")
    return data

class Scene:
    def __init__(self, ident, duration, template, config, chapter=1, label=""):
        self.id, self.duration, self.template = ident, duration, template
        self.cfg = dict(config.get("templates", {}).get(template, {}))
        if template=="05-chapter":
            self.cfg.update(config.get("chapter_presets",{}).get(str(chapter or 1),{}))
        self.cfg.update(config.get("shots",{}).get(ident,{}))
        self.project_config=config
        self.accent = config.get("accent", "#90ddf1")
        self.nav_accent = config.get("nav_accent", "#8e72dc")
        self.chapter, self.label = chapter, label
        self.html, self.tweens = [], []
        self.animated_keys = set()
        self.initial_properties = {}
        self.key_counts, self.events = {}, []
        self.labeled_keys=set()

    def key(self, key):
        return self.id + "-" + key

    def add(self, key, markup, style="", cls="", attrs=""):
        self.html.append(f'<div id="{self.key(key)}" class="{cls}" style="{style}" {attrs}>{markup}</div>')

    def animate(self, key, start, duration, before, after, ease="power2.out"):
        # 上游01-flat-vector的独立t0和归一化时间组织，适配到GSAP seek-safe fromTo。
        count=self.key_counts.get(key,0);self.key_counts[key]=count+1
        event_id=f"{key}:{count}"
        override=self.cfg.get("motions",{}).get(event_id,{})
        start=override.get("start",start);duration=override.get("duration",duration)
        if override and start+duration>self.duration:
            raise ValueError(f"{event_id}动作超出模块时长：{start}+{duration}>{self.duration}")
        start = min(max(start, 0), max(0, self.duration - .02))
        duration = max(.01, min(duration, self.duration - start - .001))
        params = dict(after, duration=duration, ease=ease, immediateRender=False)
        self.animated_keys.add(key)
        # 每个属性以其最早事件为初值，退出才用到的裁切/位移也要在0秒锁定。
        initial=self.initial_properties.setdefault(key,{})
        for prop,value in before.items():
            if prop not in initial or start<initial[prop][0]:initial[prop]=(start,value)
        self.events.append(dict(id=event_id,selector="#"+self.key(key),start=start,duration=duration,before=before,after=after,ease=ease))
        self.tweens.append(f'tl.fromTo("#{self.key(key)}",{json.dumps(before)},{json.dumps(params)},{start:.6f});')

    def fade(self, key, start=.05, duration=.22):
        self.animate(key, start, duration, {"opacity":0}, {"opacity":1})

    def rise(self, key, start=.03, duration=.36, y=170):
        self.animate(key, start, duration, {"opacity":0,"y":y}, {"opacity":1,"y":0})

    def slot(self, key, kind="screen", style="", window=False):
        src = self.cfg.get("media", {}).get(key, f"assets/placeholders/{kind}.svg")
        if kind=="background" and self.project_config.get("recreation"):
            src="assets/examples/presenter.svg"
        rect=self.cfg.get("media_rect",{}).get(key)
        if rect:
            x,y,w,h=rect;style=f"left:{x}px;top:{y}px;width:{w}px;height:{h}px"
        options=self.cfg.get("slot_options",{}).get(key,{})
        for prop,css in [("radius","border-radius"),("background","background"),("border","border")]:
            if prop in options:style+=";"+css+":"+str(options[prop])+("px" if prop=="radius" else "")
        position=options.get("position","top center")
        ext = Path(src).suffix.lower()
        if ext in (".mp4", ".mov", ".webm"):
            media = f'<video id="{self.key(key)}-video" class="clip slot" data-start="0" data-duration="{self.duration}" data-track-index="2" src="{text(src)}" muted playsinline></video>'
        else:
            media = f'<img id="{self.key(key)}-media" class="slot" style="object-position:{text(position)}" src="{text(src)}" alt="可替换媒体" />'
        bar = '<div class="window-bar"><i></i><i></i><i></i></div>' if window else ""
        if window: media=f'<div class="window-body">{media}</div>'
        skip_label=(self.template=="04-browser" and key=="preview") or (self.template=="07-takeaway" and key=="underlay")
        if src.startswith("assets/placeholders/") and kind!="background" and "-inner-" not in self.id and not skip_label:
            labels={"document":"文档插槽","screen":"连续录屏插槽","image":"图片插槽","poster":"竖图插槽","video":"视频插槽","audio":"音频图形插槽","idea":"创意图插槽","filmstrip":"分镜图插槽"}
            position="left:16px;right:auto" if self.template=="04-browser" and key=="document" else "left:16px;right:16px"
            media+=f'<div id="{self.key(key+"-label")}" style="position:absolute;bottom:16px;{position};padding:12px 8px;background:#0b1422ee;color:#f3f7ff;text-align:center;font-size:28px;line-height:1.3;border-radius:7px">{labels[kind]}</div>'
            self.labeled_keys.add(key)
        self.add(key,bar+media,style,"slot-box")
        if kind=="background" and self.project_config.get("recreation"):
            presenter=self.cfg.get("presenter",{});px,py,pw,ph=presenter.get("rect",[650,90,700,940])
            self.add(key+"-presenter",f'<img src="{text(presenter.get("src","assets/examples/actor.svg"))}" style="width:100%;height:100%;object-fit:contain" />',f"position:absolute;left:{px}px;top:{py}px;width:{pw}px;height:{ph}px")

    def head(self, title, subtitle="", eyebrow="CODEX / VIDEO SKILLS"):
        self.add("heading", f'<div class="eyebrow">{text(eyebrow)}</div><h1 class="heading" style="margin-top:18px">{text(self.cfg.get("title",title),28)}</h1><p class="sub" style="margin-top:15px">{text(self.cfg.get("subtitle",subtitle),90)}</p>',"","heading-wrap")

    def grid(self, count=6, pipeline=False):
        names = self.cfg.get("items", ["选题","分镜","提示词","剪辑字幕","成片包装"] if pipeline else NAMES)
        bodies=self.cfg.get("item_bodies",["一句话生成动态内容","自动处理视频素材","代码批量制作视频","图片、视频、音频","中文剪辑与字幕","创意生成分镜"])
        if len(names)!=count: raise ValueError(f"{self.template} 需要恰好{count}项")
        for i,title in enumerate(names):
            x=100+i*350 if pipeline else 110+(i%3)*572
            y=330 if pipeline else 280+(i//3)*312
            w,h=(320,355) if pipeline else (552,292)
            if pipeline:
                markup=f'<p class="n">{i+1:02d}</p><div class="rule"></div><h2 class="card-title">{text(title,22)}</h2><p class="tiny" style="margin-top:16px">{["TOPIC","STORYBOARD","PROMPTS","EDIT & CAPTIONS","PACKAGE"][i]}</p>'
            else:
                markup=f'<span style="position:absolute;left:28px;top:120px;font-size:30px;color:var(--accent);font-weight:700">{i+1:02d}</span><div style="position:absolute;left:108px;top:104px;right:24px"><h2 class="card-title" style="font-size:28px">{text(title,22)}</h2><p class="tiny" style="font-size:18px;margin-top:18px">{text(bodies[i],24)}</p></div><div style="position:absolute;left:0;bottom:0;width:38%;height:3px;background:var(--accent)"></div>'
            self.add(f"card-{i}",markup,f'left:{x}px;top:{y}px;width:{w}px;height:{h}px',"grid-card")
            if pipeline and i<4:self.add(f"chain-arrow-{i}","→",f"position:absolute;left:{x+320}px;top:488px;font-size:22px;color:#82c5d9")

    def nav(self, active=None):
        active = self.chapter if active is None else active
        names=["概览"]+NAMES
        if self.template=="05-chapter":
            names=NAMES;active=max(0,min(5,active-1))
        else:names=["视频制作"]+NAMES+["串成工作流"]
        spans="".join(f'<span style="{("background:"+self.nav_accent+";color:#f9f8ff") if i==active else ""}">{i+1:02d} {text(name)}</span>' for i,name in enumerate(names))
        self.add("nav",spans,"","nav")

    def finish(self):
        inner=''.join(self.html)
        initial=''.join(f'gsap.set("#{self.key(key)}",{json.dumps({prop:v[1] for prop,v in values.items()})});' for key,values in self.initial_properties.items())
        code=initial+''.join(self.tweens)
        return f'''<template><style>{CSS}</style>
<div id="root" data-composition-id="{self.id}" data-width="1920" data-height="1080" style="--accent:{self.accent}">
<div id="{self.key('body')}" class="stage">{inner}</div></div>
<script>const tl=gsap.timeline({{paused:true}});{code}tl.to({{}},{{duration:.001}},{max(.001,self.duration-.002):.6f});window.__timelines=window.__timelines||{{}};window.__timelines["{self.id}"]=tl;</script></template>'''

def title_intro(s):
    s.slot("background","background","inset:0;border:0;border-radius:0")
    s.add("shade","","position:absolute;inset:0;background:#060b17a8")
    s.add("hero",f'<p class="eyebrow">CODEX · VIDEO WORKFLOW</p><h1 style="font-size:106px;margin-top:20px;white-space:nowrap">{text(s.cfg.get("title","用 Codex 串起视频制作"),24)}</h1>',"position:absolute;left:140px;right:140px;top:360px;text-align:center")
    s.add("subtitle",f'<p class="sub">{text(s.cfg.get("subtitle","六项 Skills，组合你的制作流程"),45)}</p>',"position:absolute;left:220px;right:220px;top:550px;text-align:center")
    s.add("tags",'<span class="chip">从创意到成片</span><span class="chip" style="margin-left:18px">Skills</span>',"position:absolute;left:580px;top:635px")
    s.animate("hero",.06,.24,{"scale":.78,"opacity":0},{"scale":1,"opacity":1})
    s.rise("subtitle",.28,.18,16);s.fade("tags",.38,.18);s.nav(0)

def media_flip(s):
    s.slot("background","background","inset:0;border:0;border-radius:0")
    s.slot("screen","screen","left:250px;top:150px;width:1420px;height:830px",True)
    s.rise("screen",0,.38,480)
    end=max(.55,s.duration-.42)
    # 斜边遮罩与整体旋转共同产生原片纸页般的退出，不虚称真实曲面卷页。
    s.animate("screen",end,.36,{"clipPath":"polygon(0% 0%,100% 0%,100% 100%,0% 100%)","rotation":0,"x":0,"y":0},
        {"clipPath":"polygon(0% 0%,0% 0%,0% 0%,0% 0%)","rotation":-38,"x":-2200,"y":-900},"power2.in")
    s.nav()

def grid_six(s, include_nav=True):
    s.add("bg","","inset:0","grid-bg")
    s.head("将六项 Skills 组合起来","按任务选择，再串成工作流程")
    s.grid(); s.fade("heading",0,.18)
    # 源六宫格整体出现，六卡同一入场时刻；不改成通用逐条飞入。
    for i in range(6):s.fade(f"card-{i}",.08,.22)
    if include_nav:s.nav(7 if s.chapter==7 else 0)
    s.add("footer","","","footer")
    if s.chapter==7:workflow_badge(s,overlay=True)

def browser_stack(s):
    if s.chapter==0:
        window_cfg=s.cfg
        s.cfg=dict(s.project_config.get("templates",{}).get("03-grid",{}))
        grid_six(s,False)
        s.cfg=window_cfg
        # 叠窗承接上一镜的完整六宫格，底层内容不能在切点重新入场。
        s.tweens=[];s.events=[];s.initial_properties={};s.animated_keys=set();s.key_counts={}
        # 原片先让叠窗覆盖既有总览；仅标注这些确实位于下层的文字。
        # 不豁免前景窗口、内层预览或其他场景的遮挡检查。
        for index,markup in enumerate(s.html):
            if f'id="{s.key("heading")}"' in markup or any(f'id="{s.key(f"card-{i}")}"' in markup for i in range(6)):
                s.html[index]=re.sub(r'<(h1|h2|p|div) class="(eyebrow|heading|sub|n|card-title|tiny)"',r'<\1 data-layout-allow-occlusion class="\2"',markup)
    else:
        s.slot("background","background","inset:0;border:0;border-radius:0")
    group_start=len(s.html)
    s.slot("document","document","left:135px;top:70px;width:470px;height:1010px",False)
    if "preview" in s.cfg.get("media",{}):
        s.slot("preview","screen","left:607px;top:316px;width:1178px;height:663px",False)
    else:
        # 源播放器切页的空预览是纯色底，不是通用媒体占位图。
        s.add("preview","","position:absolute;left:607px;top:316px;width:1178px;height:663px;background:#0b1121","slot-box")
    if s.project_config.get("recreation"):
        s.add("browser-bar",'<img src="assets/examples/browser-chrome.svg" style="width:100%;height:100%;object-fit:fill"/>',"position:absolute;left:607px;top:70px;width:1178px;height:246px")
        s.rise("browser-bar",.09,.38,440)
    s.rise("document",.02,.38,440);s.rise("preview",.09,.38,440)
    # 可替换真实录屏；缺省示例把内层不同页作为独立组，保持内外两层动画。
    if "preview" not in s.cfg.get("media",{}):
        pages=[(0,.4,"03-grid",0),(.5,1.3,"05-chapter",1),(1.8,.25,"03-grid",0),(2.05,2.7,"05-chapter",2),(4.75,.7,"03-grid",0)] if s.chapter==3 else [(0,.40,"03-grid",0),(.70,max(.1,s.duration-.70),"05-chapter",1)]
        base=5.7 if s.chapter==3 else 2.63
        factor=s.duration/base
        for j,(st,span,kind,num) in enumerate(pages):
            st*=factor;span*=factor
            nested=Scene(s.key(f"inner-{j}"),span,kind,s.project_config,num)
            (grid_six if kind=="03-grid" else chapter)(nested)
            contents=''.join(nested.html)
            s.add(f"nested-{j}",f'<div style="position:absolute;left:0;top:0;width:1920px;height:1080px;transform:scale(.61354167);transform-origin:0 0;background:#0b1121">{contents}</div>',"position:absolute;left:607px;top:316px;width:1178px;height:663px;overflow:hidden;background:#0b1121")
            s.fade(f"nested-{j}",st,.015)
            s.animate(f"nested-{j}",st+span-.025,.02,{"opacity":1},{"opacity":0})
            child_initial=''.join(f'gsap.set("#{nested.key(key)}",{json.dumps({prop:v[1] for prop,v in vals.items()})});' for key,vals in nested.initial_properties.items())
            child_code=(child_initial+''.join(nested.tweens)).replace('tl.','nestedTL.')
            s.tweens.append('{const nestedTL=gsap.timeline();'+child_code+f'tl.add(nestedTL,{st});'+'}')
    windows=''.join(s.html[group_start:])
    s.html[group_start:]=[]
    s.add("windows",windows,"position:absolute;inset:0")
    if s.duration>1.3:
        s.animate("windows",s.duration-.3,.28,
            {"clipPath":"polygon(0% 0%,100% 0%,100% 100%,0% 100%)","rotation":0,"x":0,"y":0},
            {"clipPath":"polygon(0% 0%,0% 0%,0% 0%,0% 0%)","rotation":-37,"x":-2400,"y":-900},"power2.in")
    s.nav()

def chapter(s):
    number=max(1,min(s.chapter or 1,6));name=NAMES[number-1]
    s.slot("background","background","inset:0;border:0;border-radius:0")
    pack_start=len(s.html)
    s.add("chapter-fill","","position:absolute;inset:0;background:linear-gradient(120deg,#091526,#20133e)")
    s.add("ribbons",'<svg width="1920" height="1080" viewBox="0 0 1920 1080"><path d="M-120 800C450 675 1070 820 1700 430L2000 185L2000 100C1550 140 1510 10 1130 80L2000 200L2000 500C1190 1070 720 700-120 850Z" fill="#020308"/><path d="M-90 815C250 760 420 960 650 1100M800 0C1200 40 1130 200 1800 60" stroke="#67569b" stroke-width="2" fill="none" opacity=".32"/></svg>',"position:absolute;inset:0")
    s.slot("preview","document","left:1190px;top:220px;width:680px;height:425px",True)
    s.add("number",f'{number:02d}',"position:absolute;left:50px;top:365px","outline-number")
    title=s.cfg.get("title",name)
    title_size=57 if len(title)>15 else 76
    s.add("title",f'<div class="eyebrow">CODEX / VIDEO SKILL</div><h1 class="chapter-title" style="font-size:{title_size}px;margin-top:28px">{text(title,28)}</h1>',"position:absolute;left:515px;top:305px;width:700px")
    s.add("copy",f'<p class="sub">{text(s.cfg.get("subtitle","把当前步骤交给合适的 Skill"),35)}</p><p class="label" style="margin-top:30px">通用用途</p><p class="card-copy" style="margin-top:22px">{text(s.cfg.get("body","输入资料与要求，留下可继续编辑的产物。"),48)}</p><div style="margin-top:28px"><span class="chip">输入 · 项目资料</span><span class="chip" style="margin-left:15px">输出 · 制作结果</span></div>',"position:absolute;left:515px;top:475px;width:660px")
    s.add("number-rule","","position:absolute;left:50px;top:650px;width:310px;height:2px;background:#8d79d3")
    s.fade("number-rule",.19,.25)
    s.fade("preview",.04,.24);s.fade("number",.19,.25);s.fade("title",.34,.22);s.fade("copy",.44,.22)
    pack=''.join(s.html[pack_start:]);s.html[pack_start:]=[]
    s.add("chapter-pack",pack,"position:absolute;inset:0;background:transparent")
    s.fade("chapter-pack",0,.18)
    s.animate("chapter-pack",max(.7,s.duration-.2),.18,{"opacity":1},{"opacity":0})
    s.nav(number)

def fan_five(s):
    s.slot("background","background","inset:0;border:0;border-radius:0")
    s.add("surface","","","surface")
    s.fade("surface",.08,.32)
    names=s.cfg.get("items",["知识讲解","产品介绍","导出成片","自动化流程","AI 能力"])
    if len(names)!=5:raise ValueError("五卡模板需要5项")
    coords=[(500,100,5),(1015,100,-4),(180,550,-6),(750,550,3),(1310,550,7)]
    for i,(x,y,angle) in enumerate(coords):
        cls="panel"
        icon='<svg width="66" height="66" viewBox="0 0 66 66"><rect x="2" y="2" width="62" height="62" rx="16" fill="#7768df"/><path d="M18 46V31h8v15m7 0V20h8v26m6 0V26h5v20" stroke="white" fill="none" stroke-width="2"/></svg>'
        paths=['<path d="M18 46V31h8v15m7 0V20h8v26m6 0V26h5v20"/>','<path d="M22 16H40L49 25V51H22ZM40 16V27H49M28 35H43M28 42H43"/>','<path d="M32 13V40M23 31L32 41L42 31M19 42V51H47V42"/>','<path d="M22 17H41V30H22ZM13 45H29V56H13ZM39 45H55V56H39ZM32 30V39M21 39H47M21 39V45M47 39V45"/>','<path d="M34 12L39 27L54 32L39 37L34 52L29 37L14 32L29 27ZM48 12L50 18L56 20L50 22L48 28L46 22L40 20L46 18Z"/>']
        icon=f'<svg width="66" height="66" viewBox="0 0 66 66"><rect x="2" y="2" width="62" height="62" rx="16" fill="#7768df"/><g stroke="white" fill="none" stroke-width="2">{paths[i]}</g></svg>'
        s.add(f"fan-{i}",icon+f'<h2 class="card-title" style="margin-top:28px">{text(names[i],15)}</h2><p class="card-copy" style="margin-top:22px">{text(s.cfg.get("card_bodies",["把知识变成清楚的动态讲解","展示新产品与使用方法","从内容直接导出 MP4","把常用步骤串成制作流程","让 AI 参与内容与视觉表达"])[i],35)}</p>',f'position:absolute;left:{x}px;top:{y}px;width:440px;height:400px;padding:38px;text-align:center;'+('background:#594bd0;' if i==2 else ''),cls)
        s.animate(f"fan-{i}",.05+i*.035,.58,{"x":760-x,"y":390-y,"scale":.58,"rotation":(-10+i*4),"opacity":0},{"x":0,"y":0,"scale":1,"rotation":angle,"opacity":1},"power2.inOut")
        s.animate(f"fan-{i}",.80, min(1.4,s.duration-.84),{"rotation":angle},{"rotation":angle+(-2 if i%2 else 2)},"sine.inOut")
    s.nav(1)

def takeaway(s):
    s.slot("background","background","inset:0;border:0;border-radius:0")
    s.add("shade","","position:absolute;inset:0;background:#08111b88")
    body=text(s.cfg.get("body","输入当前资料\n明确这一步的输出"),60).replace(chr(10),"<br>")
    sx,sy,sw,sh=s.cfg.get("summary_rect",[94,205,585,450])
    line=f'<div id="{s.key("summary-line")}" class="line"></div>'
    if s.cfg.get("summary_track"):
        line=f'<div style="height:5px;background:#46505e;margin-top:30px"><div id="{s.key("summary-line")}" style="height:5px;background:linear-gradient(90deg,#66d7ed,#b6ef4b);transform-origin:left center"></div></div>'
    s.add("summary",f'<div class="eyebrow">KEY TAKEAWAY</div><h1 class="heading">{text(s.cfg.get("title","从资料得到可用产物"),22)}</h1><p class="sub">{body}</p>{line}',f"left:{sx}px;top:{sy}px;width:{sw}px;min-height:{sh}px","takeaway")
    if s.chapter==2:
        s.slot("underlay","document","left:1210px;top:290px;width:610px;height:440px",True)
        s.fade("underlay",max(.1,s.duration-.65),.12)
    s.slot("screen","screen","left:675px;top:174px;width:1245px;height:700px",False)
    s.rise("screen",.03,.33,330);s.fade("summary",.08,.23)
    s.animate("summary-line",.24,s.cfg.get("line_duration",max(.2,s.duration-.65)),{"scaleX":0},{"scaleX":1},"none")
    if s.duration>2 or s.chapter==5:
        summary_exit=s.duration-.23 if s.chapter==2 else s.duration-.64
        if s.chapter==5:summary_exit=s.duration-.2
        screen_exit=s.duration-.53 if s.chapter==2 else s.duration-.48
        exit_cfg=s.cfg.get("exit",{})
        summary_exit=exit_cfg.get("summary_start",summary_exit)
        fade_duration=exit_cfg.get("fade_duration",.18)
        s.animate("summary",summary_exit,fade_duration,{"opacity":1},{"opacity":0})
        if s.chapter==2:
            s.animate("underlay",summary_exit,fade_duration,{"opacity":1},{"opacity":0})
        if s.cfg.get("page_peel"):
            px,py,pw,ph=s.cfg.get("media_rect",{}).get("screen",[675,174,1245,700])
            front=next(x for x in s.html if f'id="{s.key("screen")}"' in x)
            back=re.sub(r'id="([^"]+)"',lambda m:'id="'+m[1]+'-back"',front)
            s.html.remove(front)
            old=f"left:{px}px;top:{py}px;width:{pw}px;height:{ph}px"
            front=front.replace(old,f"left:0px;top:0px;width:{pw}px;height:{ph}px",1)
            back=back.replace(old,f"left:0px;top:0px;width:{pw}px;height:{ph}px;opacity:0",1)
            s.add("peel-host",front+back,f"position:absolute;left:{px}px;top:{py}px;width:{pw}px;height:{ph}px;overflow:hidden")
            peel=s.cfg["page_peel"];start=peel["start"];duration=peel["duration"]
            s.tweens.append('{const state={p:0};const draw=nanaPeel(document.getElementById("'+s.key("screen")+'"),document.getElementById("'+s.key("screen")+'-back"),'+str(pw)+','+str(ph)+');draw(0);tl.fromTo(state,{p:0},{p:1,duration:'+str(duration)+',ease:"'+peel.get("ease","power2.out")+'",immediateRender:false,onUpdate:()=>draw(state.p)},'+str(start)+');}')
            s.events.append(dict(id="screen-peel:0",selector="#"+s.key("screen"),start=start,duration=duration,before={"fold":0},after={"fold":1},ease=peel.get("ease","power2.out")))
        elif s.chapter!=5:
            s.animate("screen",screen_exit,.28,{"rotation":0,"x":0,"clipPath":"polygon(0% 0%,100% 0%,100% 100%,0% 100%)"},{"rotation":-27,"x":-2100,"clipPath":"polygon(0% 0%,0% 0%,0% 0%,0% 0%)"},"power2.in")
        else:
            s.animate("screen",exit_cfg.get("screen_start",s.duration-.2),fade_duration,{"opacity":1},{"opacity":0})
    s.nav()

def node_flow(s):
    s.slot("background","background","inset:0;border:0;border-radius:0")
    s.add("surface","","","surface");s.head("让资料进入制作流程","把输入、处理和输出放在同一张图里")
    s.add("circle",'<svg viewBox="0 0 500 500" width="500" height="500"><circle cx="250" cy="250" r="238" fill="#17303855" stroke="#3b7787" stroke-width="2"/></svg>',"position:absolute;left:650px;top:300px")
    s.add("left",'<svg width="115" height="115" viewBox="0 0 115 115"><rect x="2" y="2" width="110" height="110" rx="20" fill="#241c38" stroke="#cf80e6" stroke-width="3"/><path d="M57 25V90M25 57H90M34 34L81 81M34 81L81 34" stroke="#ca82d9" stroke-width="3"/></svg><div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;margin-top:30px">'+''.join(f'<span class="chip">{text(x)}</span>' for x in s.cfg.get("items",["接收素材","处理内容","整理字幕","交付结果"]))+'</div>',"position:absolute;left:120px;top:390px;width:510px")
    s.add("app",'<div class="window-bar"><i></i><i></i><i></i></div>',"position:absolute;left:720px;top:340px;width:1080px;height:560px","panel")
    coords=[(800,460,430,205),(1110,580,365,195),(1460,470,270,160)]
    for i,(x,y,w,h) in enumerate(coords):
        title=s.cfg.get("node_titles",["资料输入","指令处理","制作结果"])[i]
        s.add(f"node-{i}",f'<h2 class="card-title" style="font-size:27px">{text(title,14)}</h2><div style="height:6px;background:#b5bbc6;margin-top:28px;width:85%"></div><div style="height:6px;background:#d3d7df;margin-top:18px;width:65%"></div>',f'position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px',"white-card")
    s.add("cursor",'<svg viewBox="0 0 60 60" width="55" height="55"><path d="M5 5L48 23L30 31L23 48Z" fill="white"/></svg>',"position:absolute;left:1680px;top:810px")
    s.fade("surface",0,.2);s.fade("heading",0,.2);s.fade("left",.08,.2);s.fade("circle",.10,.2);s.fade("app",.16,.2)
    for i in range(3):s.fade(f"node-{i}",.23+i*.035,.18)
    s.add("node-marker","","position:absolute;left:1140px;top:715px;width:64px;height:65px;background:#ffd465")
    s.fade("node-marker",.265,.18)
    s.fade("cursor",.25,.2);s.nav()

def media_board(s):
    s.add("bg","","inset:0","grid-bg");s.head(s.cfg.get("title","图片、视频、音频全覆盖"),s.cfg.get("subtitle","缺少什么素材，就补充哪类素材"))
    boxes=[("document","document",110,350,420,440),("image","image",550,320,400,470),("video","video",970,320,440,245),("audio","audio",970,565,440,220)]
    for key,kind,x,y,w,h in boxes:
        s.slot(key,kind,f'left:{x}px;top:{y}px;width:{w}px;height:{h}px');s.fade(key,.14,.25)
    s.add("repo-label",'<div style="font-size:23px;color:white">GENERATIVE MEDIA SKILLS</div><div style="font-size:17px;color:#9caec4;margin-top:12px">图片、视频、音频统一管理</div>',"position:absolute;left:130px;top:680px;width:370px")
    s.fade("repo-label",.14,.25)
    s.add("list",'<div class="eyebrow">ASSET PACK</div>'+''.join(f'<div class="chip" style="margin-top:17px">{text(x)}</div>' for x in ["图像素材","视频片段","音频文件","版式字段","导出设置"]),"position:absolute;left:1460px;top:345px;width:350px;padding:28px;height:520px","panel")
    s.fade("heading",.02,.2);s.fade("list",.14,.25);s.nav(4);s.add("footer","","","footer")
    delay=min(1.32,s.duration*.42)
    s.animate("list",delay,.12,{"opacity":1},{"opacity":0})
    s.animate("image-media",delay,.12,{"opacity":1},{"opacity":0})
    for key in ("image","video"):
        if key in s.labeled_keys:s.animate(key+"-label",delay,.03,{"opacity":1},{"opacity":0})
    for key,kind,x,y,w,h in [("poster","poster",604,320,330,440),("wide","image",972,326,420,239),("portrait","video",1392,144,448,794)]:
        s.slot(key,kind,f'left:{x}px;top:{y}px;width:{w}px;height:{h}px');s.fade(key,delay,.16)

def media_overlay(s):
    s.slot("background","background","inset:0;border:0;border-radius:0")
    for key,kind,x,y,w,h in [("poster","poster",604,320,330,440),("wide","image",972,326,420,239),("portrait","video",1392,144,448,794)]:
        s.slot(key,kind,f'left:{x}px;top:{y}px;width:{w}px;height:{h}px')
        if s.duration>.4:s.fade(key,0,.08)
        s.animate(key,max(.02,s.duration-.18),.15,{"opacity":1},{"opacity":0})
    s.nav(4)

def storyboard(s):
    s.add("paper","","position:absolute;inset:0;background:#f7f2da")
    s.add("title",f'<p style="color:#697064;font-size:22px;letter-spacing:4px">IDEA / STORYBOARD / VIDEO</p><h1 style="font-size:52px;color:#23283a;margin-top:18px">{text(s.cfg.get("title","把一个创意拆成三个镜头"),25)}</h1>',"position:absolute;left:190px;right:190px;top:160px;text-align:center")
    s.add("frame","","position:absolute;left:90px;right:90px;top:320px;height:580px;border:3px solid #68625a;border-radius:24px")
    for key,kind,x,w in [("idea","idea",150,365),("frames","filmstrip",637,601),("result","video",1330,470)]:
        s.slot(key,kind,f'left:{x}px;top:398px;width:{w}px;height:405px;border:0;border-radius:18px;background:transparent')
    for i,x in enumerate([570,1250]):s.add(f"arrow-{i}",'<svg width="86" height="70" viewBox="0 0 86 70"><path d="M3 25H49V5L82 35L49 65V45H3Z" fill="#aaa0d7" stroke="#56506e" stroke-width="3"/></svg>',f'position:absolute;left:{x}px;top:520px')
    for i,(x,label) in enumerate([(265,"视频创意"),(850,"15秒分镜"),(1400,"Seedance 成片")]):s.add(f"label-{i}",text(label),f'position:absolute;left:{x}px;top:805px;background:#fffdf4;border:2px solid #ada892;color:#3b355a;border-radius:30px;padding:12px 35px;font-size:26px')
    s.fade("title",.02,.14);s.fade("frame",.13,.18)
    for key in ["idea","frames","result","arrow-0","arrow-1","label-0","label-1","label-2"]:s.fade(key,.2,.18)
    s.nav(6)

def smash_title(s):
    s.slot("background","background","inset:0;border:0;border-radius:0")
    s.add("smash",text(s.cfg.get("title","让创意变成视频"),16),"position:absolute;left:90px;right:90px;top:425px;text-align:center;white-space:nowrap;font-size:142px;font-weight:900;text-shadow:0 8px 2px #0008",attrs='data-layout-allow-overflow')
    s.animate("smash",0,.38,{"scale":7,"opacity":1},{"scale":1,"opacity":1},"power3.out")
    s.animate("smash",max(.5,s.duration-.36),.32,{"x":0,"opacity":1},{"x":1600,"opacity":0},"power2.in")
    s.nav(6)

def workflow_badge(s,overlay=False):
    if not overlay:
        s.add("bg","","inset:0","grid-bg");s.head("把工具串成自己的流程");s.grid();s.nav(0)
    delay=2.77 if overlay else .15
    if overlay and s.duration<delay+.8:return
    s.add("badge",f'<div id="{s.key("badge-text")}" class="badge-text">{text(s.cfg.get("badge_text","专属工作流"),10)}</div><div class="badge-square"></div><svg class="badge-check" viewBox="0 0 140 140"><path id="{s.key("badge-check")}" d="M20 70L58 105L123 28" pathLength="1"/></svg>',"","badge")
    s.animate("badge",delay,.19,{"scale":.62,"opacity":0},{"scale":1,"opacity":1})
    s.animate("badge-text",delay+.10,.25,{"clipPath":"inset(0% 100% 0% 0%)"},{"clipPath":"inset(0% 0% 0% 0%)"},"none")
    reset=delay+1.50
    if reset<s.duration-.2:
        s.tweens.append(f'tl.set("#{s.key("badge-check")}",{{strokeDashoffset:1}},{reset});')
    for t in [delay+.22,delay+1.70]:
        if t<s.duration-.15:s.animate("badge-check",t,.18,{"strokeDashoffset":1},{"strokeDashoffset":0},"none")

def pipeline_five(s):
    s.add("bg","","inset:0","grid-bg");s.head("一条可以复用的制作流程","按步骤留下清楚的中间产物")
    s.grid(5,True);s.fade("body",0,.12);s.fade("heading",.02,.17)
    for i in range(5):s.fade(f"card-{i}",.12+i*.065,.18)
    s.add("footer","","","footer");s.nav(7)
    s.animate("body",max(.7,s.duration-.18),.16,{"opacity":1},{"opacity":0})

def chapter_nav(s):
    s.add("bg","","inset:0","grid-bg");s.head("让当前章节一眼可见","固定导航位置，只切换当前章节")
    s.nav(1)
    for i in range(6):
        s.add(f"section-{i}",f'{i+1:02d}  {text(NAMES[i])}',f'position:absolute;left:120px;top:430px;font-size:100px;font-weight:700')
        s.fade(f"section-{i}",i*s.duration/6,.06)
        if i<5:s.animate(f"section-{i}",(i+1)*s.duration/6-.06,.05,{"opacity":1},{"opacity":0})
    # 独立导航示例中的活动色块分段切换；正文中由各场景chapter字段定位。
    for i in range(1,7):
        s.tweens.append(f'tl.set("#{s.key("nav")} span",{{background:"transparent",color:"#becbe0"}},{(i-1)*s.duration/6});tl.set("#{s.key("nav")} span:nth-child({i+1})",{{background:"{s.nav_accent}",color:"#f9f8ff"}},{(i-1)*s.duration/6});')

def media_slot(s):
    s.slot("media","background","inset:0;border:0;border-radius:0");s.nav()
    if not s.project_config.get("recreation") and not s.cfg.get("media",{}).get("media"):
        s.add("slot-label",'<h1 style="font-size:76px">全幅媒体插槽</h1><p class="sub" style="margin-top:26px">替换为你自己的连续原速视频</p>',"position:absolute;left:200px;right:200px;top:430px;text-align:center")

FUNCTIONS = dict(zip([t["id"] for t in TEMPLATES],[title_intro,media_flip,grid_six,browser_stack,chapter,fan_five,takeaway,node_flow,media_board,media_overlay,storyboard,smash_title,workflow_badge,pipeline_five,chapter_nav]))
FUNCTIONS["media-slot"]=media_slot

def write_scene(folder, shot, config):
    s=Scene(shot["id"],shot["duration"],shot["template"],config,shot.get("chapter",1),shot.get("label",""))
    FUNCTIONS[shot["template"]](s)
    dst=folder/"compositions"/(s.id+".html");dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(s.finish())
    events=folder/"motion-params"/(s.id+".json");events.parent.mkdir(exist_ok=True)
    events.write_text(json.dumps(s.events,ensure_ascii=False,indent=2)+"\n")
    return s

def root_html(shots, duration, config=None):
    config=config or {}
    hosts='\n'.join(f'<div id="{s["id"]}" class="clip" data-composition-id="{s["id"]}" data-composition-src="compositions/{s["id"]}.html" data-start="{s["start"]:.8f}" data-duration="{s["duration"]:.8f}" data-track-index="1" data-track-kind="graphics" data-width="1920" data-height="1080"></div>' for s in shots)
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="UTF-8"><title>Codex 视频 MG 模板</title><script src="assets/vendor/gsap.min.js"></script><script src="assets/runtime/diagonal-peel.js"></script><style>html,body{{margin:0;width:1920px;height:1080px;background:#090f1f;overflow:hidden}}#root{{position:absolute;inset:0}}</style></head><body><div id="root" data-composition-id="main" data-start="0" data-duration="{duration}" data-width="1920" data-height="1080" data-fps="30">{hosts}{config.get("root_media_html", "")}</div><script>window.__timelines=window.__timelines||{{}};window.__timelines.main=gsap.timeline({{paused:true}});</script></body></html>'''

def build_project(folder, shots, config):
    folder.mkdir(parents=True,exist_ok=True)
    if folder!=ENGINE:
        shutil.copytree(ENGINE/"assets",folder/"assets",dirs_exist_ok=True)
        for f in ["hyperframes.json","package.json"]:shutil.copy2(ENGINE/f,folder/f)
    for shot in shots:write_scene(folder,shot,config)
    (folder/"index.html").write_text(root_html(shots,max(s["start"]+s["duration"] for s in shots),config))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",type=Path,default=P/"配置.json")
    parser.add_argument("--template",choices=list(FUNCTIONS))
    parser.add_argument("--output",type=Path)
    parser.add_argument("--duration",type=float,default=4.0)
    parser.add_argument("--chapter",type=int,choices=range(1,7),default=1)
    args=parser.parse_args();config=read_config(args.config)
    if args.template:
        if not args.output:parser.error("独立导出必须给 --output，避免覆盖完整工程")
        if args.output.resolve()==ENGINE.resolve():parser.error("不能用独立模块覆盖完整工程")
        if not .8<=args.duration<=60:parser.error("时长范围为0.8–60秒")
        shots=[dict(id="module",template=args.template,start=0,duration=args.duration,chapter=args.chapter)]
        build_project(args.output,shots,config)
    elif args.output:
        build_project(args.output,PLAN["shots"],config)
    else:
        build_project(ENGINE,PLAN["shots"],config)
        gallery=[dict(id="library-"+t["id"],template=t["id"],start=i*4,duration=4,chapter=1) for i,t in enumerate(TEMPLATES)]
        build_project(P/"模板总览",gallery,config)
    print("构建完成；动态输出遵循当前授权及实际检查状态。")

if __name__=="__main__":main()
