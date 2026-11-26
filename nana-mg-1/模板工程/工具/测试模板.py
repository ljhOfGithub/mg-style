"""检查真实复用接口与时间映射，防止把模板做成固定截图。"""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

P=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("builder",P/"工具/构建.py")
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)

class TemplateTests(unittest.TestCase):
    def test_complete_source_coverage(self):
        last=0
        for row in b.PLAN["shots"]:
            self.assertEqual(row["start_frame"],last)
            self.assertGreater(row["end_frame"],last)
            self.assertIn(row["template"],b.FUNCTIONS)
            last=row["end_frame"]
        self.assertEqual(last,1838)

    def test_each_module_changes_content_and_is_seekable(self):
        for index in b.TEMPLATES:
            cfg={"accent":"#f7ca7c","templates":{index["id"]:{"title":"测试自定义标题"}}}
            scene=b.Scene("test-"+index["id"],4,index["id"],cfg)
            b.FUNCTIONS[index["id"]](scene)
            result=scene.finish()
            self.assertIn('paused:true',result)
            self.assertIn('window.__timelines',result)
            self.assertIn('--accent:#f7ca7c',result)
            self.assertGreater(len(scene.tweens),0)
            for item in scene.events:
                self.assertGreaterEqual(item["start"],0)
                self.assertLess(item["start"]+item["duration"],4)

    def test_unsafe_media_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            cfg=Path(temp)/"cfg.json"
            cfg.write_text(json.dumps({"templates":{"01-title":{"media":{"background":"../../private.mp4"}}}}))
            with self.assertRaisesRegex(ValueError,"assets"):
                b.read_config(cfg)

    def test_text_is_escaped(self):
        self.assertEqual(b.text('<img src=x>'), '&lt;img src=x&gt;')

    def test_independent_timing_override(self):
        cfg={"templates":{"02-media-flip":{"motions":{"screen:0":{"start":.4,"duration":.3}}}}}
        s=b.Scene("timing",4,"02-media-flip",cfg);b.media_flip(s)
        self.assertEqual(s.events[0]["start"],.4)
        self.assertEqual(s.events[0]["duration"],.3)
        self.assertNotEqual(s.events[1]["start"],.4)
        self.assertIn('"immediateRender": false',s.tweens[1])

    def test_future_exit_seeds_new_properties_without_overwriting_entry(self):
        s=b.Scene("seed",4,"02-media-flip",{})
        s.rise("screen",0,.3,480)
        s.animate("screen",3,.3,{"rotation":0,"x":0,"opacity":1},{"rotation":-38,"x":-700,"opacity":0})
        initial={k:v[1] for k,v in s.initial_properties["screen"].items()}
        self.assertEqual(initial,{"opacity":0,"y":480,"rotation":0,"x":0})
        self.assertIn('gsap.set("#seed-screen"',s.finish())
        self.assertTrue(all('"immediateRender": false' in x for x in s.tweens))

    def test_shot_media_override_does_not_change_other_shots(self):
        c={"templates":{"07-takeaway":{"title":"通用标题"}},"shots":{"one":{"title":"本段标题","media_rect":{"screen":[10,20,600,400]}}}}
        one=b.Scene("one",3,"07-takeaway",c);b.takeaway(one)
        two=b.Scene("two",3,"07-takeaway",c);b.takeaway(two)
        self.assertIn("本段标题",one.finish());self.assertIn("left:10px;top:20px;width:600px;height:400px",one.finish())
        self.assertIn("通用标题",two.finish());self.assertNotIn("本段标题",two.finish())

    def test_page_exit_collapses_entire_polygon(self):
        s=b.Scene("exit",3.4,"07-takeaway",{},1);b.takeaway(s)
        exit_event=[e for e in s.events if e["id"]=="screen:1"][0]
        self.assertEqual(exit_event["after"]["clipPath"],"polygon(0% 0%,0% 0%,0% 0%,0% 0%)")
        self.assertLess(exit_event["start"]+exit_event["duration"],s.duration-.15)

    def test_fan_reveals_over_presenter_instead_of_empty_cut(self):
        s=b.Scene("fan",2.5,"06-fan",{});b.fan_five(s)
        self.assertIn('id="fan-background"',s.finish())
        fade=[e for e in s.events if e["id"]=="surface:0"][0]
        self.assertEqual(fade["before"]["opacity"],0)
        self.assertGreater(fade["duration"],.2)

    def test_browser_retains_existing_overview_without_reentry(self):
        s=b.Scene("stack",2.63,"04-browser",{"templates":{"03-grid":{"title":"已有六宫格"}}},0);b.browser_stack(s)
        self.assertIn("已有六宫格",s.finish())
        self.assertFalse(any(e["id"].startswith(("heading:","card-")) for e in s.events))

    def test_browser_page_gaps_have_no_media_placeholder(self):
        for chapter in [0,3]:
            s=b.Scene("browser",5.7 if chapter==3 else 2.63,"04-browser",{},chapter);b.browser_stack(s)
            self.assertNotIn('assets/placeholders/screen.svg',s.finish())

    def test_node_entry_retains_backdrop(self):
        s=b.Scene("nodes",2.5,"08-nodes",{});b.node_flow(s)
        self.assertIn('id="nodes-background"',s.finish())
        self.assertTrue(any(e["id"]=="surface:0" and e["before"]=={"opacity":0} for e in s.events))

    def test_two_stage_takeaway_has_backface_and_joint_exit(self):
        cfg={"shots":{"test":{"page_peel":{"start":2.6,"duration":.33,"ease":"none"},"summary_rect":[94,205,660,454],"summary_track":True}}}
        s=b.Scene("test",3.2667,"07-takeaway",cfg,2);b.takeaway(s)
        html=s.finish();self.assertIn("nanaPeel(",html);self.assertIn('test-screen-back',html)
        self.assertIn('test-peel-host',html);self.assertIn("linear-gradient(90deg",html)
        self.assertEqual(len([e for e in s.events if e["id"].startswith("underlay:")]),2)

    def test_peel_has_mirrored_intermediate_and_closed_endpoint(self):
        js=(P/"assets/runtime/diagonal-peel.js").read_text()
        result=subprocess.check_output(["node","-e","global.window={};"+js+";const f={style:{}},b={style:{}};const draw=window.nanaPeel(f,b,1297,977);draw(.35);const mid={...b.style};draw(1);process.stdout.write(JSON.stringify({mid,end:b.style,front:f.style}));"],text=True)
        state=json.loads(result);self.assertEqual(state["mid"]["opacity"],"1");self.assertTrue(state["mid"]["transform"].startswith("matrix(-0.832"));self.assertEqual(state["end"]["opacity"],"0");self.assertIn("0px 0px,0px 0px,0px 0px",state["front"]["clipPath"])

    def test_timing_outside_module_rejected(self):
        cfg={"templates":{"02-media-flip":{"motions":{"screen:0":{"start":3.9,"duration":.3}}}}}
        with self.assertRaisesRegex(ValueError,"超出"):
            s=b.Scene("timing",4,"02-media-flip",cfg);b.media_flip(s)

    def test_takeaway_orders_are_distinct(self):
        first=b.Scene("first",3.3,"07-takeaway",{},1);b.takeaway(first)
        second=b.Scene("second",3.3,"07-takeaway",{},2);b.takeaway(second)
        def start(scene,key):return [e['start'] for e in scene.events if e['id'].startswith(key)][-1]
        self.assertLess(start(first,'summary:'),start(first,'screen:'))
        self.assertGreater(start(second,'summary:'),start(second,'screen:'))
        self.assertIn('second-underlay',second.finish())

    def test_nested_demo_uses_real_layouts(self):
        s=b.Scene("nested",5.7,"04-browser",{},3);b.browser_stack(s)
        page=s.finish()
        self.assertIn('outline-number',page)
        self.assertIn('nested-inner-1-title',page)
        self.assertIn('nested-inner-3-number',page)
        self.assertIn('nestedTL.fromTo',page)
        self.assertIn('nested-windows',page)

    def test_badge_has_empty_hold_between_strokes(self):
        s=b.Scene("badge",4,"13-badge",{});b.workflow_badge(s)
        strokes=[e for e in s.events if e['id'].startswith('badge-check:')]
        self.assertEqual(len(strokes),2)
        self.assertAlmostEqual(strokes[1]['start']-(.15+1.50),.20)
        self.assertTrue(any('tl.set("#badge-badge-check"' in line for line in s.tweens))

    def test_short_third_takeaway_still_exits(self):
        s=b.Scene("short",50/30,"07-takeaway",{},5);b.takeaway(s)
        exits=[e for e in s.events if e['after'].get('opacity')==0]
        self.assertEqual({e['id'] for e in exits},{'summary:1','screen:1'})

if __name__=="__main__":unittest.main(verbosity=2)
