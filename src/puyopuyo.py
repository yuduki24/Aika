import pygame
from pygame.locals import *
import sys

SCR_RECT = Rect(0, 0, 768, 576)
CELL_SIZE = 32
WINDOW_ROW = SCR_RECT.height // CELL_SIZE
WINDOW_COL = SCR_RECT.width // CELL_SIZE
FIELD_COL, FIELD_ROW = 8, 15

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
        Field.screen = screen

        self.field = Field(1, 1)

    def update(self):
        """ゲーム状態の更新"""
        self.all.update()

    def draw(self, screen):
        """描画"""
        screen.fill((50, 50, 50))
        
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

    def update(self):
        pygame.draw.rect(self.screen, (50, 100, 255), Rect(self.x*CELL_SIZE, self.y*CELL_SIZE, FIELD_COL*CELL_SIZE, FIELD_ROW*CELL_SIZE))

if __name__ == "__main__":
    Puyopuyo()