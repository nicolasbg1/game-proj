
import pygame
import os
from settings import *

imagens = {}
sons = {}
explosoes = []

def carregar_assets():

    assets_folder = os.path.join(os.path.dirname(__file__), PASTA_ASSETS)

    imagens['player'] = carregar_imagem(assets_folder, "Player2.png")
    imagens['enemy'] = carregar_imagem(assets_folder, "Enemy1.png", cor_chave=PRETO)
    imagens['missile'] = carregar_imagem(assets_folder, "Player2Shot.png", cor_chave=PRETO)
    imagens['enemy_missile'] = carregar_imagem(assets_folder, "Enemy1Shot.png", cor_chave=PRETO)
    imagens['background_far'] = carregar_imagem(assets_folder, "background_far.png", (LARGURA_TELA, ALTURA_TELA * 2))
    imagens['background_near'] = carregar_imagem(assets_folder, "background_near.png", (LARGURA_TELA, ALTURA_TELA * 2))
    explosion_sheet = carregar_imagem(assets_folder, "explosion.png", (384, 128), PRETO)

    sons['shoot'] = carregar_som(assets_folder, "alienshoot1.wav")
    sons['explosion'] = carregar_som(assets_folder, "explosion.wav")
    sons['game_over'] = carregar_som(assets_folder, "gameover.wav")
    sons['hit'] = carregar_som(assets_folder, "hit.wav")
    sons['enemy_shoot'] = carregar_som(assets_folder, "alienshoot3.wav")
    sons['powerup'] = carregar_som(assets_folder, "invincible.wav")

    try:
        pygame.mixer.music.load(os.path.join(assets_folder, 'spaceship.wav'))
        pygame.mixer.music.set_volume(0.4)
    except pygame.error:
        print("AVISO: Nao foi possivel carregar a musica de fundo.")

    if explosion_sheet:
        for i in range(12):
            img = explosion_sheet.subsurface(pygame.Rect(i * 32, 0, 32, 32))
            explosoes.append(img)

def carregar_imagem(pasta, nome_arquivo, tamanho=None, cor_chave=None):
    caminho_completo = os.path.join(pasta, nome_arquivo)
    try:
        imagem = pygame.image.load(caminho_completo).convert_alpha()
        if tamanho:
            imagem = pygame.transform.scale(imagem, tamanho)
        if cor_chave:
            imagem.set_colorkey(cor_chave)
        return imagem
    except (pygame.error, FileNotFoundError):
        print(f"AVISO: Nao foi possivel carregar a imagem '{nome_arquivo}'.")
        if tamanho:
            return pygame.Surface(tamanho, pygame.SRCALPHA)
        return pygame.Surface((50, 50), pygame.SRCALPHA)

def carregar_som(pasta, nome_arquivo):
    caminho_completo = os.path.join(pasta, nome_arquivo)
    try:
        return pygame.mixer.Sound(caminho_completo)
    except (pygame.error, FileNotFoundError):
        print(f"AVISO: Nao foi possivel carregar o som '{nome_arquivo}'.")
        class DummySound:
            def play(self): pass
        return DummySound()
