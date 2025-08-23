
import pygame
import random
from settings import *
from assets import imagens, sons, explosoes

class Player(pygame.sprite.Sprite):
    def __init__(self, todos_sprites, balas):
        super().__init__()
        self.todos_sprites = todos_sprites
        self.balas = balas
        self.original_image = imagens.get('player', pygame.Surface([60, 50], pygame.SRCALPHA))
        if not imagens.get('player'): self.original_image.fill(AZUL_JOGADOR)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(centerx=LARGURA_TELA / 2, bottom=ALTURA_TELA - 20)
        self.velocidade_x = 0
        self.frequencia_tiro_base = 250
        self.frequencia_tiro = self.frequencia_tiro_base
        self.ultimo_tiro = pygame.time.get_ticks()
        self.health = 100
        self.ultimo_dano = 0
        self.invencivel = False
        self.powerup_ativo_timer = 0

    def update(self):
        self.velocidade_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT] or keystate[pygame.K_a]:
            self.velocidade_x = -8
        if keystate[pygame.K_RIGHT] or keystate[pygame.K_d]:
            self.velocidade_x = 8
        self.rect.x += self.velocidade_x
        self.rect.clamp_ip(pygame.display.get_surface().get_rect())

        agora = pygame.time.get_ticks()
        if self.invencivel and agora - self.ultimo_dano > DURACAO_INVENCIBILIDADE_JOGADOR:
            self.invencivel = False

        if self.powerup_ativo_timer > 0:
            if agora - self.powerup_ativo_timer > DURACAO_POWERUP:
                self.frequencia_tiro = self.frequencia_tiro_base
                self.powerup_ativo_timer = 0
            if pygame.time.get_ticks() % 200 < 100:
                self.image.fill(AMARELO_POWERUP, special_flags=pygame.BLEND_RGB_ADD)
            else:
                self.image = self.original_image.copy()
        else:
            if self.invencivel:
                self.image.set_alpha(128 if pygame.time.get_ticks() % 200 < 100 else 255)
            else:
                self.image = self.original_image.copy()
                self.image.set_alpha(255)

    def shoot(self):
        agora = pygame.time.get_ticks()
        if agora - self.ultimo_tiro > self.frequencia_tiro:
            self.ultimo_tiro = agora
            missil_esq = Bullet(self.rect.left + 15, self.rect.top)
            missil_dir = Bullet(self.rect.right - 15, self.rect.top)
            self.balas.add(missil_esq, missil_dir)
            self.todos_sprites.add(missil_esq, missil_dir)
            sons['shoot'].play()

    def take_damage(self, dano):
        if not self.invencivel:
            self.health -= dano
            self.invencivel = True
            self.ultimo_dano = pygame.time.get_ticks()
            sons['hit'].play()

    def ativar_powerup(self):
        sons['powerup'].play()
        self.frequencia_tiro = self.frequencia_tiro_base / 2
        self.powerup_ativo_timer = pygame.time.get_ticks()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, todos_sprites, inimigos_balas, dificuldade=1.0):
        super().__init__()
        self.image_original = imagens.get('enemy', pygame.Surface([50, 40], pygame.SRCALPHA))
        if not imagens.get('enemy'): self.image_original.fill(VERMELHO_INIMIGO)
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
        self.todos_sprites = todos_sprites
        self.inimigos_balas = inimigos_balas
        self.reset(dificuldade)

    def update(self):
        self.rect.y += self.velocidade_y
        offset_x = self.amplitude * pygame.math.Vector2(1, 0).rotate_rad(self.angulo).x
        self.rect.centerx = self.pos_x_original + offset_x
        self.angulo += self.frequencia
        if pygame.time.get_ticks() - self.ultimo_tiro > self.frequencia_tiro:
            self.shoot()
            self.ultimo_tiro = pygame.time.get_ticks()
        if self.rect.top > ALTURA_TELA + 10: self.reset()

    def reset(self, dificuldade=1.0):
        self.pos_x_original = random.randrange(50, LARGURA_TELA - 50)
        self.rect.centerx = self.pos_x_original
        self.rect.y = random.randrange(-200, -100)
        self.velocidade_y = random.randrange(1, 4) * dificuldade
        self.angulo = random.uniform(0, 2 * 3.14159)
        self.amplitude = random.randrange(30, 80)
        self.frequencia = random.uniform(0.02, 0.05)
        self.ultimo_tiro = pygame.time.get_ticks()
        self.frequencia_tiro = max(400, FREQUENCIA_TIRO_INIMIGO_BASE / dificuldade) + random.randrange(-200, 200)

    def shoot(self):
        new_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        self.todos_sprites.add(new_bullet)
        self.inimigos_balas.add(new_bullet)
        sons['enemy_shoot'].play()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = imagens.get('missile', pygame.Surface([10, 20]))
        if not imagens.get('missile'): self.image.fill(AMARELO_TIRO)
        self.rect = self.image.get_rect(centerx=x, bottom=y)
        self.velocidade_y = -10

    def update(self):
        self.rect.y += self.velocidade_y
        if self.rect.bottom < 0: self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = imagens.get('enemy_missile', pygame.Surface([10, 20]))
        if not imagens.get('enemy_missile'): self.image.fill(VERMELHO)
        self.rect = self.image.get_rect(centerx=x, top=y)
        self.velocidade_y = 5

    def update(self):
        self.rect.y += self.velocidade_y
        if self.rect.top > ALTURA_TELA: self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
        pygame.draw.circle(self.image, AMARELO_POWERUP, (12, 12), 12)
        self.rect = self.image.get_rect(center=center)
        self.velocidade_y = 3

    def update(self):
        self.rect.y += self.velocidade_y
        if self.rect.top > ALTURA_TELA: self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        super().__init__()
        self.size = size
        self.frame = 0
        self.image = pygame.transform.scale(explosoes[self.frame], (size, size))
        self.rect = self.image.get_rect(center=center)
        self.ultimo_update = pygame.time.get_ticks()
        self.frequencia_animacao = 50

    def update(self):
        agora = pygame.time.get_ticks()
        if agora - self.ultimo_update > self.frequencia_animacao:
            self.ultimo_update = agora
            self.frame += 1
            if self.frame < len(explosoes):
                center = self.rect.center
                self.image = pygame.transform.scale(explosoes[self.frame], (self.size, self.size))
                self.rect = self.image.get_rect(center=center)
            else:
                self.kill()

class Background(pygame.sprite.Sprite):
    def __init__(self, image, velocidade, y_offset=0):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(y=y_offset)
        self.velocidade = velocidade

    def update(self):
        self.rect.y += self.velocidade
        if self.rect.top >= ALTURA_TELA: self.rect.y = -ALTURA_TELA
