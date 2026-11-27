"""校验公开风格包的源码、相对路径、默认构建与文档链接。"""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
import subprocess

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
IGNORED = {'.git', '.build', '.hyperframes', '.venv', '__pycache__', 'saved', 'exports', 'logs', 'output'}


def candidates():
    for f in ROOT.rglob('*'):
        if f.is_file() and not any(p in IGNORED for p in f.relative_to(ROOT).parts) and f.name != '构建记录.json':
            yield f


def main():
    catalog = json.loads((ROOT / 'index.json').read_text())
    count = 0
    for style in catalog['styles']:
        library = ROOT / style['path']
        assert library.resolve().parent == ROOT.resolve(), '每个风格须有独立的根目录子文件夹'
        assert library.name == style['id'], '风格目录应与登记ID一致'
        assert (library / 'README.md').is_file(), '缺少风格使用入口'
        meta = json.loads((library / '风格.json').read_text())
        if meta.get('project_type') == 'frame-function-components':
            assert meta['component_count'] == style['component_count']
            assert meta['distribution'] == 'public-components'
            assert not any(f.suffix.lower() in ['.wav', '.mp3', '.flac', '.m4a'] for f in library.rglob('*'))
            subprocess.run(['node', 'tools/verify.mjs'], cwd=library, check=True)
            count += 1
            continue
        project = library / meta['project']
        config = json.loads((project / '配置.json').read_text())
        assert len(config['scenes']) == style['scene_count']
        if meta.get('distribution') == 'public-placeholder':
            assert config.get('audio') is None, '公开占位版不附带个人音轨'
            assert not any(f.suffix.lower() in ['.wav', '.mp3', '.flac', '.m4a'] for f in library.rglob('*'))
        spec = importlib.util.spec_from_file_location('public_build', project / '构建.py')
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        out = Path(tempfile.mkdtemp(prefix='mg-style-verify-')) / 'current.build'
        report = mod.build(project / '配置.json', out)
        assert out.read_bytes() == (project / 'index.html').read_bytes(), '默认HTML与源码不一致'
        assert report['scene_count'] == style['scene_count']
        manifest = json.loads((library / '基线文件清单.json').read_text())
        for entry in manifest['files']:
            f = library / entry['path']
            assert f.resolve().is_relative_to(library.resolve()), '清单不可越出风格目录'
            assert f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest() == entry['sha256'], entry['path']
        count += 1
    files = list(candidates())
    for f in files:
        assert all(part.isascii() for part in f.relative_to(ROOT).parts[:-1]), '文件夹须使用英文ASCII名称：'+str(f)
    for name in ['fred-mg-1','nana-mg-1']:
        style = ROOT/name
        meta = json.loads((style/'风格.json').read_text())
        library = style/meta['component_library']
        catalog_name = 'catalog.json' if name=='fred-mg-1' else '目录.json'
        components = json.loads((library/catalog_name).read_text())['components']
        assert len(components)==meta['component_count']
        assert len({x['id'] for x in components})==len(components), '组件ID不可重复'
    for f in files:
        if f.suffix.lower() in ['.md', '.py', '.js', '.json', '.html', '.css', '.command', '.yaml']:
            text = f.read_text(encoding='utf-8')
            assert not any(prefix in text for prefix in [chr(47)+'Users'+chr(47), 'C:'+chr(92)+'Users'+chr(92)]), f'含本机绝对路径：{f}'
        if f.suffix.lower() == '.md':
            for link in re.findall(r'\]\(([^)]+)\)', f.read_text()):
                if '://' in link or link.startswith('#'):
                    continue
                target = link.split('#')[0].strip('<>')
                assert (f.parent / target).exists(), (f, link)
    print(json.dumps(dict(status='PASS', styles=count, source_files=len(files), local_links='valid', default_html='identical'), ensure_ascii=False))


if __name__ == '__main__':
    main()
