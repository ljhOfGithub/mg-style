"""编号章节卡；从nana mg1已验证动作源码拆分。"""
from runtime import *

def chapter(s):
    number=max(1,min(s.chapter or 1,6));name=NAMES[number-1]
    s.slot("background","background","inset:0;border:0;border-radius:0")
    pack_start=len(s.html)
    s.add("chapter-fill","","position:absolute;inset:0;background:linear-gradient(120deg,#091526,#20133e)")
    s.add("ribbons",'<svg width="1920" height="1080" viewBox="0 0 1920 1080"><path d="M-120 800C450 675 1070 820 1700 430L2000 185L2000 100C1550 140 1510 10 1130 80L2000 200L2000 500C1190 1070 720 700-120 850Z" fill="#020308"/><path d="M-90 815C250 760 420 960 650 1100M800 0C1200 40 1130 200 1800 60" stroke="#67569b" stroke-width="2" fill="none" opacity=".32"/></svg>',"position:absolute;inset:0")
    s.slot("preview","document","left:1190px;top:220px;width:680px;height:425px",True)
    s.add("number",f'{number:02d}',"position:absolute;left:50px;top:365px","outline-number")
    title=s.cfg.get("title",name)
    title_size=fit_font(title,76,650,24)
    s.add("title",f'<div class="eyebrow">{text(s.cfg.get("eyebrow","NANA / CHAPTER"),30)}</div><h1 class="chapter-title" style="font-size:{title_size}px;margin-top:28px">{text(title,28)}</h1>',"position:absolute;left:515px;top:305px;width:700px")
    s.add("copy",f'<p class="sub">{text(s.cfg.get("subtitle","把当前步骤交给合适的 Skill"),35)}</p><p class="label" style="margin-top:30px">{text(s.cfg.get("usage_label","通用用途"),12)}</p><p class="card-copy" style="margin-top:22px">{text(s.cfg.get("body","输入资料与要求，留下可继续编辑的产物。"),48)}</p><div style="margin-top:28px"><span class="chip">{text(s.cfg.get("input_label","输入 · 当前资料"),24)}</span><span class="chip" style="margin-left:15px">{text(s.cfg.get("output_label","输出 · 可用内容"),24)}</span></div>',"position:absolute;left:515px;top:475px;width:660px")
    s.add("number-rule","","position:absolute;left:50px;top:650px;width:310px;height:2px;background:#8d79d3")
    s.fade("number-rule",.19,.25)
    s.fade("preview",.04,.24);s.fade("number",.19,.25);s.fade("title",.34,.22);s.fade("copy",.44,.22)
    pack=''.join(s.html[pack_start:]);s.html[pack_start:]=[]
    s.add("chapter-pack",pack,"position:absolute;inset:0;background:transparent")
    s.fade("chapter-pack",0,.18)
    s.animate("chapter-pack",max(.7,s.duration-.2),.18,{"opacity":1},{"opacity":0})
    s.nav(number)

build=chapter
