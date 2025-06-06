import os
import sys
import pygame as pg

WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    画面下では跳ね返らない
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0:  # 画面下は飛び出る
        tate = False
    return yoko, tate


class Bord(pg.sprite.Sprite):
    """
    ゲームキャラクター（操作バー）に関するクラス
    """

    delta = {  # 押下キーと移動量の辞書
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }

    def __init__(self):
        """
        操作バーSurfaceを生成する
        引数 xy：操作バーの初期位置座標タプル
        """
        super().__init__()
        # 画像を用意
        self.image = pg.Surface((80, 20))  # 操作バーを作成
        pg.draw.rect(self.image, (0, 0, 0), (0, 0, 80, 20))
        self.rect = self.image.get_rect()
        self.dire = (+1, 0)
        self.rect.center = (WIDTH / 2, HEIGHT - 30)  # 中央下に配置
        self.speed = 20

    def accelerate(self):
        """
        バーを少し加速させる
        """
        acceleration = 1.05  # 5%加速
        self.speed *= acceleration

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じて操作バーを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        # 加速された速度を反映
        move_x = sum_mv[0] * (self.speed / 20)  # 基準速度20で正規化
        move_y = sum_mv[1] * (self.speed / 20)
        self.rect.move_ip(move_x, move_y)
        if check_bound(self.rect) != (True, True):
            self.rect.move_ip(-move_x, -move_y)
        screen.blit(self.image, self.rect)


# 個々のブロッククラス
class Block(pg.sprite.Sprite):
    """
    ブロックを表すクラス
    """
    def __init__(self, x: int, y: int, color: tuple[int, int, int]=(255, 0, 0)):
        """
        引数1,2 配置座標
        引数3 色
        """
        super().__init__()
        self.image = pg.Surface((80, 30)) # 大きさ
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)


# ブロックのグループを管理するクラス
class BlockGroup(pg.sprite.Group):
    """
    複数のブロックを管理するクラス
    """

    def __init__(self):
        super().__init__()
        # インスタンス化したらブロックを生成
        self.create_blocks()

    def create_blocks(self):
        """
        ブロックを生成する
        """
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
        for y in range(6):  # 行
            for x in range(13): # 列
                color = colors[y % len(colors)]
                block = Block(x * 85, y * 35 + 50, color)
                self.add(block)

    def update(self, screen: pg.Surface):
        """
        全てのブロックを更新する
        """
        for block in self.sprites():
            block.update(screen)

    def check_collision(self, _ball: "Ball") -> bool:
        """
        ボールとブロックの衝突を検出し、衝突したブロック数を返す（矩形判定）
        """
        collision_count = 0
        blocks_to_remove = []
        
        for block in self.sprites():
            # 矩形の当たり判定
            if _ball.rect.colliderect(block.rect):
                blocks_to_remove.append(block)
                collision_count += 1
        
        # 衝突したブロックを削除
        for block in blocks_to_remove:
            self.remove(block)
            
        if collision_count > 0:
            _ball.accelerate()
            
        return collision_count


class Ball(pg.sprite.Sprite):
    """
    こうかとんボールに関するクラス
    """

    def __init__(self):
        """
        こうかとんSurfaceを生成する
        """
        super().__init__()
        self.original_image = pg.transform.rotozoom(
            pg.image.load("fig/ball.png"), 0, 0.9
        )  # 元画像を保存
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT - 60)  # バー上を初期位置に
        self.vx, self.vy = +5, +5
        self.angle = 0  # 回転角度

    def accelerate(self):
        """
        ボールを少し加速させる
        """
        acceleration = 1.05  # 5%加速
        self.vx *= acceleration
        self.vy *= acceleration

    def update(self):
        """
        こうかとんを速度ベクトルself.vx, self.vyに基づき移動させる
        """
        yoko, tate = check_bound(self.rect)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1

        # 回転処理
        self.angle += 5  # 回転速度
        if self.angle >= 360:
            self.angle = 0

        # 回転した画像を生成
        self.image = pg.transform.rotozoom(self.original_image, self.angle, 1.0)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center

        self.rect.move_ip(self.vx, self.vy)


class Clear:
    """
    ブロックを全て壊した時のエフェクト
    """

    def __init__(self):
        self.fonto = pg.font.SysFont("bizudgothic", 30)
        self.color = (0, 0, 255)
        self.cle = "よくぞ、全てのブロックを崩せた！クリア本当におめでとう！！" # 表示テキスト
        self.image = pg.Surface((WIDTH, HEIGHT))
        pg.draw.rect(self.image, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
        self.rect = self.image.get_rect()
        self.image.set_alpha(128)

    def update(self, screen: pg.Surface):
        self.img = self.fonto.render(self.cle, 0, self.color)
        screen.blit(self.img, self.rect)


class Score:
    """
    スコアを管理するクラス
    """

    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (255, 255, 255)
        self.value = 0 # 初期スコア
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT - 50

    def add_score(self, points: int):
        """
        スコアを加算する
        """
        self.value += points

    def update(self, screen: pg.Surface):
        """
        スコアを画面に描画する
        """
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)


class Lose:
    """
    ゲームオーバー画面に関するクラス
    """

    def __init__(self):
        self.bg_img = pg.transform.smoothscale(
            pg.image.load("fig/bg.jpeg"), (WIDTH, HEIGHT)
        )
        self.lose_img = pg.image.load("fig/sprGAMEOVER.png")
        lose_w, lose_h = self.lose_img.get_size()
        self.lose_x = (WIDTH - lose_w) // 2
        self.lose_y = (HEIGHT - lose_h) // 2

    def draw(self, screen: pg.Surface):
        screen.blit(self.bg_img, (0, 0))
        screen.blit(self.lose_img, (self.lose_x, self.lose_y))


def main():
    pg.display.set_caption("壁にレッツゴーこうかとん！")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")

    bord = Bord()
    blocks = BlockGroup()
    balls = pg.sprite.Group()
    balls.add(Ball())
    clear = Clear()
    score = Score()
    clock = pg.time.Clock()
    tmr = 0
    lose_screen = None
    is_gameover = False
    is_clear = False

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        if not is_gameover and not is_clear:
            screen.blit(bg_img, [0, 0])

            # GameOver判定時
            for ball in balls:
                if ball.rect.bottom >= HEIGHT:
                    is_gameover = True
                    lose_screen = Lose()  # 一度だけ生成

            for bird in pg.sprite.spritecollide(
                bord, balls, False
            ):  # バーとbirdが衝突したとき
                # ボールをバーの上に押し戻す
                bird.rect.bottom = bord.rect.top
                bird.vy = abs(bird.vy) * -1  # 上方向に反転（負の値にする）

            # ボールとブロックが衝突したとき
            for ball in balls:
                collision_count = blocks.check_collision(ball)
                if collision_count > 0:
                    ball.vy *= -1
                    bord.accelerate()  # バーも加速
                    score.add_score(10 * collision_count)  # 衝突したブロック数分スコア加算

            # ブロックが全て消えたらクリア
            if len(blocks) == 0:
                is_clear = True

            key_lst = pg.key.get_pressed()
            bord.update(key_lst, screen)
            blocks.update(screen)
            balls.update()
            balls.draw(screen)
        # GameOver中
        elif is_clear:
            clear = Clear()
            clear.update(screen)
        else:
            # GameOver画面を3秒間表示し続ける
            if lose_screen is not None:
                lose_screen.draw(screen)
            # Rキーを押すまで待機
            for event in pg.event.get():
                if event.type == pg.KEYDOWN and event.key == pg.K_r:
                    is_gameover = False
                    blocks = BlockGroup()  # ブロックを再生成
                    balls.empty()
                    balls.add(Ball())
                    bord = Bord()
                    score = Score()
                    is_clear = False
                if event.type == pg.QUIT:
                    return

        # スコア表示
        score.update(screen)

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
