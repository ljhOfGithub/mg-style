"""输入输出节点；从nana mg1已验证动作源码拆分。"""
from runtime import *

def node_flow(s):
    s.slot("background","background","inset:0;border:0;border-radius:0")
    s.add("surface","","","surface");s.head("让资料进入制作流程","把输入、处理和输出放在同一张图里")
    s.add("circle",'<svg viewBox="0 0 500 500" width="500" height="500"><circle cx="250" cy="250" r="238" fill="#17303855" stroke="#3b7787" stroke-width="2"/></svg>',"position:absolute;left:650px;top:300px")
    s.add("left",'<svg width="115" height="115" viewBox="0 0 115 115"><rect x="2" y="2" width="110" height="110" rx="20" fill="#241c38" stroke="#cf80e6" stroke-width="3"/><path d="M57 25V90M25 57H90M34 34L81 81M34 81L81 34" stroke="#ca82d9" stroke-width="3"/></svg><div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;margin-top:30px">'+''.join(f'<span class="chip">{text(x)}</span>' for x in s.cfg.get("items",["接收素材","处理内容","整理字幕","交付结果"]))+'</div>',"position:absolute;left:120px;top:390px;width:510px")
    s.add("app",'<div class="window-bar"><i></i><i></i><i></i></div>',"position:absolute;left:720px;top:340px;width:1080px;height:560px","panel")
    coords=[(800,460,430,205),(1110,580,365,195),(1460,470,270,160)]
    for i,(x,y,w,h) in enumerate(coords):
        title=s.cfg.get("node_titles",["资料输入","指令处理","制作结果"])[i]
        s.add(f"node-{i}",f'<h2 class="card-title" style="font-size:{fit_font(title,27,w-64)}px">{text(title,14)}</h2><div style="height:6px;background:#b5bbc6;margin-top:28px;width:85%"></div><div style="height:6px;background:#d3d7df;margin-top:18px;width:65%"></div>',f'position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px',"white-card")
    s.add("cursor",'<svg viewBox="0 0 60 60" width="55" height="55"><path d="M5 5L48 23L30 31L23 48Z" fill="white"/></svg>',"position:absolute;left:1680px;top:810px")
    s.fade("surface",0,.2);s.fade("heading",0,.2);s.fade("left",.08,.2);s.fade("circle",.10,.2);s.fade("app",.16,.2)
    for i in range(3):s.fade(f"node-{i}",.23+i*.035,.18)
    s.add("node-marker","","position:absolute;left:1140px;top:715px;width:64px;height:65px;background:#ffd465")
    s.fade("node-marker",.265,.18)
    s.fade("cursor",.25,.2);s.nav()

build=node_flow
