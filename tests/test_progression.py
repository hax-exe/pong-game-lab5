import tempfile
import unittest
from pathlib import Path

from pong.progression import (
    HighScoreStore,
    OnePlayerProgress,
    PADDLE_COLOR_UNLOCKS,
    get_color_option,
    is_color_unlocked,
)


class TestOnePlayerProgress(unittest.TestCase):
    """Tests for non-graphical one-player progression logic."""

    def test_elapsed_time_scoring_is_frame_rate_independent(self) -> None:
        """Run score should come from elapsed seconds regardless of update chunk size."""

        progress = OnePlayerProgress(high_score=0.0)
        progress.tick(0.25)
        progress.tick(1.5)
        progress.tick(0.25)
        self.assertAlmostEqual(progress.current_run_seconds, 2.0)

    def test_high_score_updates_when_human_concedes(self) -> None:
        """Conceding should finalize run and keep only the best run as high score."""

        progress = OnePlayerProgress(high_score=1.0)
        progress.tick(4.0)
        self.assertTrue(progress.on_human_conceded())
        self.assertAlmostEqual(progress.high_score, 4.0)
        self.assertEqual(progress.current_run_seconds, 0.0)

        progress.tick(2.0)
        self.assertFalse(progress.on_human_conceded())
        self.assertAlmostEqual(progress.high_score, 4.0)

    def test_color_selection_rejects_locked_choices(self) -> None:
        """Players should only be able to select colors unlocked by high score."""

        default = PADDLE_COLOR_UNLOCKS[0]
        locked = PADDLE_COLOR_UNLOCKS[1]
        progress = OnePlayerProgress(high_score=default.threshold_seconds)

        self.assertTrue(progress.set_selected_color(default.color_id))
        self.assertFalse(progress.set_selected_color(locked.color_id))
        self.assertEqual(progress.selected_color_id, default.color_id)

    def test_unlock_threshold_rules(self) -> None:
        """Unlock helper should respect each color's threshold boundary exactly."""

        for option in PADDLE_COLOR_UNLOCKS:
            before = max(0.0, option.threshold_seconds - 0.1)
            self.assertEqual(is_color_unlocked(option.color_id, option.threshold_seconds), True)
            if option.threshold_seconds > 0.0:
                self.assertEqual(is_color_unlocked(option.color_id, before), False)
            self.assertIsNotNone(get_color_option(option.color_id))


class TestHighScoreStore(unittest.TestCase):
    """Tests for resilient score persistence file behavior."""

    def test_load_missing_or_malformed_data_falls_back_to_zero(self) -> None:
        """Store should return default score for missing file or invalid JSON."""

        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "progress.json"
            store = HighScoreStore(path=file_path)
            self.assertEqual(store.load_high_score(), 0.0)

            file_path.write_text("{not json", encoding="utf-8")
            self.assertEqual(store.load_high_score(), 0.0)

    def test_save_and_load_round_trip(self) -> None:
        """Writable score files should keep values across save/load calls."""

        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "progress.json"
            store = HighScoreStore(path=file_path)
            self.assertTrue(store.save_high_score(12.5))
            self.assertAlmostEqual(store.load_high_score(), 12.5)

    def test_save_failure_returns_false(self) -> None:
        """Unwritable destination should fail gracefully without exceptions."""

        with tempfile.TemporaryDirectory() as tmp_dir:
            dir_path = Path(tmp_dir) / "folder"
            dir_path.mkdir()
            store = HighScoreStore(path=dir_path)
            self.assertFalse(store.save_high_score(10.0))


if __name__ == "__main__":
    unittest.main()
