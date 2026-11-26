"""媒体分区；从nana mg1已验证动作源码拆分。"""
from runtime import *

def media_board(s):
    s.add("bg","","inset:0","grid-bg");s.head(s.cfg.get("title","图片、视频、音频全覆盖"),s.cfg.get("subtitle","缺少什么素材，就补充哪类素材"))
    boxes=[("document","document",110,350,420,440),("image","image",550,320,400,470),("video","video",970,320,440,245),("audio","audio",970,565,440,220)]
    for key,kind,x,y,w,h in boxes:
        s.slot(key,kind,f'left:{x}px;top:{y}px;width:{w}px;height:{h}px');s.fade(key,.14,.25)
    s.add("repo-label",'<div style="font-size:23px;color:white">MEDIA COLLECTION</div><div style="font-size:17px;color:#9caec4;margin-top:12px">多种资料按内容归类</div>',"position:absolute;left:130px;top:680px;width:370px")
    s.fade("repo-label",.14,.25)
    s.add("list",'<div class="eyebrow">ASSET PACK</div>'+''.join(f'<div class="chip" style="margin-top:17px">{text(x)}</div>' for x in s.cfg.get("list_items",["图像资料","视频片段","音频文件","版式字段","导出设置"])),"position:absolute;left:1460px;top:345px;width:350px;padding:28px;height:520px","panel")
    s.fade("heading",.02,.2);s.fade("list",.14,.25);s.nav(4);s.add("footer","","","footer")
    delay=min(1.32,s.duration*.42)
    s.animate("list",delay,.12,{"opacity":1},{"opacity":0})
    s.animate("image-media",delay,.12,{"opacity":1},{"opacity":0})
    for key in ("image","video"):
        if key in s.labeled_keys:s.animate(key+"-label",delay,.03,{"opacity":1},{"opacity":0})
    for key,kind,x,y,w,h in [("poster","poster",604,320,330,440),("wide","image",972,326,420,239),("portrait","video",1392,144,448,794)]:
        s.slot(key,kind,f'left:{x}px;top:{y}px;width:{w}px;height:{h}px');s.fade(key,delay,.16)

build=media_board
