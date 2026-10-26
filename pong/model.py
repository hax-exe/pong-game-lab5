from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from . import settings


@dataclass(frozen=True)
class GameConfig:
    width: int = settings.SCREEN_WIDTH
    height: int = settings.SCREEN_HEIGHT
    paddle_width: int = settings.PADDLE_WIDTH
    paddle_height: int = settings.PADDLE_HEIGHT
    paddle_margin: int = settings.PADDLE_MARGIN
    paddle_speed: float = settings.PADDLE_SPEED
    ball_size: int = settings.BALL_SIZE
    ball_speed_x: float = settings.BALL_SPEED_X
    ball_speed_y: float = settings.BALL_SPEED_Y
    winning_score: int = settings.WINNING_SCORE


class GameMode(str, Enum):
    SINGLE_PLAYER = "single_player"
    TWO_PLAYER = "two_player"


@dataclass
class Paddle:
    x: float
    y: float
    width: int
    height: int
    speed: float

    def move(self, direction: float, dt: float, bounds_height: int) -> None:
        self.y += direction * self.speed * dt
        self.y = max(0.0, min(float(bounds_height - self.height), self.y))

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2


@dataclass
class Ball:
    x: float
    y: float
    size: int
    vx: float
    vy: float

    def move(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.size

    @property
    def top(self) -> float:
        return self.y

    @property
    def bottom(self) -> float:
        return self.y + self.size


@dataclass
class GameModel:
    mode: GameMode
    config: GameConfig = field(default_factory=GameConfig)

    def __post_init__(self) -> None:
        self.scores = [0, 0]
        self.winner: int | None = None
        self._serve_direction = 1
        self._serve_vertical_direction = 1
        self.left = Paddle(
            x=float(self.config.paddle_margin),
            y=float((self.config.height - self.config.paddle_height) / 2),
            width=self.config.paddle_width,
            height=self.config.paddle_height,
            speed=self.config.paddle_speed,
        )
        self.right = Paddle(
            x=float(self.config.width - self.config.paddle_margin - self.config.paddle_width),
            y=float((self.config.height - self.config.paddle_height) / 2),
            width=self.config.paddle_width,
            height=self.config.paddle_height,
            speed=self.config.paddle_speed,
        )
        self.ball = Ball(0.0, 0.0, self.config.ball_size, 0.0, 0.0)
        self.reset_round(self._serve_direction)

    def reset_round(self, serve_direction: int) -> None:
        self.left.y = float((self.config.height - self.left.height) / 2)
        self.right.y = float((self.config.height - self.right.height) / 2)
        self.ball.x = float((self.config.width - self.ball.size) / 2)
        self.ball.y = float((self.config.height - self.ball.size) / 2)
        self.ball.vx = self.config.ball_speed_x * float(serve_direction)
        self.ball.vy = self.config.ball_speed_y * float(self._serve_vertical_direction)
        self._serve_vertical_direction *= -1
        self._serve_direction = serve_direction

    def reset_match(self) -> None:
        self.scores = [0, 0]
        self.winner = None
        self._serve_direction = 1
        self._serve_vertical_direction = 1
        self.reset_round(self._serve_direction)

    def update(self, dt: float, left_up: bool, left_down: bool, right_up: bool = False, right_down: bool = False) -> None:
        if self.winner is not None:
            return

        self.left.move(float(left_down) - float(left_up), dt, self.config.height)

        if self.mode == GameMode.SINGLE_PLAYER:
            self._update_cpu(dt)
        else:
            self.right.move(float(right_down) - float(right_up), dt, self.config.height)

        self.ball.move(dt)
        self._handle_wall_collision()
        self._handle_paddle_collision()
        self._handle_scoring()

    def _update_cpu(self, dt: float) -> None:
        dead_zone = 8.0
        target = self.ball.y + self.ball.size / 2
        direction = 0.0
        if target < self.right.center_y - dead_zone:
            direction = -1.0
        elif target > self.right.center_y + dead_zone:
            direction = 1.0
        self.right.move(direction, dt, self.config.height)

    def _handle_wall_collision(self) -> None:
        if self.ball.top <= 0:
            self.ball.y = 0.0
            self.ball.vy = abs(self.ball.vy)
        elif self.ball.bottom >= self.config.height:
            self.ball.y = float(self.config.height - self.ball.size)
            self.ball.vy = -abs(self.ball.vy)

    def _intersects(self, paddle: Paddle) -> bool:
        return (
            self.ball.right >= paddle.x
            and self.ball.left <= paddle.x + paddle.width
            and self.ball.bottom >= paddle.y
            and self.ball.top <= paddle.y + paddle.height
        )

    def _handle_paddle_collision(self) -> None:
        if self.ball.vx < 0 and self._intersects(self.left):
            self.ball.x = self.left.x + self.left.width
            self.ball.vx = abs(self.ball.vx)
            self._apply_spin(self.left)

        if self.ball.vx > 0 and self._intersects(self.right):
            self.ball.x = self.right.x - self.ball.size
            self.ball.vx = -abs(self.ball.vx)
            self._apply_spin(self.right)

    def _apply_spin(self, paddle: Paddle) -> None:
        offset = (self.ball.y + self.ball.size / 2 - paddle.center_y) / (paddle.height / 2)
        offset = max(-1.0, min(1.0, offset))
        self.ball.vy = self.config.ball_speed_y * offset

    def _handle_scoring(self) -> None:
        if self.ball.right < 0:
            self._on_score(player=1, serve_direction=-1)
        elif self.ball.left > self.config.width:
            self._on_score(player=0, serve_direction=1)

    def _on_score(self, player: int, serve_direction: int) -> None:
        self.scores[player] += 1
        if self.scores[player] >= self.config.winning_score:
            self.winner = player
            self.ball.vx = 0.0
            self.ball.vy = 0.0
            return
        self.reset_round(serve_direction)
