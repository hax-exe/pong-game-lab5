from __future__ import annotations

"""Application/controller layer for the Pong MVC example."""

from enum import Enum, auto

import pygame

from . import settings
from .model import GameConfig, GameMode, GameModel
from .progression import HighScoreStore, OnePlayerProgress, PADDLE_COLOR_UNLOCKS
from .view import GameView


class AppState(Enum):
    """High-level screens the app can be in."""

    MENU = auto()
    SINGLE_PLAYER_SETUP = auto()
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
        self.high_score_store = HighScoreStore()
        self.one_player = OnePlayerProgress(high_score=self.high_score_store.load_high_score())
        self.single_player_color_index = self._color_index_for_id(self.one_player.selected_color_id)
        self.single_player_feedback = ""

        # Resolve key names from settings once so each frame can read key state by index.
        self.left_up_key = pygame.key.key_code(settings.LEFT_UP_KEY)
        self.left_down_key = pygame.key.key_code(settings.LEFT_DOWN_KEY)
        self.right_up_key = pygame.key.key_code(settings.RIGHT_UP_KEY)
        self.right_down_key = pygame.key.key_code(settings.RIGHT_DOWN_KEY)

    def start_game(self, mode: GameMode) -> None:
        """Create a fresh model for the selected mode and switch to gameplay."""

        self.model = GameModel(mode=mode, config=self.config)
        if mode == GameMode.SINGLE_PLAYER:
            self.one_player.reset_current_run()
        self.state = AppState.GAME

    def _color_index_for_id(self, color_id: str) -> int:
        """Find where a color appears in the setup list so keyboard cycling stays stable."""

        for index, option in enumerate(PADDLE_COLOR_UNLOCKS):
            if option.color_id == color_id:
                return index
        return 0

    def _cycle_single_player_color(self, step: int) -> None:
        """Move setup selection cursor and show if that option is locked or selectable."""

        option_count = len(PADDLE_COLOR_UNLOCKS)
        self.single_player_color_index = (self.single_player_color_index + step) % option_count
        option = PADDLE_COLOR_UNLOCKS[self.single_player_color_index]
        if self.one_player.set_selected_color(option.color_id):
            self.single_player_feedback = f"Selected {option.label}"
        else:
            self.single_player_feedback = f"Locked until {option.threshold_seconds:.0f}s high score"

    def _start_single_player_if_unlocked(self) -> None:
        """Start one-player only when current setup choice is unlocked."""

        option = PADDLE_COLOR_UNLOCKS[self.single_player_color_index]
        if self.one_player.set_selected_color(option.color_id):
            self.single_player_feedback = ""
            self.start_game(GameMode.SINGLE_PLAYER)
        else:
            self.single_player_feedback = f"{option.label} is locked ({option.threshold_seconds:.0f}s needed)"

    def _handle_menu_keydown(self, key: int) -> bool:
        """Handle menu-only keys. Returns False when the app should exit."""

        if key == pygame.K_1:
            self.state = AppState.SINGLE_PLAYER_SETUP
            self.single_player_feedback = ""
            self.single_player_color_index = self._color_index_for_id(self.one_player.selected_color_id)
        elif key == pygame.K_2:
            self.start_game(GameMode.TWO_PLAYER)
        elif key == pygame.K_ESCAPE:
            return False
        return True

    def _handle_single_player_setup_keydown(self, key: int) -> bool:
        """Handle one-player setup controls for color cycling and start/back actions."""

        if key in (pygame.K_LEFT, pygame.K_a):
            self._cycle_single_player_color(-1)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self._cycle_single_player_color(1)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self._start_single_player_if_unlocked()
        elif key in (pygame.K_ESCAPE, pygame.K_m):
            self.state = AppState.MENU
        return True

    def _handle_game_keydown(self, key: int) -> bool:
        """Handle global in-game actions without directly mutating render code."""

        if key == pygame.K_ESCAPE:
            return False
        if self.model is None:
            return True
        if key == pygame.K_r:
            self.model.reset_match()
            if self.model.mode == GameMode.SINGLE_PLAYER:
                self.one_player.reset_current_run()
        elif key == pygame.K_m:
            self.model = None
            self.one_player.reset_current_run()
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
                    elif self.state == AppState.SINGLE_PLAYER_SETUP:
                        running = self._handle_single_player_setup_keydown(event.key)
                    else:
                        running = self._handle_game_keydown(event.key)

            if self.state == AppState.GAME and self.model is not None:
                keys = pygame.key.get_pressed()
                old_cpu_score = self.model.scores[1]
                if self.model.mode == GameMode.SINGLE_PLAYER and self.model.winner is None:
                    self.one_player.tick(dt)
                self.model.update(
                    dt=dt,
                    left_up=keys[self.left_up_key],
                    left_down=keys[self.left_down_key],
                    # In single-player mode the right paddle is owned by CPU logic in the model.
                    right_up=keys[self.right_up_key] if self.model.mode == GameMode.TWO_PLAYER else False,
                    right_down=keys[self.right_down_key] if self.model.mode == GameMode.TWO_PLAYER else False,
                )
                if self.model.mode == GameMode.SINGLE_PLAYER and self.model.scores[1] > old_cpu_score:
                    # Human conceded on the left side, so this run ends and may set a new best.
                    if self.one_player.on_human_conceded():
                        self.high_score_store.save_high_score(self.one_player.high_score)
                paddle_color = self.one_player.selected_color() if self.model.mode == GameMode.SINGLE_PLAYER else settings.COLOR_FG
                self.view.game(
                    self.model,
                    left_paddle_color=paddle_color,
                    one_player_survival_seconds=self.one_player.current_run_seconds if self.model.mode == GameMode.SINGLE_PLAYER else None,
                    one_player_high_score_seconds=self.one_player.high_score if self.model.mode == GameMode.SINGLE_PLAYER else None,
                )
            elif self.state == AppState.SINGLE_PLAYER_SETUP:
                selected_option = PADDLE_COLOR_UNLOCKS[self.single_player_color_index]
                self.view.single_player_setup(
                    high_score_seconds=self.one_player.high_score,
                    selected_color_id=selected_option.color_id,
                    active_color_id=self.one_player.selected_color_id,
                    setup_feedback=self.single_player_feedback,
                )
            else:
                self.view.menu(one_player_high_score_seconds=self.one_player.high_score)

            self.view.present()

        pygame.quit()
