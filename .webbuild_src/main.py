from pathlib import Path
import asyncio
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dddt_game.game import run_game, run_game_async


if __name__ == "__main__":
    if sys.platform == "emscripten":
        asyncio.run(run_game_async())
    else:
        run_game()
