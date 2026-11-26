"""组件输入边界、独立导出与时序的行为回归。"""
import copy,importlib.util,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import 构建 as api

class Components(unittest.TestCase):
    def spec(self,id='07-takeaway'):return api.load(ROOT/'预设'/(id+'.json'))
    def test_all_fifteen_export_without_movie_timeline(self):
        self.assertEqual(len(api.REGISTRY),15)
        with tempfile.TemporaryDirectory() as d:
            for ident in api.REGISTRY:
                out=Path(d)/ident;report=api.build(self.spec(ident),out)
                self.assertGreater(report['event_count'],0)
                self.assertTrue((out/'compositions/component.html').is_file())
                html=(out/'index.html').read_text()
                self.assertNotIn('shot-',html);self.assertIn('data-start="0"',html)
                self.assertFalse((out/'整片计划.json').exists())
    def test_long_hold_does_not_slow_front_entry(self):
        with tempfile.TemporaryDirectory() as d:
            for ident in api.REGISTRY:
                data=[]
                for duration in [3,8]:
                    spec=self.spec(ident);spec['duration']=duration;out=Path(d)/(ident+str(duration));api.build(spec,out)
                    events=api.load(out/'动作参数.json')['events'];data.append([(e['id'],e['start'],e['duration']) for e in events if e['start']<.2 and 'summary-line' not in e['id'] and 'section-' not in e['id']])
                self.assertEqual(*data,msg=ident)
    def test_peel_and_joint_exit_follow_changed_duration(self):
        with tempfile.TemporaryDirectory() as d:
            for duration in [3,5,8]:
                spec=self.spec();spec['duration']=duration;out=Path(d)/str(duration);api.build(spec,out)
                events=api.load(out/'动作参数.json')['events']
                peel=next(e for e in events if e['id']=='screen-peel:0');self.assertAlmostEqual(peel['start'],duration-.6)
                summary=next(e for e in events if e['id']=='summary:1');under=next(e for e in events if e['id']=='underlay:1')
                self.assertEqual(summary['start'],under['start']);self.assertAlmostEqual(peel['duration'],.32)
    def test_invalid_duration_is_rejected_instead_of_clamped(self):
        for n in [True,0,2.9,12.1,float('nan'),float('inf'),3.01]:
            s=self.spec('01-title');s['duration']=n
            with self.assertRaises(ValueError):api.validate(s)
    def test_long_text_is_rejected_instead_of_truncated(self):
        s=self.spec();s['content']['title']='字'*23
        with self.assertRaises(ValueError):api.validate(s)
    def test_wrong_card_count_is_rejected(self):
        s=self.spec('06-fan');s['content']['items']=['一','二']
        with self.assertRaises(ValueError):api.validate(s)
    def test_media_cannot_escape_chosen_root(self):
        for name in ['../outside.png','/tmp/outside.png','bad.mp4']:
            s=self.spec();s['media']['screen']=name
            with self.assertRaises(ValueError):api.validate(s)
    def test_content_is_html_escaped(self):
        with tempfile.TemporaryDirectory() as d:
            s=self.spec('01-title');s['content']['title']='<b>新标题</b>';api.build(s,d)
            self.assertIn('&lt;b&gt;',Path(d,'compositions/component.html').read_text())
    def test_typo_motion_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            s=self.spec();s['options']['motions']={'no-such-object:0':{'start':1,'duration':.2}}
            with self.assertRaises(ValueError):api.build(s,d)
    def test_typo_content_is_rejected(self):
        s=self.spec();s['content']['titel']='标题'
        with self.assertRaises(ValueError):api.validate(s)
    def test_output_owns_all_media_files(self):
        with tempfile.TemporaryDirectory() as d:
            s=self.spec('11-storyboard');api.build(s,d);out=Path(d)
            self.assertTrue((out/'assets/fonts/NotoSansSC.ttf').is_file())
            self.assertEqual(len(list((out/'assets/content').glob('*.svg'))),3)
            self.assertNotIn('模板工程',(out/'index.html').read_text())
    def test_exported_media_has_independent_inode(self):
        import os
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);api.build(self.spec('11-storyboard'),out)
            src=ROOT/'素材/square.svg';dst=next((out/'assets/content').glob('*'+src.suffix))
            # 比较同内容文件，不能仅凭文件名推断copy。
            dst=next(f for f in (out/'assets/content').iterdir() if f.read_bytes()==src.read_bytes())
            self.assertFalse(os.path.samestat(src.stat(),dst.stat()))
            original=src.read_bytes();dst.write_text('changed');self.assertEqual(src.read_bytes(),original)
    def test_minimal_spec_uses_documented_duration(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(api.build({'format':'nana-component@1','component':'01-title'},d)['duration'],4)
    def test_media_only_components_reject_unused_text(self):
        for ident in ['02-media-flip','04-browser','10-media-overlay']:
            s=self.spec(ident);s['content']['title']='不应被静默忽略'
            with self.assertRaises(ValueError):api.validate(s)
    def test_peel_motion_override_changes_actual_js(self):
        with tempfile.TemporaryDirectory() as d:
            s=self.spec();s['options']['motions']={'screen-peel:0':{'start':2,'duration':.5}};api.build(s,d)
            html=Path(d,'compositions/component.html').read_text();self.assertIn('duration:0.5',html)
            event=next(e for e in api.load(Path(d)/'动作参数.json')['events'] if e['id']=='screen-peel:0');self.assertEqual(event['start'],2)
    def test_fan_media_options_change_image_style(self):
        with tempfile.TemporaryDirectory() as d:
            s=self.spec('06-fan');s['options']['slot_options']={'card-0':{'fit':'cover','radius':18}};api.build(s,d)
            self.assertIn('object-fit:cover;object-position:center;border-radius:18px',Path(d,'compositions/component.html').read_text())
    def test_original_short_dissolve_has_no_peel_or_underlay(self):
        with tempfile.TemporaryDirectory() as d:
            s=self.spec();s['duration']=53/30;s['options']={'exit_mode':'dissolve','layout':'reference'};api.build(s,d)
            html=Path(d,'compositions/component.html').read_text();self.assertNotIn('nanaPeel(',html);self.assertNotIn('component-underlay',html)
            e=api.load(Path(d)/'动作参数.json')['events'];a=next(x for x in e if x['id']=='summary:1');b=next(x for x in e if x['id']=='screen:1');self.assertEqual(a['start'],b['start'])

    def test_short_badge_retains_two_strokes_before_scene_cut(self):
        with tempfile.TemporaryDirectory() as d:
            s=self.spec('13-badge');s['duration']=79/30;api.build(s,d)
            events=api.load(Path(d)/'动作参数.json')['events']
            strokes=[x for x in events if x['id'].startswith('badge-check:')]
            self.assertEqual(len(strokes),2)
            self.assertTrue(all(x['start']+x['duration']<79/30 for x in strokes))

if __name__=='__main__':unittest.main(verbosity=2)
