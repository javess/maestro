# CLI Noughts And Crosses

Build a command-line noughts-and-crosses game for two human players.

Outcomes:
- ask both players for their names before the first round
- play on a standard 3x3 board in the terminal
- alternate turns between X and O
- detect wins, draws, and invalid moves
- track score across multiple rounds
- show the current score before each new round
- support a deterministic `--demo` mode for preview and smoke testing

Constraints:
- Python project
- local CLI only
- no network dependency in the game itself
- keep the codebase small, readable, and easy to test
- include `pytest`, `ruff`, and `ty` friendly project structure

Acceptance criteria:
- players can enter their names once and reuse them across rounds
- the game prints a readable board after every move
- a completed round announces the winner or a draw
- score persists for the current process across repeated rounds
- `python game.py --demo` prints a deterministic transcript suitable for `maestro preview`
- the project includes automated tests for game rules and score keeping

Risks:
- CLI input handling can become tangled if game state and rendering are mixed together
- repeated-round score keeping can introduce hidden state if not modeled explicitly

Non-goals:
- online multiplayer
- AI opponents
- persistent score storage across separate process runs
