import pygame
import random
import os

LARGURA_TELA = 900
ALTURA_TELA = 640
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)
AZUL_JOGADOR = (0, 0, 255)
VERMELHO_INIMIGO = (255, 0, 0)
AMARELO_TIRO = (255, 255, 0)
EXPLOSAO_FRAMES = []
DANO_TIRO_INIMIGO = 10
DANO_COLISAO_INIMIGO = 25
FREQUENCIA_TIRO_INIMIGO = 1500
DURACAO_INVENCIBILIDADE_JOGADOR = 1000

pygame.init()
pygame.mixer.init()
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Space Shooter - Corrigido")
relogio = pygame.time.Clock()

assets_folder = os.path.join(os.path.dirname(__file__), 'assets')

def carregar_imagem(nome_arquivo, tamanho=None, cor_chave=None):
    caminho_completo = os.path.join(assets_folder, nome_arquivo)
    try:
        imagem = pygame.image.load(caminho_completo)
        if imagem.get_alpha() is not None or imagem.get_colorkey() is not None:
            imagem = imagem.convert_alpha()
        else:
            imagem = imagem.convert()
        if tamanho:
            imagem = pygame.transform.scale(imagem, tamanho)
        if cor_chave:
            imagem.set_colorkey(cor_chave)
        return imagem
    except (pygame.error, FileNotFoundError):
        print(f"AVISO: Nao foi possivel carregar a imagem '{nome_arquivo}'.")
        return None

def carregar_som(nome_arquivo):
    caminho_completo = os.path.join(assets_folder, nome_arquivo)
    try:
        return pygame.mixer.Sound(caminho_completo)
    except (pygame.error, FileNotFoundError):
        print(f"AVISO: Nao foi possivel carregar o som '{nome_arquivo}'.")
        return None

player_img = carregar_imagem("Player2.png")
enemy_img = carregar_imagem("Enemy1.png", cor_chave=PRETO)
missile_img = carregar_imagem("Player2Shot.png", cor_chave=PRETO)
enemy_missile_img = carregar_imagem("Enemy1Shot.png", cor_chave=PRETO)
background_far_img = carregar_imagem("background_far.png", (LARGURA_TELA, ALTURA_TELA * 2))
background_near_img = carregar_imagem("background_near.png", (LARGURA_TELA, ALTURA_TELA * 2))

explosion_sheet = carregar_imagem("explosion.png", (384, 128), PRETO)

if explosion_sheet:
    for i in range(12):
        frame = explosion_sheet.subsurface(pygame.Rect(i * 32, 0, 32, 32))
        EXPLOSAO_FRAMES.append(frame)

shoot_sound = carregar_som("alienshoot1.wav")
explosion_sound = carregar_som("explosion.wav")
game_over_sound = carregar_som("gameover.wav")
hit_sound = carregar_som("hit.wav")
enemy_shoot_sound = carregar_som("alienshoot3.wav")

try:
    pygame.mixer.music.load(os.path.join(assets_folder, 'spaceship.wav'))
    pygame.mixer.music.set_volume(0.4)
except pygame.error:
    print("AVISO: Nao foi possivel carregar a musica de fundo.")

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        if player_img:
            self.image = player_img
        else:
            self.image = pygame.Surface([60, 50], pygame.SRCALPHA)
            self.image.fill(AZUL_JOGADOR)
        self.rect = self.image.get_rect(centerx=LARGURA_TELA / 2, bottom=ALTURA_TELA - 20)
        self.velocidade_x = 0
        self.ultimo_tiro = pygame.time.get_ticks()
        self.frequencia_tiro = 250
        self.health = 100
        self.ultimo_dano = pygame.time.get_ticks()
        self.invencivel = False

    def update(self):
        self.velocidade_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT] or keystate[pygame.K_a]:
            self.velocidade_x = -8
        if keystate[pygame.K_RIGHT] or keystate[pygame.K_d]:
            self.velocidade_x = 8
        self.rect.x += self.velocidade_x
        self.rect.clamp_ip(tela.get_rect())

        if self.invencivel:
            self.image.set_alpha(128 if pygame.time.get_ticks() % 200 < 100 else 255)
            if pygame.time.get_ticks() - self.ultimo_dano > DURACAO_INVENCIBILIDADE_JOGADOR:
                self.invencivel = False
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)

    def shoot(self, todos_sprites, balas):
        agora = pygame.time.get_ticks()
        if agora - self.ultimo_tiro > self.frequencia_tiro:
            self.ultimo_tiro = agora
            missil_esq = Bullet(self.rect.left + 15, self.rect.top)
            missil_dir = Bullet(self.rect.right - 15, self.rect.top)
            balas.add(missil_esq, missil_dir)
            todos_sprites.add(missil_esq, missil_dir)  # <--- CORREÇÃO APLICADA
            if shoot_sound: shoot_sound.play()

    def take_damage(self, dano):
        if not self.invencivel:
            self.health -= dano
            self.invencivel = True
            self.ultimo_dano = pygame.time.get_ticks()
            if hit_sound: hit_sound.play()

    def reset(self):
        self.health = 100
        self.rect.centerx = LARGURA_TELA / 2
        self.rect.bottom = ALTURA_TELA - 20
        self.invencivel = False
        self.image.set_alpha(255)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, todos_sprites, inimigos_balas):
        super().__init__()
        if enemy_img:
            self.image = enemy_img.copy()
        else:
            self.image = pygame.Surface([50, 40], pygame.SRCALPHA); self.image.fill(VERMELHO_INIMIGO)
        self.rect = self.image.get_rect()
        self.todos_sprites = todos_sprites
        self.inimigos_balas = inimigos_balas
        self.reset()

    def update(self):
        self.rect.y += self.velocidade_y
        self.angulo += self.frequencia
        offset_x = self.amplitude * pygame.math.Vector2(1, 0).rotate_rad(self.angulo).x
        self.rect.centerx = self.pos_x_original + offset_x
        if pygame.time.get_ticks() - self.ultimo_tiro > self.frequencia_tiro:
            self.shoot()
            self.ultimo_tiro = pygame.time.get_ticks()
        if self.rect.top > ALTURA_TELA + 10: self.reset()

    def reset(self):
        self.pos_x_original = random.randrange(50, LARGURA_TELA - 50)
        self.rect.centerx = self.pos_x_original
        self.rect.y = random.randrange(-200, -100)
        self.velocidade_y = random.randrange(1, 4)
        self.angulo = random.uniform(0, 2 * 3.14159)
        self.amplitude = random.randrange(30, 80)
        self.frequencia = random.uniform(0.02, 0.05)
        self.ultimo_tiro = pygame.time.get_ticks()
        self.frequencia_tiro = FREQUENCIA_TIRO_INIMIGO + random.randrange(-500, 500)

    def shoot(self):
        new_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        self.todos_sprites.add(new_bullet)
        self.inimigos_balas.add(new_bullet)
        if enemy_shoot_sound: enemy_shoot_sound.play()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        if missile_img:
            self.image = missile_img
        else:
            self.image = pygame.Surface([10, 20]); self.image.fill(AMARELO_TIRO)
        self.rect = self.image.get_rect(centerx=x, bottom=y)
        self.velocidade_y = -10

    def update(self):
        self.rect.y += self.velocidade_y
        if self.rect.bottom < 0: self.kill()


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        if enemy_missile_img:
            self.image = enemy_missile_img
        else:
            self.image = pygame.Surface([10, 20]); self.image.fill(VERMELHO)
        self.rect = self.image.get_rect(centerx=x, top=y)
        self.velocidade_y = 5

    def update(self):
        self.rect.y += self.velocidade_y
        if self.rect.top > ALTURA_TELA: self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        super().__init__()
        self.size = size
        self.frame = 0
        if EXPLOSAO_FRAMES:
            self.image = pygame.transform.scale(EXPLOSAO_FRAMES[self.frame], (size, size))
        else:
            self.image = pygame.Surface([size, size]);
            self.image.fill(VERMELHO)
        self.rect = self.image.get_rect(center=center)
        self.ultimo_update = pygame.time.get_ticks()
        self.frequencia_animacao = 50

    def update(self):
        agora = pygame.time.get_ticks()
        if agora - self.ultimo_update > self.frequencia_animacao:
            self.ultimo_update = agora
            self.frame += 1
            if self.frame < len(EXPLOSAO_FRAMES):
                center = self.rect.center
                self.image = pygame.transform.scale(EXPLOSAO_FRAMES[self.frame], (self.size, self.size))
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


def mostrar_texto(texto, tamanho, cor, x, y):
    fonte = pygame.font.Font(pygame.font.match_font('arial'), tamanho)
    superficie_texto = fonte.render(texto, True, cor)
    rect_texto = superficie_texto.get_rect(midtop=(x, y))
    tela.blit(superficie_texto, rect_texto)


def tela_inicial():
    tela.fill(PRETO)
    mostrar_texto("SPACE SHOOTER", 54, BRANCO, LARGURA_TELA / 2, ALTURA_TELA / 4)
    mostrar_texto("Setas/A/D para mover, Espaco para atirar", 22, BRANCO, LARGURA_TELA / 2, ALTURA_TELA / 2)
    mostrar_texto("Pressione qualquer tecla para começar", 18, BRANCO, LARGURA_TELA / 2, ALTURA_TELA * 3 / 4)
    pygame.display.flip()
    esperando = True
    while esperando:
        relogio.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYUP: esperando = False


def tela_game_over(pontuacao):
    tela.fill(PRETO)
    mostrar_texto("GAME OVER", 64, VERMELHO, LARGURA_TELA / 2, ALTURA_TELA / 4)
    mostrar_texto(f"Pontuação: {pontuacao}", 30, BRANCO, LARGURA_TELA / 2, ALTURA_TELA / 2)
    mostrar_texto("Pressione qualquer tecla para jogar novamente", 18, BRANCO, LARGURA_TELA / 2, ALTURA_TELA * 3 / 4)
    pygame.display.flip()
    esperando = True
    while esperando:
        relogio.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYUP: esperando = False


jogo_rodando = True
game_over = True
pontuacao = 0

while jogo_rodando:
    if game_over:
        if pontuacao == 0:
            tela_inicial()
        else:
            tela_game_over(pontuacao)

        game_over = False

        todos_sprites = pygame.sprite.Group()
        inimigos = pygame.sprite.Group()
        balas = pygame.sprite.Group()
        inimigos_balas = pygame.sprite.Group()

        background_far_1 = Background(background_far_img, 1)
        background_far_2 = Background(background_far_img, 1, y_offset=-ALTURA_TELA)
        background_near_1 = Background(background_near_img, 2)
        background_near_2 = Background(background_near_img, 2, y_offset=-ALTURA_TELA)
        todos_sprites.add(background_far_1, background_far_2, background_near_1, background_near_2)

        player = Player()
        todos_sprites.add(player)

        for i in range(8):
            inimigo = Enemy(todos_sprites, inimigos_balas)
            todos_sprites.add(inimigo)
            inimigos.add(inimigo)

        pontuacao = 0
        try:
            pygame.mixer.music.play(loops=-1)
        except pygame.error:
            pass

    relogio.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            jogo_rodando = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot(todos_sprites, balas)

    todos_sprites.update()

    colisoes_balas_inimigos = pygame.sprite.groupcollide(balas, inimigos, True, True)
    for inimigo_atingido in colisoes_balas_inimigos:
        pontuacao += 10
        if explosion_sound: explosion_sound.play()
        explosao = Explosion(inimigo_atingido.rect.center, 70)  # <--- CORREÇÃO APLICADA
        todos_sprites.add(explosao)
        novo_inimigo = Enemy(todos_sprites, inimigos_balas)
        todos_sprites.add(novo_inimigo)
        inimigos.add(novo_inimigo)

    colisoes_jogador_tiros = pygame.sprite.spritecollide(player, inimigos_balas, True)
    if colisoes_jogador_tiros:
        player.take_damage(DANO_TIRO_INIMIGO)

    colisoes_jogador_inimigos = pygame.sprite.spritecollide(player, inimigos, True)
    if colisoes_jogador_inimigos:
        player.take_damage(DANO_COLISAO_INIMIGO)
        for inimigo in colisoes_jogador_inimigos:
            explosao_inimigo = Explosion(inimigo.rect.center, 70)  # <--- CORREÇÃO APLICADA
            todos_sprites.add(explosao_inimigo)
            novo_inimigo = Enemy(todos_sprites, inimigos_balas)
            todos_sprites.add(novo_inimigo)
            inimigos.add(novo_inimigo)

    if player.health <= 0 and player.alive():
        if game_over_sound:
            game_over_sound.play()
        explosao_player = Explosion(player.rect.center, 90)  # <--- CORREÇÃO APLICADA
        todos_sprites.add(explosao_player)
        player.kill()

    if not player.alive():
        pygame.mixer.music.stop()
        game_over = True

    tela.fill(PRETO)
    todos_sprites.draw(tela)
    mostrar_texto(f"Pontos: {pontuacao}", 22, BRANCO, LARGURA_TELA / 2, 10)
    mostrar_texto(f"Vida: {player.health}", 22, BRANCO, 80, 10)
    pygame.display.flip()

pygame.quit()