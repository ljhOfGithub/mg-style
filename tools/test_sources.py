"""来源校验必须拒绝漏项、作品号错配与公开入口遗漏。"""
import json
from pathlib import Path
import tempfile
import unittest
from verify_sources import verify_sources


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.library = self.root / 'example'
        self.library.mkdir()
        self.url = 'https://www.douyin.com/video/1234567890'
        (self.root / 'index.json').write_text(json.dumps({'styles': [{'id': 'example', 'path': 'example', 'reference_url': self.url}]}))
        self.meta = {'reference_source': {'platform': 'douyin', 'url': self.url, 'video_id': '1234567890', 'verification': '实际来源记录', 'rights': '保留原权利'}}
        self.save()
        for p in (self.root / 'README.md', self.library / 'README.md'):
            p.write_text(f'[原视频]({self.url})')

    def save(self):
        (self.library / '风格.json').write_text(json.dumps(self.meta))

    def test_complete_source(self):
        self.assertEqual(verify_sources(self.root), 1)

    def test_missing_source(self):
        self.meta = {}
        self.save()
        with self.assertRaises(KeyError):
            verify_sources(self.root)

    def test_wrong_video_id(self):
        self.meta['reference_source']['video_id'] = '999'
        self.save()
        with self.assertRaises(AssertionError):
            verify_sources(self.root)

    def test_missing_visible_link(self):
        (self.library / 'README.md').write_text('无来源')
        with self.assertRaises(AssertionError):
            verify_sources(self.root)


if __name__ == '__main__':
    unittest.main()
