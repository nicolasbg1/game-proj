
import pygame
import random
from settings import *
from sprites import Player, Enemy, Explosion, PowerUp, Background
from assets import carregar_assets, imagens, sons
from screens import tela_inicial, tela_game_over, mostrar_texto
from utils import carregar_highscore, salvar_highscore

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption(NOME_JOGO)
        self.relogio = pygame.time.Clock()
        self.rodando = True
        self.recorde = carregar_highscore()

    def novo_jogo(self):
        self.todos_sprites = pygame.sprite.Group()
        self.inimigos = pygame.sprite.Group()
        self.balas = pygame.sprite.Group()
        self.inimigos_balas = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        bg_far_img = imagens.get('background_far')
        bg_near_img = imagens.get('background_near')
        if bg_far_img:
            self.todos_sprites.add(Background(bg_far_img, 1))
            self.todos_sprites.add(Background(bg_far_img, 1, y_offset=-ALTURA_TELA))
        if bg_near_img:
            self.todos_sprites.add(Background(bg_near_img, 2))
            self.todos_sprites.add(Background(bg_near_img, 2, y_offset=-ALTURA_TELA))

        self.player = Player(self.todos_sprites, self.balas)
        self.todos_sprites.add(self.player)
        for _ in range(8):
            self.spawn_enemy()

        self.pontuacao = 0
        pygame.mixer.music.play(loops=-1)
        self.run()

    def spawn_enemy(self, dificuldade=1.0):
        inimigo = Enemy(self.todos_sprites, self.inimigos_balas, dificuldade)
        self.todos_sprites.add(inimigo)
        self.inimigos.add(inimigo)

    def run(self):
        self.jogando = True
        while self.jogando:
            self.relogio.tick(FPS)
            self.eventos()
            self.update()
            self.draw()

    def eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.jogando:
                    self.jogando = False
                self.rodando = False

        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_SPACE]:
            self.player.shoot()

    def update(self):
        self.todos_sprites.update()
        dificuldade = 1.0 + (self.pontuacao / 1000.0)

        colisoes_balas_inimigos = pygame.sprite.groupcollide(self.balas, self.inimigos, True, True)
        for inimigo_atingido in colisoes_balas_inimigos:
            self.pontuacao += 10
            sons['explosion'].play()
            self.todos_sprites.add(Explosion(inimigo_atingido.rect.center, 70))

            if random.random() < CHANCE_POWERUP:
                powerup = PowerUp(inimigo_atingido.rect.center)
                self.todos_sprites.add(powerup)
                self.powerups.add(powerup)

            self.spawn_enemy(dificuldade)

        if pygame.sprite.spritecollide(self.player, self.inimigos_balas, True):
            self.player.take_damage(DANO_TIRO_INIMIGO)

        colisoes_jogador_inimigos = pygame.sprite.spritecollide(self.player, self.inimigos, True)
        if colisoes_jogador_inimigos:
            self.player.take_damage(DANO_COLISAO_INIMIGO)
            for inimigo in colisoes_jogador_inimigos:
                self.todos_sprites.add(Explosion(inimigo.rect.center, 70))
                self.spawn_enemy(dificuldade)

        if pygame.sprite.spritecollide(self.player, self.powerups, True):
            self.player.ativar_powerup()

        if self.player.health <= 0 and self.player.alive():
            sons['game_over'].play()
            self.todos_sprites.add(Explosion(self.player.rect.center, 90))
            self.player.kill()

        if not self.player.alive() and not any(isinstance(s, Explosion) for s in self.todos_sprites):
            self.jogando = False

    def draw(self):
        self.tela.fill(PRETO)
        self.todos_sprites.draw(self.tela)

        mostrar_texto(self.tela, f"Pontos: {self.pontuacao}", 22, BRANCO, LARGURA_TELA / 2, 10)
        mostrar_texto(self.tela, f"Vida: {max(0, self.player.health)}", 22, BRANCO, 80, 10, align="midtop")
        mostrar_texto(self.tela, f"Recorde: {self.recorde}", 18, BRANCO, LARGURA_TELA - 80, 10, align="midtop")

        pygame.display.flip()

    def mostrar_tela_inicial(self):
        bg_img = pygame.transform.scale(imagens.get('background_near'), (LARGURA_TELA, ALTURA_TELA))
        tela_inicial(self.tela, self.relogio, self.recorde, bg_img)

    def mostrar_tela_game_over(self):
        pygame.mixer.music.stop()
        self.recorde = salvar_highscore(self.pontuacao, self.recorde)
        tela_game_over(self.tela, self.relogio, self.pontuacao, self.recorde)


if __name__ == '__main__':
    g = Game()
    carregar_assets()

    while g.rodando:
        g.mostrar_tela_inicial()
        g.novo_jogo()
        if g.rodando:
            g.mostrar_tela_game_over()

    pygame.quit()
