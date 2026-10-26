# Pong Game (Lab 5)

Simple 2D Pong game built with Python and `pygame-ce`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python -m pong
```

## Controls

- **Menu**
  - `1`: Open single-player setup (choose paddle color, then start)
  - `2`: Local two-player
  - `Esc`: Quit
- **Single-player setup**
  - `A` / `←`: Previous paddle color option
  - `D` / `→`: Next paddle color option
  - `Enter` / `Space`: Start one-player with highlighted unlocked color
  - `Esc` / `M`: Return to menu
- **In game**
  - Left paddle: `W` / `S`
  - Right paddle (two-player): `↑` / `↓`
  - `R`: Restart match
  - `M`: Return to menu
  - `Esc`: Quit

## One-player survival score and unlocks

- In one-player mode, your **current survival score** is the number of seconds (elapsed gameplay time) since your left paddle last conceded a point.
- When you concede, that run ends. If the run is higher than your previous best, the game updates the **one-player high score**.
- High score is persisted in a local JSON file at:
  - `~/.pong_game_lab5_progress.json`
- If the file is missing, malformed, or unwritable, the game safely falls back to default values (`0.0`) and continues.

### Paddle color unlock thresholds (one-player)

- `Classic White` — unlocked at `0s` (always available)
- `Mint` — unlocked at `10s`
- `Gold` — unlocked at `20s`
- `Violet` — unlocked at `35s`

## MVC Overview

- **Model** (`pong/model.py`): Game state/entities (paddles, ball, scores), movement, collisions, scoring, CPU behavior, and win logic.
- **View** (`pong/view.py`): Draws menu/game scenes, scores, controls, and win state.
- **Controller/Application** (`pong/app.py`): Main loop, event handling, mode selection, state transitions, and input mapping.
