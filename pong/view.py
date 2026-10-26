from __future__ import annotations

"""View layer responsible for translating model state into pixels/text."""

import pygame

from . import settings
from .model import GameMode, GameModel
from .progression import PADDLE_COLOR_UNLOCKS, is_color_unlocked


class GameView:
    """Rendering-only surface helper for menu and gameplay scenes."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.title_font = pygame.font.Font(None, 64)
        self.score_font = pygame.font.Font(None, 96)
        self.body_font = pygame.font.Font(None, 30)

    def clear(self) -> None:
        """Paint a clean background before drawing a frame."""

        self.screen.fill(settings.COLOR_BG)

    def text(self, value: str, font: pygame.font.Font, color: tuple[int, int, int], center: tuple[int, int]) -> None:
        """Render centered text, used by both menu and in-game HUD."""

        surface = font.render(value, True, color)
        self.screen.blit(surface, surface.get_rect(center=center))

    def menu(self, one_player_high_score_seconds: float | None = None) -> None:
        """Draw the main menu with mode options and global controls."""

        width, height = self.screen.get_size()
        self.clear()
        self.text("PONG", self.title_font, settings.COLOR_ACCENT, (width // 2, 130))
        self.text("1  Single player (W/S vs CPU)", self.body_font, settings.COLOR_FG, (width // 2, 270))
        self.text("2  Two players (W/S and ↑/↓)", self.body_font, settings.COLOR_FG, (width // 2, 320))
        if one_player_high_score_seconds is not None:
            self.text(
                f"One-player best survival: {one_player_high_score_seconds:.1f}s",
                self.body_font,
                settings.COLOR_MUTED,
                (width // 2, 372),
            )
        self.text("Press 1 or 2 to start • Esc to quit", self.body_font, settings.COLOR_MUTED, (width // 2, 430))

    def single_player_setup(
        self,
        high_score_seconds: float,
        selected_color_id: str,
        active_color_id: str,
        setup_feedback: str = "",
    ) -> None:
        """Draw one-player setup where users can preview locked/unlocked paddle colors."""

        width, _ = self.screen.get_size()
        self.clear()
        self.text("Single-player setup", self.title_font, settings.COLOR_ACCENT, (width // 2, 95))
        self.text(f"Best survival score: {high_score_seconds:.1f}s", self.body_font, settings.COLOR_FG, (width // 2, 155))

        y = 220
        for option in PADDLE_COLOR_UNLOCKS:
            unlocked = is_color_unlocked(option.color_id, high_score_seconds)
            cursor = ">" if option.color_id == selected_color_id else " "
            active = " • selected" if option.color_id == active_color_id and unlocked else ""
            lock_text = "unlocked" if unlocked else f"locked ({option.threshold_seconds:.0f}s)"
            line = f"{cursor} {option.label} - {lock_text}{active}"
            line_color = option.color if unlocked else settings.COLOR_MUTED
            self.text(line, self.body_font, line_color, (width // 2, y))
            y += 36

        if setup_feedback:
            self.text(setup_feedback, self.body_font, settings.COLOR_ACCENT, (width // 2, y + 18))

        self.text("A/← previous • D/→ next", self.body_font, settings.COLOR_MUTED, (width // 2, 430))
        self.text("Enter/Space start • Esc/M menu", self.body_font, settings.COLOR_MUTED, (width // 2, 462))

    def game(
        self,
        model: GameModel,
        left_paddle_color: tuple[int, int, int] = settings.COLOR_FG,
        one_player_survival_seconds: float | None = None,
        one_player_high_score_seconds: float | None = None,
    ) -> None:
        """Draw one gameplay frame from the current model snapshot."""

        self.clear()
        # Dashed center line reinforces player sides and score positions.
        for y in range(0, model.config.height, 30):
            pygame.draw.rect(self.screen, settings.COLOR_MUTED, (model.config.width // 2 - 2, y, 4, 16))

        pygame.draw.rect(self.screen, left_paddle_color, (model.left.x, model.left.y, model.left.width, model.left.height))
        pygame.draw.rect(self.screen, settings.COLOR_FG, (model.right.x, model.right.y, model.right.width, model.right.height))
        pygame.draw.rect(self.screen, settings.COLOR_ACCENT, (model.ball.x, model.ball.y, model.ball.size, model.ball.size))

        self.text(str(model.scores[0]), self.score_font, settings.COLOR_FG, (model.config.width // 2 - 90, 75))
        self.text(str(model.scores[1]), self.score_font, settings.COLOR_FG, (model.config.width // 2 + 90, 75))

        mode_text = "Mode: Single player" if model.mode == GameMode.SINGLE_PLAYER else "Mode: Two players"
        controls_text = "Controls: W/S vs CPU" if model.mode == GameMode.SINGLE_PLAYER else "Controls: Left W/S • Right ↑/↓"
        self.text(mode_text, self.body_font, settings.COLOR_MUTED, (model.config.width // 2, model.config.height - 52))
        self.text(controls_text, self.body_font, settings.COLOR_MUTED, (model.config.width // 2, model.config.height - 24))
        self.text("R restart • M menu • Esc quit", self.body_font, settings.COLOR_MUTED, (model.config.width // 2, 22))
        if one_player_survival_seconds is not None:
            self.text(f"Survival run: {one_player_survival_seconds:.1f}s", self.body_font, settings.COLOR_ACCENT, (170, 22))
        if one_player_high_score_seconds is not None:
            self.text(f"Best: {one_player_high_score_seconds:.1f}s", self.body_font, settings.COLOR_MUTED, (170, 48))

        if model.winner is not None:
            # Winner overlay is informational only; controller still owns restart/menu actions.
            self.text(
                f"Player {model.winner + 1} wins!",
                self.title_font,
                settings.COLOR_ACCENT,
                (model.config.width // 2, model.config.height // 2 - 20),
            )
            self.text(
                "Press R to play again • M for menu",
                self.body_font,
                settings.COLOR_MUTED,
                (model.config.width // 2, model.config.height // 2 + 40),
            )

    def present(self) -> None:
        """Swap back buffer to the screen."""

        pygame.display.flip()
