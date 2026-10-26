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
  - `1`: Single-player (left paddle vs CPU)
  - `2`: Local two-player
  - `Esc`: Quit
- **In game**
  - Left paddle: `W` / `S`
  - Right paddle (two-player): `↑` / `↓`
  - `R`: Restart match
  - `M`: Return to menu
  - `Esc`: Quit

## MVC Overview

- **Model** (`pong/model.py`): Game state/entities (paddles, ball, scores), movement, collisions, scoring, CPU behavior, and win logic.
- **View** (`pong/view.py`): Draws menu/game scenes, scores, controls, and win state.
- **Controller/Application** (`pong/app.py`): Main loop, event handling, mode selection, state transitions, and input mapping.
