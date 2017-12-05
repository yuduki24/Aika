import pygame
from pygame.locals import *
SCR_RECT = Rect(0, 0, 768, 576)

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
        screen.fill((100, 10, 10))

    def key_handler(self):
        """キーハンドラー"""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

if __name__ == "__main__":
    Puyopuyo()
