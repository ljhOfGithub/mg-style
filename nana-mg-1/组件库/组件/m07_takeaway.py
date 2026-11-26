"""摘要与双层翻页；从nana mg1已验证动作源码拆分。"""
from runtime import *

def takeaway(s):
    s.slot("background","background","inset:0;border:0;border-radius:0")
    s.add("shade","","position:absolute;inset:0;background:#08111b88")
    body=text(s.cfg.get("body","输入当前资料\n明确这一步的输出"),60).replace(chr(10),"<br>")
    sx,sy,sw,sh=s.cfg.get("summary_rect",[94,205,585,450])
    line=f'<div id="{s.key("summary-line")}" class="line"></div>'
    if s.cfg.get("summary_track"):
        line=f'<div style="height:5px;background:#46505e;margin-top:30px"><div id="{s.key("summary-line")}" style="height:5px;background:linear-gradient(90deg,#66d7ed,#b6ef4b);transform-origin:left center"></div></div>'
    s.add("summary",f'<div class="eyebrow">KEY TAKEAWAY</div><h1 class="heading" style="font-size:{fit_font(s.cfg.get("title","从资料得到可用产物"),42,sw-68,24)}px">{text(s.cfg.get("title","从资料得到可用产物"),22)}</h1><p class="sub">{body}</p>{line}',f"left:{sx}px;top:{sy}px;width:{sw}px;min-height:{sh}px","takeaway")
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

build=takeaway
