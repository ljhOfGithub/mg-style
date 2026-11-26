"""独立组件、真实参数消费、资源类型与时窗的行为回归。"""
from pathlib import Path
import copy,importlib.util,json,subprocess,sys,tempfile,unittest
L=Path(__file__).resolve().parents[1];sys.path.insert(0,str(L));import build as api
class Components(unittest.TestCase):
 def spec(self,ident='04-chapter-flip'):return {'format':'fred-component@1','component':ident}
 def output(self):return Path(tempfile.mkdtemp(prefix='fred-component-test-'))
 def build(self,s):p=self.output();api.build(s,p);return p,api.load(p/'config.json'),(p/'compositions/component.html').read_text()
 def test_all_23_are_single_scene_self_contained(self):
  self.assertEqual(len(api.CATALOG),23)
  for r in api.CATALOG:
   p,c,h=self.build(self.spec(r['id']));self.assertEqual(len(c['scenes']),1);self.assertEqual(c['scenes'][0]['start'],0);self.assertEqual(len(list((p/'modules').glob('*.tpl'))),1)
   self.assertIn('data-composition-id="component"',h);self.assertNotIn('151.266',h);self.assertEqual(len(list(p.glob('*.html'))),1)
 def test_output_can_rebuild_without_library(self):
  p,c,h=self.build(self.spec());(p/'index.html').write_text('stale');subprocess.run([sys.executable,str(p/'build.py')],cwd=p,check=True);self.assertIn('component-host',(p/'index.html').read_text())
 def test_background_and_wall_offsets_are_retained(self):
  p,c,h=self.build(self.spec('12-render-queue'));self.assertAlmostEqual(c['backgrounds'][0]['source_offset'],5.6);self.assertIn('data-media-start="5.6',h)
  p,c,h=self.build(self.spec('23-ending-type'));self.assertGreater(c['ambient_walls'][0]['media_offset'],39);self.assertIn('data-media-start="39.',h)
 def test_longer_duration_keeps_entry_speed_and_moves_exit(self):
  a=self.spec();p,c,h=self.build(a);a['duration']=3.8;q,d,_=self.build(a)
  x=c['scenes'][0]['events'];y=d['scenes'][0]['events'];self.assertEqual(x[0],y[0]);self.assertAlmostEqual(y[2]['at']-x[2]['at'],2)
 def test_chapter_data_updates_actual_dom(self):
  s=self.spec();s['data']={'chapter':{'number':'08','title':'资料整理'}};p,c,h=self.build(s);self.assertIn('资料整理',h);self.assertEqual(c['data']['chapters'][0]['number'],'08')
 def test_grouped_chapter_rejects_unused_title(self):
  s=self.spec('07-chapter-reveal');s['data']={'chapter':{'number':'03','title':'无效','groups':['资料','整理']}}
  with self.assertRaises(ValueError):api.build(s,self.output())
 def test_opening_budget_rejects_unused_fields(self):
  s=self.spec('01-opening-wall');s['data']={'budget':{'human':[1,2,3,4,5],'ai_labels':['a']*5}}
  with self.assertRaises(ValueError):api.build(s,self.output())
 def test_budget_and_prompt_are_consumed(self):
  s=self.spec('19-budget-ledger');s['data']={'budget':{'human':[4,0,0,8,3],'ai_labels':['短任务']*5,'human_bar_px_per_minute':10}};p,c,h=self.build(s);self.assertIn('4 + 0 + 0 + 8 + 3 = 15分钟',h)
  s=self.spec('05-prompt-input');s['data']={'prompt':'这是本次的新提示词'};p,c,h=self.build(s);self.assertIn('这是本次的新提示词',h)
 def test_source_media_are_independent_copies(self):
  p,c,h=self.build(self.spec('05-prompt-input'));src=next((L/'shared/assets/placeholders').glob('*.png'));matches=[f for f in (p/'assets/media').iterdir() if f.read_bytes()==src.read_bytes()];self.assertTrue(matches);self.assertNotEqual(src.stat().st_ino,matches[0].stat().st_ino)
 def test_image_slot_rejects_video(self):
  r=api.REGISTRY['05-prompt-input'];slot=next(k for k,v in r['media'].items() if v['kind']=='image');s=self.spec(r['id']);s['media']={slot:'assets/placeholders/demo.mp4'}
  with self.assertRaises(ValueError):api.build(s,self.output())
 def test_media_path_cannot_escape_root(self):
  with self.assertRaises(ValueError):api.safe_media(L/'shared','../../README.md')
 def test_invalid_duration_is_rejected(self):
  for d in [True,0,1.7,30.1,float('nan'),2.01]:
   s=self.spec();s['duration']=d
   with self.assertRaises(ValueError):api.validate(s)
 def test_unknown_fields_and_motion_rejected(self):
  for patch in [{'unknown':1},{'motions':{'missing':{'at':0}}},{'content':{'missing':'text'}}]:
   s=self.spec();s.update(patch)
   with self.assertRaises(ValueError):api.validate(s)
 def test_bound_wall_duration_rejected(self):
  s=self.spec('01-opening-wall');s['motions']={'开场-01':{'duration':.5}}
  with self.assertRaises(ValueError):api.validate(s)
 def test_knotted_bar_duration_rejected(self):
  for r in api.CATALOG:
   c=api.load(L/'presets'/(r['id']+'.json'));event=next((e for e in c['scenes'][0]['events'] if e.get('knots')),None)
   if event:
    s=self.spec(r['id']);s['motions']={event['id']:{'duration':6}}
    with self.assertRaises(ValueError):api.validate(s)
    return
  self.fail('缺少节点进度测试对象')
 def test_truncated_action_rejected(self):
  s=self.spec();s['motions']={'章节01-01':{'at':1.7}}
  with self.assertRaises(ValueError):api.build(s,self.output())
 def test_content_is_escaped_and_not_silently_cut(self):
  r=api.REGISTRY['02-contrast'];key=r['fields'][0]['key'];s=self.spec(r['id']);s['content']={key:'<新内容>'};p,c,h=self.build(s);self.assertIn('&lt;新内容&gt;',h)
  s['content'][key]='字'*100
  with self.assertRaises(ValueError):api.validate(s)
 def test_media_stays_present_through_full_exit(self):
  for ident,duration in [('02-contrast',6),('15-review',12.4),('18-publishing',16.3)]:
   spec=self.spec(ident);spec['duration']=duration;p,c,h=self.build(spec)
   for m in c['scenes'][0]['media']:self.assertAlmostEqual(m['at']+m['duration'],duration)
 def test_six_queue_media_finish_together(self):
  s=self.spec('12-render-queue');s['duration']=10.6;p,c,h=self.build(s)
  media=[m for m in c['scenes'][0]['media'] if m['target'].startswith(('#v-队列','#queue-live-'))]
  self.assertEqual(len(media),6);self.assertTrue(all(abs(m['at']+m['duration']-10.6)<1e-6 for m in media))
if __name__=='__main__':unittest.main(verbosity=2)
