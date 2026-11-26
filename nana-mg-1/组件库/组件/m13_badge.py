"""双次描勾；从nana mg1已验证动作源码拆分。"""
from runtime import *

def workflow_badge(s,overlay=False):
    if not overlay:
        s.slot("background","background","inset:0;border:0;border-radius:0")
        if s.cfg.get('layout')!='overlay':s.head(s.cfg.get("title","当前任务已完成"),s.cfg.get("subtitle","确认结果，再继续下一步"))
    delay=2.77 if overlay else .15
    if overlay and s.duration<delay+.8:return
    placement='position:absolute;right:120px;top:92px' if s.cfg.get('layout')=='overlay' else ''
    s.add("badge",f'<div id="{s.key("badge-text")}" class="badge-text">{text(s.cfg.get("badge_text","专属工作流"),10)}</div><div class="badge-square"></div><svg class="badge-check" viewBox="0 0 140 140"><path id="{s.key("badge-check")}" d="M20 70L58 105L123 28" pathLength="1"/></svg>',placement,"badge")
    s.animate("badge",delay,.19,{"scale":.62,"opacity":0},{"scale":1,"opacity":1})
    s.animate("badge-text",delay+.10,.25,{"clipPath":"inset(0% 100% 0% 0%)"},{"clipPath":"inset(0% 0% 0% 0%)"},"none")
    reset=s.cfg.get('motions',{}).get('badge-reset:0',{}).get('start',delay+1.50)
    if reset<s.duration-.2:
        s.tweens.append(f'tl.set("#{s.key("badge-check")}",{{strokeDashoffset:1}},{reset});')
        s.events.append(dict(id='badge-reset:0',selector='#'+s.key('badge-check'),start=reset,duration=.001,before={'strokeDashoffset':0},after={'strokeDashoffset':1},ease='none'))
    for t in [delay+.22,delay+1.70]:
        if t<s.duration-.15:s.animate("badge-check",t,.18,{"strokeDashoffset":1},{"strokeDashoffset":0},"none")

build=workflow_badge
