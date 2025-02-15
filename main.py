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
    def aabb_collision(self, other):
        """AABB (Axis-Aligned Bounding Box) 衝突判定"""
        return (
            self.x < other.x + other.width and
            self.x + self.width > other.x and
            self.y < other.y + other.height and
            self.y + self.height > other.y
        )


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
    @property
    def direction(self):
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
        self.width = 60
        self.height = 10
        self.speed = 8

    def update(self, direction):
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
        self.width = width
        self.height = height
        self.color = color
        self.active = True

    def draw(self):
        if self.active:
            pyxel.rect(self.x, self.y, self.width, self.height, self.color)


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
    @staticmethod
    def check_collision(ball, paddle):
        """ボールとパドルの衝突判定"""
        if paddle.aabb_collision(ball):
            ball.dy *= -1
            offset = (ball.x - (paddle.x + paddle.width / 2)) / (paddle.width / 2)
            ball.dx = offset * 5

    @staticmethod
    def check_block_collision(ball, blocks, score):
        """ボールとブロックの衝突判定"""
        for block in blocks:
            if block.active and block.aabb_collision(ball):
                block.active = False
                ball.dy *= -1
                score.add(100)
                break


# =======================
# 🎮 ゲームクラス
# =======================

class BreakOut:
    def __init__(self):
        pyxel.init(600, 400, title="Break Out")
        self.input = Input()
        self.paddle = Paddle()
        self.ball = Ball()
        self.blocks = self.create_blocks()
        self.score = Score()
        self.game_over = False
        pyxel.run(self.update, self.draw)

    def create_blocks(self):
        """ブロック生成"""
        blocks = []
        for row in range(5):
            for col in range(10):
                x = col * 55 + 25
                y = row * 25 + 50
                blocks.append(Block(x, y))
        return blocks

    def update(self):
        """ゲーム全体の更新処理"""
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R):
                self.reset_game()
            return

        direction = self.input.direction
        self.paddle.update(direction)
        self.ball.update()

        # 衝突判定
        GameLogic.check_collision(self.ball, self.paddle)
        GameLogic.check_block_collision(self.ball, self.blocks, self.score)

        # ボールが下に落ちたらゲームオーバー
        if self.ball.y > pyxel.height:
            self.game_over = True

        # 全てのブロックが破壊されたらゲームクリア
        if all(not block.active for block in self.blocks):
            self.game_over = True

    def reset_game(self):
        """ゲームをリセット"""
        self.ball.x, self.ball.y = 300, 300
        self.ball.dx, self.ball.dy = 4, -4
        self.blocks = self.create_blocks()
        self.score.value = 0
        self.game_over = False

    def draw(self):
        """描画処理"""
        pyxel.cls(0)
        self.paddle.draw()
        self.ball.draw()
        self.score.draw()
        for block in self.blocks:
            block.draw()

        if self.game_over:
            pyxel.text(240, 180, "GAME OVER!", 8)
            pyxel.text(220, 200, "Press R to Restart", 7)


# ゲーム実行
BreakOut()
