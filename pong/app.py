from __future__ import annotations

"""Application/controller layer for the Pong MVC example."""

from enum import Enum, auto

import pygame

from . import settings
from .model import GameConfig, GameMode, GameModel
from .view import GameView


class AppState(Enum):
    """High-level screens the app can be in."""

    MENU = auto()
    GAME = auto()


class PongApp:
    """Coordinates input/events and delegates state + rendering to model/view."""

    def __init__(self) -> None:
        pygame.init()
        self.config = GameConfig()
        self.screen = pygame.display.set_mode((self.config.width, self.config.height))
        pygame.display.set_caption("Pong")
        self.clock = pygame.time.Clock()
        self.view = GameView(self.screen)
        self.state = AppState.MENU
        self.model: GameModel | None = None

        # Resolve key names from settings once so each frame can read key state by index.
        self.left_up_key = pygame.key.key_code(settings.LEFT_UP_KEY)
        self.left_down_key = pygame.key.key_code(settings.LEFT_DOWN_KEY)
        self.right_up_key = pygame.key.key_code(settings.RIGHT_UP_KEY)
        self.right_down_key = pygame.key.key_code(settings.RIGHT_DOWN_KEY)

    def start_game(self, mode: GameMode) -> None:
        """Create a fresh model for the selected mode and switch to gameplay."""

        self.model = GameModel(mode=mode, config=self.config)
        self.state = AppState.GAME

    def _handle_menu_keydown(self, key: int) -> bool:
        """Handle menu-only keys. Returns False when the app should exit."""

        if key == pygame.K_1:
            self.start_game(GameMode.SINGLE_PLAYER)
        elif key == pygame.K_2:
            self.start_game(GameMode.TWO_PLAYER)
        elif key == pygame.K_ESCAPE:
            return False
        return True

    def _handle_game_keydown(self, key: int) -> bool:
        """Handle global in-game actions without directly mutating render code."""

        if key == pygame.K_ESCAPE:
            return False
        if self.model is None:
            return True
        if key == pygame.K_r:
            self.model.reset_match()
        elif key == pygame.K_m:
            self.model = None
            self.state = AppState.MENU
        return True

    def run(self) -> None:
        """Main loop: poll events, update model from input, then draw current scene."""

        running = True
        while running:
            # `tick` caps frame rate and returns elapsed milliseconds for frame-independent motion.
            dt = self.clock.tick(settings.FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.state == AppState.MENU:
                        running = self._handle_menu_keydown(event.key)
                    else:
                        running = self._handle_game_keydown(event.key)

            if self.state == AppState.GAME and self.model is not None:
                keys = pygame.key.get_pressed()
                self.model.update(
                    dt=dt,
                    left_up=keys[self.left_up_key],
                    left_down=keys[self.left_down_key],
                    # In single-player mode the right paddle is owned by CPU logic in the model.
                    right_up=keys[self.right_up_key] if self.model.mode == GameMode.TWO_PLAYER else False,
                    right_down=keys[self.right_down_key] if self.model.mode == GameMode.TWO_PLAYER else False,
                )
                self.view.game(self.model)
            else:
                self.view.menu()

            self.view.present()

        pygame.quit()
