import pygame
from pygame.locals import *
from loader import load_image, split_image
import sys
import random

SCR_RECT = Rect(0, 0, 768, 576)
CELL_SIZE = 32
WINDOW_ROW = SCR_RECT.height // CELL_SIZE
WINDOW_COL = SCR_RECT.width // CELL_SIZE
FIELD_COL, FIELD_ROW = 8, 16
SUN, EARTH, FIX, OJAMA = 0, 1, 2, 3
UPPER, RIGHT, DOWN, LEFT = 0, 1, 2, 3

class Puyopuyo:
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode(SCR_RECT.size)
        pygame.display.set_caption(u"Puyopuyo")
        self.initialize(screen)
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            self.draw(screen)
            self.update()
            
            self.draw_grid(screen) #デバッグ.
            pygame.display.update()
            self.key_handler()

    def initialize(self, screen):
        """ゲームオブジェクトの初期化"""
        self.all = pygame.sprite.RenderUpdates()
        Field.containers = self.all
        Field.image = load_image("background.png")
        Field.screen = screen
        
        Puyo.containers = self.all
        Puyo.images = split_image(load_image("puyo.png"), 6)
        self.field = Field(1, 1)
        self.puyoOpelator = PuyoOperator(self.field)
        self.puyoOpelator.makePuyo()
    def update(self):
        """ゲーム状態の更新"""
        self.puyoOpelator.update()
        self.all.update()
    def draw(self, screen):
        """描画"""
        screen.fill((50, 50, 50))
        self.all.draw(screen)
    def key_handler(self):
        """キーハンドラー"""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
    def draw_grid(self, screen):
        """グリッドの描画(主にデバッグ用)"""
        for y in range(WINDOW_ROW):
            for x in range(WINDOW_COL):
                pygame.draw.rect(screen, (150, 150, 150), Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

class Field(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.left = x * CELL_SIZE
        self.rect.top = y * CELL_SIZE
        # 左上の座標
        self.x, self.y = x, y
        # field初期化.
        self.field = [[0 for i in range(FIELD_COL)] for j in range(FIELD_ROW)]
        for row in range(FIELD_ROW):
            self.field[row][0] = -1
            self.field[row][FIELD_COL-1] = -1
            if row == 0 or row == FIELD_ROW-1:
                for col in range(FIELD_COL):
                    self.field[row][col] = -1
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    def update(self):
        self.allFall()
        self.updatePuyoPosition()
    def updatePuyoPosition(self):
        """"field上で移動したぷよをその位置に描画する"""
        for i in range(FIELD_COL):
            for j in range(FIELD_ROW):
                #壁でも空でもない場合(=ぷよ).
                if not(self.field[j][i] == 0 or self.field[j][i] == -1):
                     self.field[j][i].setPosition(i+self.x, j+self.y)
    def allFall(self):
        """fieldにある全てのぷよを落とす"""
        #上の隠れている2段に置かれたぷよは消滅.
        # TODO デバッグ用で有効にすると.出現位置の回転ぷよが消えてしまう.
        # for i in range(FIELD_COL):
        #     for j in range(2):
        #         if not(self.field[j][i] == 0 or self.field[j][i] == -1):
        #             self.field[j][i].kill()
        #             self.field[j][i] = 0
        #ぷよを下に落とす.
        for i in range(FIELD_COL):
            for j in range(FIELD_ROW):
                #壁でも空でもない場合(=ぷよ).
                if not(self.field[FIELD_ROW-j-1][FIELD_COL-i-1] == 0 or self.field[FIELD_ROW-j-1][FIELD_COL-i-1] == -1):
                    self.fall(FIELD_ROW-j-1, FIELD_COL-i-1)
    def fall(self, y, x):
        """(x, y)にあるぷよを一番下に落とす"""
        n = 0
        while self.field[y+n+1][x] == 0:
            n += 1
        if n == 0:
            return
        self.field[y+n][x] = self.field[y][x]
        self.field[y][x] = 0
    def getApparitionPosition(self):
        """ぷよ出現位置を返す"""
        # xはfieldの中心、yは上から3番目の位置.
        return (self.x + FIELD_COL // 2 - 1), (self.y + 2)
    def getElement(self, x, y):
        return self.field[y-self.y][x-self.x]
    def addPuyo(self, puyo):
        x, y = puyo.getPosition()
        self.field[y-self.y][x-self.x] = puyo
        puyo.setState(FIX)
class PuyoOperator():
    FIX_TIME = 10
    def __init__(self, field):
        self.field = field
    def makePuyo(self):
        """ぷよを生成"""
        # 回転ぷよは軸ぷよの上側に生成.
        self.x, self.y = self.field.getApparitionPosition()
        self.fix_time = 0
        self.rotation = UPPER
        self.sun = Puyo(self.x, self.y, random.randint(0,4), SUN)
        self.earth = Puyo(self.x, self.y-1, random.randint(0,4), EARTH)
    def update(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:  # キーを押したとき
                if event.key == K_RIGHT:
                    self.move(RIGHT)
                elif event.key == K_LEFT:
                    self.move(LEFT)
                elif event.key == K_DOWN:
                    self.move(DOWN)
                elif event.key == K_SPACE:
                    self.fixPuyo()
                elif event.key == K_c:
                    self.spin(RIGHT)
                elif event.key == K_x:
                    self.spin(LEFT)
        # if isMoveable(self.x, self.y+1):
        #     TODO 自由落下?
        # else:
        #     self.fix_time += 1
        if self.fix_time > self.FIX_TIME:
            self.fixPuyo()
    def move(self, direction):
        if direction == RIGHT:
            if self.isMoveable(self.x+1, self.y):
                self.x += 1
                self.sun.addPosition(1, 0)
                self.earth.addPosition(1, 0)
        elif direction == LEFT:
            if self.isMoveable(self.x-1, self.y):
                self.x -= 1
                self.sun.addPosition(-1, 0)
                self.earth.addPosition(-1, 0)
        elif direction == DOWN:
            if self.isMoveable(self.x, self.y+1):
                self.y += 1
                self.sun.addPosition(0, 1)
                self.earth.addPosition(0, 1)
            else:
                self.fix_time += self.FIX_TIME
    def spin(self, direction):
        moments = [[0, -1], [1, 0], [0, 1], [-1, 0]]
        next_rotation = self.rotation
        if direction == RIGHT:
            if self.rotation == 3:
                next_rotation = 0
            else:
                next_rotation = self.rotation + 1
        elif direction == LEFT:
            if self.rotation == 0:
                next_rotation = 3
            else:
                next_rotation = self.rotation - 1
        else:
            return
        if self.isMoveable(self.x+moments[next_rotation][0], self.y+moments[next_rotation][1]):
            self.earth.setPosition(self.x+moments[next_rotation][0], self.y+moments[next_rotation][1])
            self.rotation = next_rotation
    def isMoveable(self, x, y):
        if self.field.getElement(x, y) == 0:
            return True
        return False
    def fixPuyo(self):
        self.field.addPuyo(self.sun)
        self.field.addPuyo(self.earth)
        # TODO 本来なら違うが、今は位置が確定したら次のぷよを作る.
        self.makePuyo()
class Puyo(pygame.sprite.Sprite):
    def __init__(self, x, y, color, state):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.state = state
        self.image = self.images[color]
        self.rect = self.image.get_rect()
        self.rect.left = x * CELL_SIZE
        self.rect.top = y * CELL_SIZE
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    def addPosition(self, x, y):
        self.rect.left += x * CELL_SIZE
        self.rect.top += y * CELL_SIZE
    def setPosition(self, x, y):
        self.rect.left = x * CELL_SIZE
        self.rect.top = y * CELL_SIZE
    def getPosition(self):
        return (self.rect.left // CELL_SIZE), (self.rect.top // CELL_SIZE)
    def setState(self, state):
        self.state = state
if __name__ == "__main__":
    Puyopuyo()
