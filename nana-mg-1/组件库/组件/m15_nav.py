"""章节导航；从nana mg1已验证动作源码拆分。"""
from runtime import *

def chapter_nav(s):
    s.add("bg","","inset:0","grid-bg");s.head("让当前章节一眼可见","固定导航位置，只切换当前章节")
    s.nav(1)
    for i in range(len(NAMES)):
        s.add(f"section-{i}",f'{i+1:02d}  {text(NAMES[i])}',f'position:absolute;left:120px;top:430px;font-size:100px;font-weight:700')
        s.fade(f"section-{i}",i*s.duration/len(NAMES),.06)
        if i<len(NAMES)-1:s.animate(f"section-{i}",(i+1)*s.duration/len(NAMES)-.06,.05,{"opacity":1},{"opacity":0})
    # 独立导航示例中的活动色块分段切换；正文中由各场景chapter字段定位。
    for i in range(1,len(NAMES)+1):
        s.tweens.append(f'tl.set("#{s.key("nav")} span",{{background:"transparent",color:"#becbe0"}},{(i-1)*s.duration/len(NAMES)});tl.set("#{s.key("nav")} span:nth-child({i+1})",{{background:"{s.nav_accent}",color:"#f9f8ff"}},{(i-1)*s.duration/len(NAMES)});')

build=chapter_nav
