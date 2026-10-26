from __future__ import annotations

import pygame

from . import settings
from .model import GameMode, GameModel


class GameView:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.title_font = pygame.font.Font(None, 64)
        self.score_font = pygame.font.Font(None, 96)
        self.body_font = pygame.font.Font(None, 30)

    def clear(self) -> None:
        self.screen.fill(settings.COLOR_BG)

    def text(self, value: str, font: pygame.font.Font, color: tuple[int, int, int], center: tuple[int, int]) -> None:
        surface = font.render(value, True, color)
        self.screen.blit(surface, surface.get_rect(center=center))

    def menu(self) -> None:
        width, height = self.screen.get_size()
        self.clear()
        self.text("PONG", self.title_font, settings.COLOR_ACCENT, (width // 2, 130))
        self.text("1  Single player (W/S vs CPU)", self.body_font, settings.COLOR_FG, (width // 2, 270))
        self.text("2  Two players (W/S and ↑/↓)", self.body_font, settings.COLOR_FG, (width // 2, 320))
        self.text("Press 1 or 2 to start • Esc to quit", self.body_font, settings.COLOR_MUTED, (width // 2, 430))

    def game(self, model: GameModel) -> None:
        self.clear()
        for y in range(0, model.config.height, 30):
            pygame.draw.rect(self.screen, settings.COLOR_MUTED, (model.config.width // 2 - 2, y, 4, 16))

        pygame.draw.rect(self.screen, settings.COLOR_FG, (model.left.x, model.left.y, model.left.width, model.left.height))
        pygame.draw.rect(self.screen, settings.COLOR_FG, (model.right.x, model.right.y, model.right.width, model.right.height))
        pygame.draw.rect(self.screen, settings.COLOR_ACCENT, (model.ball.x, model.ball.y, model.ball.size, model.ball.size))

        self.text(str(model.scores[0]), self.score_font, settings.COLOR_FG, (model.config.width // 2 - 90, 75))
        self.text(str(model.scores[1]), self.score_font, settings.COLOR_FG, (model.config.width // 2 + 90, 75))

        mode_text = "Mode: Single player" if model.mode == GameMode.SINGLE_PLAYER else "Mode: Two players"
        controls_text = "Controls: W/S vs CPU" if model.mode == GameMode.SINGLE_PLAYER else "Controls: Left W/S • Right ↑/↓"
        self.text(mode_text, self.body_font, settings.COLOR_MUTED, (model.config.width // 2, model.config.height - 52))
        self.text(controls_text, self.body_font, settings.COLOR_MUTED, (model.config.width // 2, model.config.height - 24))
        self.text("R restart • M menu • Esc quit", self.body_font, settings.COLOR_MUTED, (model.config.width // 2, 22))

        if model.winner is not None:
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
        pygame.display.flip()
