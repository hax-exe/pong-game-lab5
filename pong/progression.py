from __future__ import annotations

"""One-player progression helpers (survival score, unlocks, and persistence)."""

from dataclasses import dataclass
import json
from pathlib import Path

from . import settings


@dataclass(frozen=True)
class PaddleColorUnlock:
    """Defines one selectable paddle color and the score needed to unlock it."""

    color_id: str
    label: str
    color: tuple[int, int, int]
    threshold_seconds: float


# Keep this list simple so junior developers can add/adjust unlocks in one place.
PADDLE_COLOR_UNLOCKS: tuple[PaddleColorUnlock, ...] = (
    PaddleColorUnlock("classic", "Classic White", settings.COLOR_FG, 0.0),
    PaddleColorUnlock("mint", "Mint", (86, 220, 180), 10.0),
    PaddleColorUnlock("gold", "Gold", (240, 205, 85), 20.0),
    PaddleColorUnlock("violet", "Violet", (177, 140, 255), 35.0),
)

DEFAULT_PADDLE_COLOR_ID = PADDLE_COLOR_UNLOCKS[0].color_id


def default_score_file_path() -> Path:
    """Store score data in the user's home directory so it survives relaunches."""

    return Path.home() / ".pong_game_lab5_progress.json"


class HighScoreStore:
    """Loads/saves one-player high-score data from a small local JSON file."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_score_file_path()

    def load_high_score(self) -> float:
        """Read high score or safely return 0.0 when file data is missing/bad."""

        try:
            raw_data = self.path.read_text(encoding="utf-8")
            payload = json.loads(raw_data)
        except (OSError, json.JSONDecodeError):
            return 0.0

        if not isinstance(payload, dict):
            return 0.0

        raw_score = payload.get("one_player_high_score_seconds", 0.0)
        try:
            score = float(raw_score)
        except (TypeError, ValueError):
            return 0.0

        return score if score >= 0.0 else 0.0

    def save_high_score(self, high_score: float) -> bool:
        """Write high score and return success; failures are non-fatal to gameplay."""

        safe_score = max(0.0, float(high_score))
        payload = {"one_player_high_score_seconds": safe_score}
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(payload), encoding="utf-8")
        except OSError:
            return False
        return True


def get_color_option(color_id: str) -> PaddleColorUnlock | None:
    """Look up color metadata by ID so selection logic can validate input."""

    for option in PADDLE_COLOR_UNLOCKS:
        if option.color_id == color_id:
            return option
    return None


def is_color_unlocked(color_id: str, high_score: float) -> bool:
    """A color is selectable only when saved one-player high score meets threshold."""

    option = get_color_option(color_id)
    return option is not None and high_score >= option.threshold_seconds


class OnePlayerProgress:
    """Tracks the current one-player survival run and unlocked color selection."""

    def __init__(self, high_score: float, selected_color_id: str = DEFAULT_PADDLE_COLOR_ID) -> None:
        self.high_score = max(0.0, float(high_score))
        self.current_run_seconds = 0.0
        self.selected_color_id = DEFAULT_PADDLE_COLOR_ID
        self.set_selected_color(selected_color_id)

    def tick(self, dt: float) -> None:
        """Advance run timer using elapsed seconds so score is frame-rate independent."""

        self.current_run_seconds += max(0.0, dt)

    def reset_current_run(self) -> None:
        """Clear current run timer (used when starting/restarting one-player rounds)."""

        self.current_run_seconds = 0.0

    def on_human_conceded(self) -> bool:
        """Finalize run on conceded point and update best score if this run is higher."""

        completed_run = self.current_run_seconds
        self.current_run_seconds = 0.0
        if completed_run > self.high_score:
            self.high_score = completed_run
            return True
        return False

    def set_selected_color(self, color_id: str) -> bool:
        """Only allow selecting colors unlocked by the saved high score."""

        if is_color_unlocked(color_id, self.high_score):
            self.selected_color_id = color_id
            return True
        return False

    def selected_color(self) -> tuple[int, int, int]:
        """Return active color with safe fallback to default when selection is invalid."""

        if is_color_unlocked(self.selected_color_id, self.high_score):
            option = get_color_option(self.selected_color_id)
            if option is not None:
                return option.color
        return PADDLE_COLOR_UNLOCKS[0].color
