import constants
from constants import *
import time

from .views import LiveGames

# class GameController:
#     state = constants.INITIAL_STATE


class PaddleController:
    def __init__(self, paddle, state):
        
        self.state = state
        self.paddle = paddle
        self.item = self.state[paddle]

    async def move(self, direction):
        if direction == "down" and self.item["y"] < constants.MAX_PADDLE_Y - constants.PADDLE_STEP:
            self.item["y"] += constants.PADDLE_STEP

        elif direction == "up" and self.item["y"] > 0 + constants.PADDLE_STEP:
            self.item["y"] -= constants.PADDLE_STEP

    def __str__(self):
        return self.paddle


class BallController:
    def __init__(self, state):
        self.state = state
        self.item = self.state["ball"]
        self.paddle1 = self.state["paddle1"]
        self.paddle2 = self.state["paddle2"]

        self.reset_ball()

        self.time = time.time()

    def reset_ball(self):
        self.vel_x = constants.MAX_VEL
        self.vel_y = 0
        self.item["x"] = constants.SCREEN_CENTER[0]
        self.item["y"] = constants.SCREEN_CENTER[1]

    async def move(self):
        if (
            self.item["y"] > constants.MAX_BALL_Y
            or self.item["y"] < constants.BALL_HEIGHT
        ):
            self.vel_y = -self.vel_y

        if 0 < self.item["x"] <= constants.PADDLE_WIDTH:
            if (
                self.paddle1["y"]
                < (self.item["y"] + BALL_WIDTH)
                < (self.paddle1["y"] + constants.PADDLE_HEIGHT + BALL_WIDTH)
            ):
                middle_y = self.paddle1["y"] + constants.PADDLE_HEIGHT / 2
                difference_in_y = middle_y - self.item["y"]
                reduction_factor = (constants.PADDLE_HEIGHT / 2) / constants.MAX_VEL
                y_vel = difference_in_y / reduction_factor

                self.vel_x = -self.vel_x
                self.vel_x =  self.vel_x * 1.05
                self.vel_y = -1 * y_vel
                self.item["x"] += 7

        elif self.item["x"] < 0:
            self.paddle2["score"] += 1
            if self.paddle2["score"] == 10:
                self.state["winner"] = self.paddle2["id"]
                await LiveGames().set_winner(self.state["winner"], self.paddle1["id"])
            self.reset_ball()
            self.vel_x = -self.vel_x


        elif constants.SCREEN_WIDTH > self.item["x"] >= constants.MAX_BALL_X:
            if (
                self.paddle2["y"]
                < (self.item["y"]) + BALL_WIDTH
                < (self.paddle2["y"] + constants.PADDLE_HEIGHT + BALL_WIDTH)
            ):

                middle_y = self.paddle2["y"] + constants.PADDLE_HEIGHT / 2
                difference_in_y = middle_y - self.item["y"]
                reduction_factor = (constants.PADDLE_HEIGHT / 2) / constants.MAX_VEL
                y_vel = difference_in_y / reduction_factor

                self.vel_x = -self.vel_x
                self.vel_x =  self.vel_x * 1.05
                self.vel_y = -1 * y_vel
                self.item["x"] -= 7

        elif self.item["x"] >= constants.SCREEN_WIDTH:
            self.paddle1["score"] += 1
            if self.paddle1["score"] == 10:
                self.state["winner"] = self.paddle1["id"]
                await LiveGames().set_winner(self.state["winner"], self.paddle2["id"])
            self.reset_ball()

        self.item["x"] += self.vel_x
        self.item["y"] += self.vel_y