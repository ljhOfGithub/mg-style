"""可复用配置与动作时间的行为测试，不复写成片。"""
from pathlib import Path
import importlib.util,json,tempfile,copy,re,subprocess
R=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('template_build',R/'构建.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
base=json.loads((R/'配置.json').read_text())
with tempfile.TemporaryDirectory(prefix='mg-template-test-') as tmp:
 p=Path(tmp);c=copy.deepcopy(base);c['data']['budget']['human'][0]=5;c['data']['chapters'][0]['title']='替换标题验证';c['data']['prompt']='这是替换后的提示词';c['data']['ending'][0]=['新的','结尾'];c['copy']['开场']['txt_000']='配置替换文字验证'
 f=p/'改值.json';f.write_text(json.dumps(c,ensure_ascii=False));out=p/'changed.html';report=m.build(f,out);s=out.read_text();assert '替换标题验证' in s and '这是替换后的提示词' in s and '配置替换文字验证' in s
 assert '5 + 0 + 0 + 10 + 2 = 17分钟' in s and '"to": 17' in s
 from bs4 import BeautifulSoup
 end=BeautifulSoup(s,'html.parser').select_one('[data-mg-id="end-line-0"]')
 assert '新的结尾' in ''.join(BeautifulSoup(s,'html.parser').stripped_strings) and 'class="end-group"' in s
 assert report['scene_count']==23 and report['event_count']>=130
 # 无需改源码，配置事件会改变实际输出时间。
 next(e for e in c['scenes'][0]['events'] if e['type']=='mask')['duration']=.7;f.write_text(json.dumps(c,ensure_ascii=False));m.build(f,out);assert '"duration": 0.7' in out.read_text()
 # 错目标必须被拒绝，不能生成貌似成功的空动作。
 c['scenes'][0]['events'][0]['target']='#不存在的目标';f.write_text(json.dumps(c,ensure_ascii=False))
 try:m.build(f,out)
 except AssertionError:pass
 else:raise AssertionError('错误目标被静默接受')
print('PASS config text/budget/chapter/prompt/ending/timing updates and missing-target rejection')

# 默认配置重建必须保持已展示画面源码完全相同。
with tempfile.TemporaryDirectory(prefix='mg-template-default-') as tmp:
 p=Path(tmp);out=p/'default.html';m.build(R/'配置.json',out);assert out.read_bytes()==(R/'index.html').read_bytes(), '默认输出发生未展示变化'
 from bs4 import BeautifulSoup
 tree=BeautifulSoup(out.read_text(),'html.parser');assert len(tree.select('[data-mg-id="publish-check"]'))==1,'公开占位素材应只显示一个模板完成标记'
 assert len(tree.select('[data-mg-id^="parallelbar-"]'))==4,'每条制作线只保留一条进度'
 # 同一模块可重复实例化，DOM和局部时间必须隔离。
 c=copy.deepcopy(base);first=copy.deepcopy(c['scenes'][0]);first.update(end=5.6,visibleEnd=5.6,fadeOut=0)
 second=copy.deepcopy(first);second.update(id='开场副本',module='开场',copyKey='开场',start=5.6,end=11.2,visibleEnd=11.2)
 c['scenes']=[first,second];c['canvas']['duration']=11.2;c['audio']=None;c['captions']=[]
 cfg=p/'重复模块.json';cfg.write_text(json.dumps(c,ensure_ascii=False));m.build(cfg,out);tree=BeautifulSoup(out.read_text(),'html.parser')
 ids=[e['id'] for e in tree.select('[id]')];assert len(ids)==len(set(ids)),'重复模块产生ID碰撞'
 assert tree.select_one('#scene-1 [data-mg-id="hero"]') is not None
print('PASS default byte identity, one completion mark, four progress bars, repeated-module isolation')
