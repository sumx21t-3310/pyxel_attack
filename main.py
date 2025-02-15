import pyxel


# =======================
# 🎨 インターフェース定義
# =======================

class Updatable:
    def update(self, **kwargs):
        pass


class Drawable:
    def draw(self):
        pass


class Collision:
    def __init__(self):
        self.callbacks = []

    def check_aabb_collision(self, other):
        """AABB (Axis-Aligned Bounding Box) 衝突判定"""
        return (
                self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y
        )

    def check(self, collisions):
        for other in collisions:
            if self.check_aabb_collision(other):
                for callback in self.callbacks:
                    callback(other)

    def listen(self, callback):
        self.callbacks.append(callback)


# ======================
# 🧱 基底クラス
# ======================

class GameObject(Updatable, Drawable):
    def __init__(self, x, y):
        self.x = x
        self.y = y


# =======================
# 🎮 入力クラス
# =======================

class Input:
    @staticmethod
    def direction():
        if pyxel.btn(pyxel.KEY_A):
            return -1
        if pyxel.btn(pyxel.KEY_D):
            return 1
        return 0


# =======================
# 🛶 パドルクラス
# =======================

class Paddle(GameObject, Collision):
    def __init__(self):
        super().__init__(270, 350)
        Collision.__init__(self)
        self.width = 60
        self.height = 10
        self.speed = 8

    def update(self):
        direction = Input.direction()

        self.x += direction * self.speed
        self.x = max(0, min(self.x, pyxel.width - self.width))

    def draw(self):
        pyxel.rect(self.x, self.y, self.width, self.height, 9)


# =======================
# ⚪ ボールクラス
# =======================

class Ball(GameObject, Collision):
    def __init__(self):
        super().__init__(300, 300)
        Collision.__init__(self)
        self.radius = 4
        self.width = self.radius * 2
        self.height = self.radius * 2
        self.dx = 4
        self.dy = -4

    def update(self):
        self.x += self.dx
        self.y += self.dy

        # 壁でバウンド
        if self.x < self.radius or self.x > pyxel.width - self.radius:
            self.dx *= -1
        if self.y < self.radius:
            self.dy *= -1

    def draw(self):
        pyxel.circ(self.x, self.y, self.radius, 7)


# =======================
# 🧱 ブロッククラス
# =======================

class Block(GameObject, Collision):
    def __init__(self, x, y, width=50, height=20, color=10):
        super().__init__(x, y)
        Collision.__init__(self)
        self.width = width
        self.height = height
        self.color = color
        self.active = True

    def draw(self):
        if self.active:
            pyxel.rect(self.x, self.y, self.width, self.height, self.color)


# =======================
# 🚫デッドゾーンクラス
# =======================

class DeadZone(GameObject, Collision):
    def __init__(self):
        super().__init__(0, pyxel.height - 5)
        Collision.__init__(self)
        self.width = pyxel.width
        self.height = 5

    def draw(self):
        pyxel.rect(self.x, self.y, self.width, self.height, 8)


# =======================
# ⭐ スコアクラス
# =======================

class Score(GameObject):
    def __init__(self):
        self.value = 0

    def add(self, points):
        self.value += points

    def draw(self):
        pyxel.text(10, 5, f"Score: {self.value}", 7)


# =======================
# 🧠 ゲームロジック
# =======================

class GameLogic:
    def __init__(self, ball, paddle, blocks, score, dead_zone):
        self.ball = ball
        self.paddle = paddle
        self.blocks = blocks
        self.dead_zone = dead_zone
        self.score = score
        self.game_over = False

        self.reset()

        ball.listen(self.on_paddle_collision)
        ball.listen(self.on_block_collision)
        dead_zone.listen(self.on_dead_zone_collision)

    def reset(self):
        self.score.value = 0
        self.ball.x, self.ball.y = 300, 300
        self.ball.dx, self.ball.dy = 4, -4
        self.paddle.y = 350

        for block in self.blocks:
            block.active = True
        self.game_over = False

    def on_game_over(self):
        self.game_over = True

    def on_paddle_collision(self, other):
        if isinstance(other, Paddle):
            self.ball.dy *= -1
            offset = (self.ball.x - (self.paddle.x + self.paddle.width / 2)) / (self.paddle.width / 2)
            self.ball.dx = offset * 5

    def on_block_collision(self, other):
        if isinstance(other, Block) and other.active:
            other.active = False
            self.ball.dy *= -1
            self.score.add(100)

            if all(not block.active for block in self.blocks):
                self.on_game_over()

    def on_dead_zone_collision(self, other):
        if isinstance(other, Ball):
            self.on_game_over()


# =======================
# 🎮 ゲームクラス
# =======================

def create_blocks():
    """ブロック生成"""
    blocks = []
    for row in range(5):
        for col in range(10):
            x = col * 55 + 25
            y = row * 25 + 50
            blocks.append(Block(x, y))
    return blocks


class BreakOut:
    def __init__(self):
        pyxel.init(600, 400, title="Break Out")

        self.paddle = Paddle()
        self.ball = Ball()
        self.blocks = create_blocks()
        self.score = Score()
        self.dead_zone = DeadZone()

        self.logic = GameLogic(self.ball, self.paddle, self.blocks, self.score, self.dead_zone)

        self.game_objects = [
            self.paddle,
            self.ball,
            self.score,
            self.dead_zone,
            *self.blocks
        ]

        self.collisions = [obj for obj in self.game_objects if isinstance(obj, Collision)]

        pyxel.run(self.update, self.draw)

    def update(self):
        """ゲーム全体の更新処理"""
        if self.logic.game_over:
            if pyxel.btnp(pyxel.KEY_R):
                self.logic = GameLogic(self.ball, self.paddle, self.blocks, self.score, self.dead_zone)
            return

        for col in self.collisions:
            col.check(self.collisions)

        for obj in self.game_objects:
            obj.update()

    def draw(self):
        pyxel.cls(0)
        for obj in self.game_objects:
            obj.draw()

        if self.logic.game_over:
            pyxel.text(240, 180, "GAME OVER!", 8)
            pyxel.text(220, 200, "Press R to Restart", 7)


BreakOut()
