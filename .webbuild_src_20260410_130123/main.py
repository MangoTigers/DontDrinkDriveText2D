from pathlib import Path
import asyncio
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dddt_game.game import run_game, run_game_async


def _start() -> None:
    if sys.platform == "emscripten":
        # In pygbag, main.py can be imported instead of run as __main__.
        asyncio.run(run_game_async())
    else:
        run_game()


if sys.platform == "emscripten":
    _start()
elif __name__ == "__main__":
    _start()
