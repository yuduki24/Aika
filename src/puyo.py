import pygame
from pygame.locals import *
import sys

SCR_RECT = Rect(0, 0, 768, 576)
CELL_SIZE = 32
WINDOW_ROW = SCR_RECT.height // CELL_SIZE
WINDOW_COL = SCR_RECT.width // CELL_SIZE

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
    colm, row = 8, 15
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.x = x
        self.y = y
    def update(self):
        pygame.draw.rect(self.screen, (50, 100, 255), Rect(self.x*CELL_SIZE, self.y*CELL_SIZE, self.colm*CELL_SIZE, self.row*CELL_SIZE))

if __name__ == "__main__":
    Puyopuyo()