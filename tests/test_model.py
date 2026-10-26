import unittest

from pong.model import GameConfig, GameMode, GameModel


class TestGameModel(unittest.TestCase):
    def test_paddle_stays_within_bounds(self) -> None:
        model = GameModel(mode=GameMode.TWO_PLAYER)

        model.left.y = 0
        model.left.move(direction=-1.0, dt=1.0, bounds_height=model.config.height)
        self.assertEqual(model.left.y, 0.0)

        model.left.y = model.config.height - model.left.height
        model.left.move(direction=1.0, dt=1.0, bounds_height=model.config.height)
        self.assertEqual(model.left.y, float(model.config.height - model.left.height))

    def test_ball_moves_with_velocity(self) -> None:
        model = GameModel(mode=GameMode.TWO_PLAYER)
        x0, y0 = model.ball.x, model.ball.y

        model.update(dt=0.5, left_up=False, left_down=False, right_up=False, right_down=False)

        self.assertNotEqual(model.ball.x, x0)
        self.assertNotEqual(model.ball.y, y0)

    def test_paddle_collision_reverses_horizontal_velocity(self) -> None:
        model = GameModel(mode=GameMode.TWO_PLAYER)
        model.ball.x = model.left.x + model.left.width - 1
        model.ball.y = model.left.y + model.left.height / 2
        model.ball.vx = -abs(model.ball.vx)
        model.ball.vy = 0

        model.update(dt=0.0, left_up=False, left_down=False, right_up=False, right_down=False)

        self.assertGreater(model.ball.vx, 0)

    def test_scoring_and_round_reset(self) -> None:
        model = GameModel(mode=GameMode.TWO_PLAYER)
        model.ball.x = -model.ball.size - 1

        model.update(dt=0.0, left_up=False, left_down=False, right_up=False, right_down=False)

        self.assertEqual(model.scores, [0, 1])
        self.assertIsNone(model.winner)
        self.assertAlmostEqual(model.ball.x, (model.config.width - model.ball.size) / 2)

    def test_winner_stops_ball(self) -> None:
        config = GameConfig(winning_score=1)
        model = GameModel(mode=GameMode.TWO_PLAYER, config=config)
        model.ball.x = config.width + 1

        model.update(dt=0.0, left_up=False, left_down=False, right_up=False, right_down=False)

        self.assertEqual(model.scores, [1, 0])
        self.assertEqual(model.winner, 0)
        self.assertEqual(model.ball.vx, 0.0)
        self.assertEqual(model.ball.vy, 0.0)

    def test_cpu_moves_toward_ball(self) -> None:
        model = GameModel(mode=GameMode.SINGLE_PLAYER)

        model.ball.y = 0
        initial_y = model.right.y
        model.update(dt=0.1, left_up=False, left_down=False)
        self.assertLess(model.right.y, initial_y)

        model.ball.y = model.config.height
        initial_y = model.right.y
        model.update(dt=0.1, left_up=False, left_down=False)
        self.assertGreater(model.right.y, initial_y)


if __name__ == "__main__":
    unittest.main()
