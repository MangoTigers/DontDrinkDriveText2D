from pathlib import Path
import asyncio
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dddt_game.game import run_game, run_game_async


_WEB_STARTED = False


def _start() -> None:
    global _WEB_STARTED

    if _WEB_STARTED:
        return

    _WEB_STARTED = True

    if sys.platform == "emscripten":
        # In pygbag, main.py may be imported while an event loop is already running.
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(run_game_async())
        else:
            task = loop.create_task(run_game_async())

            def _report_task_error(done_task: asyncio.Task[None]) -> None:
                try:
                    exc = done_task.exception()
                except asyncio.CancelledError:
                    return
                if exc is not None:
                    import traceback
                    traceback.print_exception(exc)

            task.add_done_callback(_report_task_error)
    else:
        run_game()


if sys.platform == "emscripten":
    _start()
elif __name__ == "__main__":
    _start()
