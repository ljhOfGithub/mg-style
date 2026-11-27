"""核对所有风格的抖音来源、作品号与公开入口是否一致。"""
import json
from pathlib import Path
import re


def verify_sources(root):
    styles = json.loads((root / 'index.json').read_text())['styles']
    for style in styles:
        library = root / style['path']
        source = json.loads((library / '风格.json').read_text())['reference_source']
        url = source['url']
        match = re.fullmatch(r'https://www\.douyin\.com/video/(\d+)', url)
        assert match, f"{style['id']}：缺少正式抖音作品链接"
        assert source['platform'] == 'douyin'
        assert source['video_id'] == match.group(1), f"{style['id']}：作品号不一致"
        assert style['reference_url'] == url, f"{style['id']}：根索引来源不一致"
        assert source['verification'].strip() and source['rights'].strip()
        for path in (root / 'README.md', library / 'README.md'):
            assert f']({url})' in path.read_text(), f'{path}：缺少可点击来源'
    return len(styles)


if __name__ == '__main__':
    print(json.dumps({'status': 'PASS', 'styles': verify_sources(Path(__file__).resolve().parents[1])}))
