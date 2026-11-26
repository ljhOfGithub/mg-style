"""验证编辑器的保存回滚、布局修改、素材替换与单模块编译。"""
from pathlib import Path
import copy,importlib.util,json,tempfile
R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('mg_editor',R/'编辑器.py');e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
base=e.read_config();meta=e.metadata(base)
assert len(meta)==23
assert not meta['章节01']['fields'],'章节文本必须由章节表编辑，不能显示不会生效的重复字段'
assert not meta['末卡']['fields'],'分词组应使用结尾编辑接口'
assert all(f['label'] for m in meta.values() for f in m['fields'])
with tempfile.TemporaryDirectory(prefix='mg-editor-test-') as folder:
 p=Path(folder).resolve();e.ROOT=p;e.write_json(p/'配置.json',base)
 c=copy.deepcopy(base);c['layout']={'审片':[{'target':'#opinion','style':{'font-size':'42px'}}]}
 c['copy']['反差']['txt_000']='测试替换正文';c['assetOverrides']['assets/角色母图.png']='assets/角色母图.png'
 result=e.save_config(c);html=(p/'index.html').read_text();assert 'font-size:42px!important' in html and '测试替换正文' in html
 assert len(list((p/'保存记录').glob('*.json')))==1 and result['ok']
 from bs4 import BeautifulSoup
 tree=BeautifulSoup(html,'html.parser');css=tree.style.string
 assert '[data-module="审片"] [data-mg-id="opinion"]' in css,'独立模块的CSS未绑定实际DOM'
 assert tree.select_one('[data-module="审片"] [data-mg-id="opinion"]') is not None
 assert '[data-module="账本"] #count' not in css,'命名空间使总计卡样式失效'
 original=(p/'配置.json').read_bytes();bad=copy.deepcopy(c);bad['scenes'][0]['events'][0]['target']='#错误目标'
 try:e.save_config(bad)
 except ValueError:pass
 else:raise AssertionError('错误配置应保存失败')
 assert (p/'配置.json').read_bytes()==original,'失败时覆盖了可用配置'
 for i in range(23):
  single=e.scene_config(base,i);single['backgrounds']=[]
  e.write_json(p/'单模块.json',single);e.builder.build(p/'单模块.json',p/'单模块.html')
  assert single['scenes'][0]['start']==0 and single['audio'] is None
 assert e.package_path('assets/新素材.mp4').is_relative_to(p)
 try:e.package_path('../外部.mp4')
 except ValueError:pass
 else:raise AssertionError('外部路径未被拒绝')
print('PASS 23 modules, semantic fields, save/rollback, real layout update, media override, independent module build')
