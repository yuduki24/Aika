import pygame
from pygame.locals import *
from loader import load_image, split_image
import sys
import random

SCR_RECT = Rect(0, 0, 768, 608)
CELL_SIZE = 32
WINDOW_ROW = SCR_RECT.height // CELL_SIZE
WINDOW_COL = SCR_RECT.width // CELL_SIZE
FIELD_COL, FIELD_ROW = 8, 16
SUN, EARTH, FIX, OJAMA = 0, 1, 2, 3
UPPER, RIGHT, DOWN, LEFT = 0, 1, 2, 3
DELETE_LINK_COUNT = 4
MOMENTS = [[0, -1], [1, 0], [0, 1], [-1, 0]]

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
        self.updatePuyoPosition()
    def fall(self, y, x):
        """(x, y)にあるぷよを一番下に落とす"""
        n = 0
        while self.field[y+n+1][x] == 0:
            n += 1
        if n == 0:
            return
        self.field[y+n][x] = self.field[y][x]
        self.field[y][x] = 0
    def getPuyoApparitionPosition(self):
        """ぷよ出現位置を返す"""
        # xはfieldの中心、yは上から3番目の位置.
        return (self.x + FIELD_COL // 2 - 1), (self.y + 2)
    def getNextPuyoApparitionPosition(self):
        """ネクストぷよ出現位置を返す"""
        # xはPlayer1ならfieldの右側、Player2ならfieldの左側.
        # yは上から4番目の位置.
        return (self.x + FIELD_COL), (self.y + 4)
    def getNextNextPuyoApparitionPosition(self):
        """ネクネクぷよ出現位置を返す"""
        # xはPlayer1ならfieldの右側、Player2ならfieldの左側.
        # yは上から6番目の位置.
        return (self.x + FIELD_COL + 1), (self.y + 6)
    def getElement(self, x, y):
        return self.field[y-self.y][x-self.x]
    def addPuyo(self, puyo):
        x, y = puyo.getPosition()
        self.field[y-self.y][x-self.x] = puyo
        puyo.setState(FIX)
    def startChain(self):
        """連鎖を開始する"""
        self.allFall()
        while self.deletePuyoAll(DELETE_LINK_COUNT):
            self.allFall()
    def deletePuyoAll(self, targetLinkCount):
        """連結しているぷよがあれば消す
            引数で与えられた数以上の
            連結があるぷよが1つでもあれば削除する
            1か所でも削除すればTrueを返す"""
        result = False
        searchField = [x[:] for x in self.field]
        for i in range(FIELD_COL):
            for j in range(FIELD_ROW):
                #壁でも空でもない場合(=ぷよ).
                if not(searchField[j][i] == 0 or searchField[j][i] == -1):
                    count = self.getLinkingCount(searchField, j, i)
                    if targetLinkCount <= count:
                        self.deletePuyo(j, i)
                        result = True
        return result
    def getLinkingCount(self, field, j, i):
        """連結数を返す
            引数で与えられたところからつながる部分をカウントする"""
        nowLinkCount = 1
        color = field[j][i].getColor()
        #もう一度捜査しないように0を入れておく.
        field[j][i] = 0
        # 上下左右を捜査.
        for next_rotation in range(4):
            element = field[j+MOMENTS[next_rotation][0]][i+MOMENTS[next_rotation][1]]
            # 壁でも空でもない場合(=ぷよ).
            if not(element == 0 or element == -1):
                # 同じ色か?
                if element.getColor() == color:
                    nowLinkCount += self.getLinkingCount(field, j+MOMENTS[next_rotation][0], i+MOMENTS[next_rotation][1])
        return nowLinkCount
    def deletePuyo(self, j, i):
        color = self.field[j][i].getColor()
        puyo = self.field[j][i]
        puyo.kill()
        self.field[j][i] = 0
        # 上下左右を捜査.
        for next_rotation in range(4):
            element = self.field[j+MOMENTS[next_rotation][0]][i+MOMENTS[next_rotation][1]]
            # 壁でも空でもない場合(=ぷよ).
            if not(element == 0 or element == -1):
                # 同じ色か?
                if element.getColor() == color:
                    self.deletePuyo(j+MOMENTS[next_rotation][0], i+MOMENTS[next_rotation][1])
class PuyoOperator():
    FIX_TIME = 10
    def __init__(self, field):
        self.field = field
        x, y = self.field.getNextPuyoApparitionPosition()
        self.nextSun = Puyo(x, y, random.randint(0,3), SUN)
        self.nextEarth = Puyo(x, y-1, random.randint(0,3), EARTH)
        x, y = self.field.getNextNextPuyoApparitionPosition()
        self.nextNextSun = Puyo(x, y, random.randint(0,3), SUN)
        self.nextNextEarth = Puyo(x, y-1, random.randint(0,3), EARTH)
    def makePuyo(self):
        """ぷよを生成"""
        # 回転ぷよは軸ぷよの上側に生成.
        self.x, self.y = self.field.getPuyoApparitionPosition()
        self.fix_time = 0
        self.rotation = UPPER
        self.sun = Puyo(self.x, self.y, self.nextSun.getColor(), SUN)
        self.earth = Puyo(self.x, self.y-1, self.nextEarth.getColor(), EARTH)
        self.nextSun.setColor(self.nextNextSun.getColor())
        self.nextEarth.setColor(self.nextNextEarth.getColor())
        self.nextNextSun.setColor(random.randint(0,4))
        self.nextNextEarth.setColor(random.randint(0,4))
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
        if self.isMoveable(self.x+MOMENTS[next_rotation][0], self.y+MOMENTS[next_rotation][1]):
            self.earth.setPosition(self.x+MOMENTS[next_rotation][0], self.y+MOMENTS[next_rotation][1])
            self.rotation = next_rotation
    def isMoveable(self, x, y):
        if self.field.getElement(x, y) == 0:
            return True
        return False
    def fixPuyo(self):
        self.field.addPuyo(self.sun)
        self.field.addPuyo(self.earth)
        self.field.startChain()
        self.makePuyo()
class Puyo(pygame.sprite.Sprite):
    def __init__(self, x, y, color, state):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.state = state
        self.color = color
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
    def getColor(self):
        return self.color
    def setColor(self, color):
        self.color = color
        self.image = self.images[color]
if __name__ == "__main__":
    Puyopuyo()
