from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from game import play


def test_demo_mode_returns_winning_transcript() -> None:
    output = play(demo=True)
    assert "Guess Zero" in output
    assert "You win!" in output
