"""三步故事板；从nana mg1已验证动作源码拆分。"""
from runtime import *

def storyboard(s):
    s.add("paper","","position:absolute;inset:0;background:#f7f2da")
    s.add("title",f'<p style="color:#697064;font-size:22px;letter-spacing:4px">IDEA / STORYBOARD / VIDEO</p><h1 style="font-size:52px;color:#23283a;margin-top:18px">{text(s.cfg.get("title","把一个创意拆成三个镜头"),25)}</h1>',"position:absolute;left:190px;right:190px;top:160px;text-align:center")
    s.add("frame","","position:absolute;left:90px;right:90px;top:320px;height:580px;border:3px solid #68625a;border-radius:24px")
    for key,kind,x,w in [("idea","idea",150,365),("frames","filmstrip",637,601),("result","video",1330,470)]:
        s.slot(key,kind,f'left:{x}px;top:398px;width:{w}px;height:405px;border:0;border-radius:18px;background:transparent')
    for i,x in enumerate([570,1250]):s.add(f"arrow-{i}",'<svg width="86" height="70" viewBox="0 0 86 70"><path d="M3 25H49V5L82 35L49 65V45H3Z" fill="#aaa0d7" stroke="#56506e" stroke-width="3"/></svg>',f'position:absolute;left:{x}px;top:520px')
    for i,(x,label) in enumerate(list(zip([265,850,1400],s.cfg.get("labels",["收集资料","整理结构","得到结果"])))):s.add(f"label-{i}",text(label),f'position:absolute;left:{x}px;top:805px;background:#fffdf4;border:2px solid #ada892;color:#3b355a;border-radius:30px;padding:12px 35px;font-size:26px')
    s.fade("title",.02,.14);s.fade("frame",.13,.18)
    for key in ["idea","frames","result","arrow-0","arrow-1","label-0","label-1","label-2"]:s.fade(key,.2,.18)
    s.nav(6)

build=storyboard
