"""五卡展开；从nana mg1已验证动作源码拆分。"""
from runtime import *

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
        opt=s.cfg.get('slot_options',{}).get(f'card-{i}',{})
        ref=s.cfg.get('layout')=='reference';size=110 if ref else 66
        image_style=f'width:{size}px;height:{size}px;object-fit:'+opt.get('fit','contain')+';object-position:'+opt.get('position','center')+';border-radius:'+str(opt.get('radius',0))+'px;background:'+opt.get('background','transparent')+';border:'+opt.get('border','0')
        icon=(f'<img src="{text(s.cfg["media"][f"card-{i}"])}" style="{escape(image_style)}"/>' if f"card-{i}" in s.cfg.get("media",{}) else icon)
        title_margin=20 if ref else 28;body_margin=14 if ref else 22;padding=30 if ref else 38
        s.add(f"fan-{i}",icon+f'<h2 class="card-title" style="margin-top:{title_margin}px">{text(names[i],15)}</h2><p class="card-copy" style="margin-top:{body_margin}px;'+('font-size:22px;color:#f4f7ff;' if ref else '')+f'">{text(s.cfg.get("card_bodies",["把知识变成清楚的动态讲解","展示新产品与使用方法","从内容直接导出 MP4","把常用步骤串成制作流程","让 AI 参与内容与视觉表达"])[i],56)}</p>',f'position:absolute;left:{x}px;top:{y}px;width:440px;height:400px;padding:{padding}px;text-align:center;'+('background:#594bd0;' if i==2 else ''),cls)
        s.animate(f"fan-{i}",.05+i*.035,.58,{"x":760-x,"y":390-y,"scale":.58,"rotation":(-10+i*4),"opacity":0},{"x":0,"y":0,"scale":1,"rotation":angle,"opacity":1},"power2.inOut")
        s.animate(f"fan-{i}",.80, min(1.4,s.duration-.84),{"rotation":angle},{"rotation":angle+(-2 if i%2 else 2)},"sine.inOut")
    s.nav(1)

build=fan_five
