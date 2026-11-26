#!/bin/zsh
cd "${0:A:h}"
if [[ -n "$MG_PYTHON" && -x "$MG_PYTHON" ]]; then
  mg_python="$MG_PYTHON"
elif [[ -x .venv/bin/python ]]; then
  mg_python="$PWD/.venv/bin/python"
else
  mg_python="$(command -v python3)"
fi
if ! "$mg_python" -c 'import bs4' 2>/dev/null; then
  echo '首次运行需要安装模板依赖。请在本目录终端执行：'
  echo 'python3 -m venv .venv'
  echo '.venv/bin/python -m pip install -r requirements.txt'
  echo '再双击本文件启动。已有Python环境可用 MG_PYTHON 指定。'
  read 'mg_ack?按回车结束'
  exit 1
fi
"$mg_python" 编辑器.py --port 64066
