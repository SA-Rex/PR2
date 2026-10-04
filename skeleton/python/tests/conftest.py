"""Корінь скелета — тека, у якій лежать `plugins.toml` і `src`.

Тести звертаються до ядра абсолютно (`src.core...`), і так само робить
реєстр, коли підвантажує плагін за іменем із `plugins.toml`
(`importlib.import_module("src.plugins.<name>.plugin")`). Тому корінь
скелета має бути у `sys.path` незалежно від того, з якої теки запущено
`pytest`. Шлях беремо від самого файлу, а не від поточної теки.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
