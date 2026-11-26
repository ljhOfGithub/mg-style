"""文档与预览叠窗；从nana mg1已验证动作源码拆分。"""
from runtime import *
from modules.m03_grid import grid_six
from modules.m05_chapter import chapter

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

build=browser_stack
