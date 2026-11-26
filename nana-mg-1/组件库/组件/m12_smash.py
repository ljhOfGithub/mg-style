"""大字强调；从nana mg1已验证动作源码拆分。"""
from runtime import *

def smash_title(s):
    s.slot("background","background","inset:0;border:0;border-radius:0")
    size=fit_font(s.cfg.get("title","让创意变成视频"),142,1620)
    s.add("smash",text(s.cfg.get("title","让创意变成视频"),16),f"position:absolute;left:90px;right:90px;top:425px;text-align:center;white-space:nowrap;font-size:{size}px;font-weight:900;text-shadow:0 8px 2px #0008",attrs='data-layout-allow-overflow')
    s.animate("smash",0,.38,{"scale":7,"opacity":1},{"scale":1,"opacity":1},"power3.out")
    s.animate("smash",max(.5,s.duration-.36),.32,{"x":0,"opacity":1},{"x":1600,"opacity":0},"power2.in")
    s.nav(6)

build=smash_title
