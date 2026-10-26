from __future__ import annotations

import pygame

from .model import GameModel


class GameView:
    BG = (18, 22, 38)
    FG = (235, 240, 255)
    ACCENT = (86, 220, 180)
    MUTED = (160, 170, 195)

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.title_font = pygame.font.Font(None, 64)
        self.score_font = pygame.font.Font(None, 96)
        self.body_font = pygame.font.Font(None, 30)

    def clear(self) -> None:
        self.screen.fill(self.BG)

    def text(self, value: str, font: pygame.font.Font, color: tuple[int, int, int], center: tuple[int, int]) -> None:
        surface = font.render(value, True, color)
        self.screen.blit(surface, surface.get_rect(center=center))

    def menu(self) -> None:
        self.clear()
        self.text("PONG", self.title_font, self.ACCENT, (450, 130))
        self.text("1  Single player (W/S vs CPU)", self.body_font, self.FG, (450, 270))
        self.text("2  Two players (W/S and ↑/↓)", self.body_font, self.FG, (450, 320))
        self.text("Press 1 or 2 to start • Esc to quit", self.body_font, self.MUTED, (450, 430))

    def game(self, model: GameModel) -> None:
        self.clear()
        for y in range(0, model.config.height, 30):
            pygame.draw.rect(self.screen, self.MUTED, (model.config.width // 2 - 2, y, 4, 16))
        pygame.draw.rect(self.screen, self.FG, (model.left.x, model.left.y, model.left.width, model.left.height))
        pygame.draw.rect(self.screen, self.FG, (model.right.x, model.right.y, model.right.width, model.right.height))
        pygame.draw.rect(self.screen, self.ACCENT, (model.ball.x, model.ball.y, model.ball.size, model.ball.size))
        self.text(str(model.scores[0]), self.score_font, self.FG, (model.config.width // 2 - 90, 75))
        self.text(str(model.scores[1]), self.score_font, self.FG, (model.config.width // 2 + 90, 75))
        if model.winner is not None:
            self.text(f"Player {model.winner + 1} wins!", self.title_font, self.ACCENT,
                      (model.config.width // 2, model.config.height // 2 - 20))
            self.text("Press R to play again • M for menu", self.body_font, self.MUTED,
                      (model.config.width // 2, model.config.height // 2 + 40))

    def present(self) -> None:
        pygame.display.flip()
