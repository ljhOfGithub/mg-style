"""六宫格总览；从nana mg1已验证动作源码拆分。"""
from runtime import *
from 组件.m13_badge import workflow_badge

def grid_six(s, include_nav=True):
    s.add("bg","","inset:0","grid-bg")
    s.head("将六项 Skills 组合起来","按任务选择，再串成工作流程")
    s.grid(); s.fade("heading",0,.18)
    # 源六宫格整体出现，六卡同一入场时刻；不改成通用逐条飞入。
    for i in range(6):s.fade(f"card-{i}",.08,.22)
    if include_nav:s.nav(7 if s.chapter==7 else 0)
    s.add("footer","","","footer")
    if s.chapter==7:workflow_badge(s,overlay=True)

build=grid_six
