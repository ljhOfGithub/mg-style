"""共享绘制原语；不读取原片计划、模板索引、章节预设或任何整片配置。"""
from pathlib import Path
from html import escape
import json,re,unicodedata,math
NAMES=["资料收集","内容整理","视觉设计","检查修改","导出分享","归档复用"]
def fit_font(value,maximum,width,minimum=20):
    units=sum(1 if unicodedata.east_asian_width(ch) in 'WF' else .62 for ch in str(value))
    return round(max(minimum,min(maximum,width/max(1,units))),2)
CSS = r"""+@font-face{font-family:'MG Sans';src:url('assets/fonts/PingFangSC-Medium.ttf')}*{box-sizing:border-box}#root{position:absolute;inset:0;color:#f4f7ff;font-family:'MG Sans',sans-serif;overflow:hidden;background:#080e1a}h1,h2,h3,p{margin:0} .stage{position:absolute;inset:0;overflow:hidden;background:radial-gradient(ellipse at 9% 85%,#12404965,transparent 48%),radial-gradient(ellipse at 92% 66%,#391f6766,transparent 52%),#090f1f}.grid-bg{position:absolute;inset:0;background-image:linear-gradient(#78b0ca14 1px,transparent 1px),linear-gradient(90deg,#78b0ca14 1px,transparent 1px);background-size:72px 72px}.eyebrow{color:var(--accent);font-size:22px;letter-spacing:4px}.heading{font-size:52px;font-weight:700;line-height:1.2}.sub{color:#c0cce1;font-size:27px;line-height:1.6}.tiny{font-size:22px;color:#acb6cb}.panel{border:2px solid #6a789b75;border-radius:14px;background:#10182be6}.slot{width:100%;height:100%;object-fit:contain;display:block}.slot-box{position:absolute;overflow:hidden;border:2px solid #798caa8a;border-radius:16px;background:#101a2d}.window-bar{position:absolute;top:0;left:0;right:0;height:32px;display:flex;align-items:center;gap:9px;padding-left:18px;background:#101625;border-bottom:1px solid #5d70935c}.window-bar i{width:8px;height:8px;border-radius:100%;background:#b39af4}.window-body{position:absolute;inset:34px 0 0}.card-title{font-size:32px;font-weight:700;line-height:1.3}.card-copy{font-size:24px;line-height:1.5;color:#d3daeb}.line{height:2px;background:var(--accent);transform-origin:left center}.footer{position:absolute;left:110px;right:110px;bottom:70px;height:2px;background:linear-gradient(90deg,#64bfd3,#7454bb)}.label{display:inline-block;padding:10px 20px;border:1px solid #8c7ed777;border-radius:7px;background:#6651bc33;font-size:23px}.chip{padding:9px 17px;border:1px solid #6d8ca777;color:#d4ebf2;font-size:22px}.placeholder-base{position:absolute;inset:0;background:#101a2d}.placeholder-base img{width:100%;height:100%;object-fit:cover}.surface{position:absolute;inset:0;background:#090d16e8}.heading-wrap{position:absolute;left:120px;right:120px;top:150px}.grid-card{position:absolute;border:2px solid #566b9477;background:linear-gradient(145deg,#0c1e35,#1c1435);padding:52px 35px}.grid-card .n{font-size:29px;color:var(--accent);margin-bottom:22px}.grid-card .rule{margin:22px 0;width:88px;height:2px;background:#8b72dc}.nav{position:absolute;left:78px;right:78px;top:20px;height:40px;display:flex;align-items:center;border:1px solid #518a9b88;border-radius:7px;background:#08131de8;padding:4px;gap:6px}.nav span{flex:1;text-align:center;font-size:18px;color:#becbe0;padding:5px 3px;border-radius:4px}.nav .active{background:var(--accent);color:#101423}.ribbon{position:absolute;border-radius:50%;background:#1b1643;border:1px solid #7d65a94d}.white-card{background:#fffef3;color:#1c2432;border-radius:14px;border:2px solid #c6cad3;padding:30px}.white-card .card-copy{color:#495166}.outline-number{font-size:270px;line-height:1;color:transparent;-webkit-text-stroke:2px #a995ff}.chapter-title{font-size:70px;line-height:1.1;letter-spacing:-2px;font-weight:700;white-space:nowrap}.media-caption{position:absolute;bottom:12px;left:18px;font-size:20px;color:#b5c2db}.badge{position:absolute;width:700px;height:174px;right:120px;top:92px;background:#fffdf7;border-radius:16px;display:flex;align-items:center;padding:28px 190px 28px 42px;color:#12151b}.badge-text{font-size:50px;font-weight:900;white-space:nowrap;font-style:italic}.badge-square{position:absolute;right:26px;top:24px;width:126px;height:126px;background:#252930;border-radius:14px}.badge-check{position:absolute;right:12px;top:16px;width:140px;height:140px}.badge-check path{fill:none;stroke:#8bf96b;stroke-width:19;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1}.takeaway{position:absolute;left:94px;top:205px;width:585px;min-height:450px;background:#0e1722f2;border:2px solid #53677b88;border-radius:18px;padding:72px 42px 30px}.takeaway .eyebrow{font-size:40px;font-weight:700}.takeaway .heading{font-size:42px;margin:27px 0}.takeaway .line{margin-top:30px}.source-hold{position:absolute;right:110px;bottom:62px;color:#a8b7ce;font-size:20px}
""".replace("+@font", "@font").replace("PingFangSC-Medium.ttf", "NotoSansSC.ttf").replace(".heading-wrap{position:absolute;left:120px;right:120px;top:150px}", ".heading-wrap{position:absolute;left:120px;right:120px;top:120px}")

def text(value, limit=100):
    value = str(value)
    if len(value) > limit:
        raise ValueError(f"文字过长（最多{limit}字）：{value[:30]}")
    return escape(value)

class Scene:
    def __init__(self, ident, duration, template, config, chapter=1, label=""):
        self.id, self.duration, self.template = ident, duration, template
        self.cfg = dict(config.get("templates", {}).get(template, {}))

        self.cfg.update(config.get("shots",{}).get(ident,{}))
        self.project_config=config
        self.accent = config.get("accent", "#90ddf1")
        self.nav_accent = config.get("nav_accent", "#7256bc")
        self.chapter, self.label = chapter, label
        self.html, self.tweens = [], []
        self.animated_keys = set()
        self.initial_properties = {}
        self.key_counts, self.events = {}, []
        self.labeled_keys=set()

    def key(self, key):
        return self.id + "-" + key

    def add(self, key, markup, style="", cls="", attrs=""):
        self.html.append(f'<div data-nana-object="{key}" id="{self.key(key)}" class="{cls}" style="{style}" {attrs}>{markup}</div>')

    def animate(self, key, start, duration, before, after, ease="power2.out"):
        # 上游01-flat-vector的独立t0和归一化时间组织，适配到GSAP seek-safe fromTo。
        count=self.key_counts.get(key,0);self.key_counts[key]=count+1
        event_id=f"{key}:{count}"
        override=self.cfg.get("motions",{}).get(event_id,{})
        start=override.get("start",start);duration=override.get("duration",duration)
        if override and start+duration>self.duration:
            raise ValueError(f"{event_id}动作超出模块时长：{start}+{duration}>{self.duration}")
        if not math.isfinite(start+duration) or start<0 or duration<=0 or start+duration>self.duration+.001:
            raise ValueError(f"{event_id}动作超出组件时长：{start}+{duration}>{self.duration}")
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
        position=options.get("position","center")
        ext = Path(src).suffix.lower()
        if ext in (".mp4", ".mov", ".webm"):
            media = f'<video id="{self.key(key)}-video" class="clip slot" data-start="0" data-duration="{self.duration}" data-track-index="2" src="{text(src)}" muted playsinline></video>'
        else:
            media = f'<img id="{self.key(key)}-media" class="slot" style="object-position:{text(position)};object-fit:{text(options.get("fit","contain"))}" src="{text(src)}" alt="可替换媒体" />'
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

    def head(self, title, subtitle="", eyebrow="NANA / MOTION COMPONENT"):
        eyebrow=self.cfg.get("eyebrow",eyebrow)
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
        if not self.project_config.get("show_nav",False):return
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

CSS+="\n.heading,.card-title,.sub,.card-copy{overflow-wrap:anywhere}.slot{object-position:center}.nav span{font-size:20px}.takeaway{padding:48px 32px 30px}.takeaway .heading{margin:24px 0}.grid-card .tiny{font-size:22px!important}.grid-card .card-title{font-size:28px}.badge{right:610px;top:400px}.badge-text{font-size:46px}.takeaway .sub{font-size:24px;line-height:1.5}"
