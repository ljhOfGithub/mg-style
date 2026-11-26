"""五步生产链；从nana mg1已验证动作源码拆分。"""
from runtime import *

def pipeline_five(s):
    s.add("bg","","inset:0","grid-bg");s.head("一条可以复用的制作流程","按步骤留下清楚的中间产物")
    s.grid(5,True);s.fade("body",0,.12);s.fade("heading",.02,.17)
    for i in range(5):s.fade(f"card-{i}",.12+i*.065,.18)
    s.add("footer","","","footer");s.nav(7)
    s.animate("body",max(.7,s.duration-.18),.16,{"opacity":1},{"opacity":0})

build=pipeline_five
