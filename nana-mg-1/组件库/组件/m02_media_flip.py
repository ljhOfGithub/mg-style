"""媒体窗斜向翻出；从nana mg1已验证动作源码拆分。"""
from runtime import *

def media_flip(s):
    s.slot("background","background","inset:0;border:0;border-radius:0")
    s.slot("screen","screen","left:250px;top:150px;width:1420px;height:830px",True)
    s.rise("screen",0,.38,480)
    end=max(.55,s.duration-.42)
    # 斜边遮罩与整体旋转共同产生原片纸页般的退出，不虚称真实曲面卷页。
    s.animate("screen",end,.36,{"clipPath":"polygon(0% 0%,100% 0%,100% 100%,0% 100%)","rotation":0,"x":0,"y":0},
        {"clipPath":"polygon(0% 0%,0% 0%,0% 0%,0% 0%)","rotation":-38,"x":-2200,"y":-900},"power2.in")
    s.nav()

build=media_flip
