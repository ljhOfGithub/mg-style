"""居中标题；从nana mg1已验证动作源码拆分。"""
from runtime import *

def title_intro(s):
    s.slot("background","background","inset:0;border:0;border-radius:0")
    s.add("shade","","position:absolute;inset:0;background:#060b17a8")
    s.add("hero",f'<p class="eyebrow">NANA · MOTION LIBRARY</p><h1 style="font-size:{fit_font(s.cfg.get("title","用 Codex 串起视频制作"),106,1560)}px;margin-top:20px;white-space:nowrap">{text(s.cfg.get("title","用 Codex 串起视频制作"),24)}</h1>',"position:absolute;left:140px;right:140px;top:360px;text-align:center")
    s.add("subtitle",f'<p class="sub">{text(s.cfg.get("subtitle","六项 Skills，组合你的制作流程"),45)}</p>',"position:absolute;left:220px;right:220px;top:550px;text-align:center")
    s.add("tags",'<span class="chip">可复用动画</span><span class="chip" style="margin-left:18px">MG</span>',"position:absolute;left:580px;top:635px")
    s.animate("hero",.06,.24,{"scale":.78,"opacity":0},{"scale":1,"opacity":1})
    s.rise("subtitle",.28,.18,16);s.fade("tags",.38,.18);s.nav(0)

build=title_intro
