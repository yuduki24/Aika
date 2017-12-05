import pygame
from pygame.locals import *

SCR_RECT = Rect(0, 0, 768, 576)
CELL_SIZE = 32
WINDOW_ROW = SCR_RECT.height // CELL_SIZE
WINDOW_COL = SCR_RECT.width // CELL_SIZE

class Puyopuyo:
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode(SCR_RECT.size)
        pygame.display.set_caption(u"Puyopuyo")

        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            self.draw(screen)
            pygame.display.update()
            self.key_handler()

    def draw(self, screen):
        """描画"""
        screen.fill((50, 50, 50))
        self.draw_grid(screen)

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
                pygame.draw.rect(screen, (150, 150, 150), Rect(x*CELL_SIZE,y*CELL_SIZE,CELL_SIZE,CELL_SIZE), 1)

if __name__ == "__main__":
    Puyopuyo()
