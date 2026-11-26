"""三媒体悬浮；从nana mg1已验证动作源码拆分。"""
from runtime import *

def media_overlay(s):
    s.slot("background","background","inset:0;border:0;border-radius:0")
    for key,kind,x,y,w,h in [("poster","poster",604,320,330,440),("wide","image",972,326,420,239),("portrait","video",1392,144,448,794)]:
        s.slot(key,kind,f'left:{x}px;top:{y}px;width:{w}px;height:{h}px')
        if s.duration>.4:s.fade(key,0,.08)
        s.animate(key,max(.02,s.duration-.18),.15,{"opacity":1},{"opacity":0})
    s.nav(4)

build=media_overlay
