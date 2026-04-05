from __future__ import annotations

import argparse


def play(demo: bool = False) -> str:
    lines = [
        "Welcome to Guess Zero!",
        "Pick a number: 0 or 1.",
    ]
    if demo:
        guess = 0
        lines.append(f"Demo guess: {guess}")
        lines.append("You win!")
        return "\n".join(lines)

    lines.append("Interactive mode is intentionally disabled in this fixture.")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="A tiny deterministic CLI game.")
    parser.add_argument("--demo", action="store_true", help="Run the deterministic demo preview.")
    args = parser.parse_args()
    print(play(demo=args.demo))


if __name__ == "__main__":
    main()
