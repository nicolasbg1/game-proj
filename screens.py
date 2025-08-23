
import pygame
from settings import *

def mostrar_texto(tela, texto, tamanho, cor, x, y, align="midtop"):

    fonte = pygame.font.Font(pygame.font.match_font(FONTE_PADRAO), tamanho)
    superficie_texto = fonte.render(texto, True, cor)
    rect_texto = superficie_texto.get_rect()
    setattr(rect_texto, align, (x, y))
    tela.blit(superficie_texto, rect_texto)

def tela_inicial(tela, relogio, recorde, background_img):

    if background_img:
        tela.blit(background_img, (0, 0))
    else:
        tela.fill(PRETO)

    mostrar_texto(tela, NOME_JOGO, 54, BRANCO, LARGURA_TELA / 2, ALTURA_TELA / 4)
    mostrar_texto(tela, f"Recorde Atual: {recorde}", 24, AMARELO_POWERUP, LARGURA_TELA / 2, ALTURA_TELA / 2 - 40)
    mostrar_texto(tela, "Setas/A/D para mover, Segure Espaço para atirar", 22, BRANCO, LARGURA_TELA / 2, ALTURA_TELA / 2)
    mostrar_texto(tela, "Pressione qualquer tecla para começar", 18, BRANCO, LARGURA_TELA / 2, ALTURA_TELA * 3 / 4)

    pygame.display.flip()
    esperando = True
    while esperando:
        relogio.tick(FPS / 2)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYUP:
                esperando = False

def tela_game_over(tela, relogio, pontuacao, recorde):

    tela.fill(PRETO)
    mostrar_texto(tela, "GAME OVER", 64, VERMELHO, LARGURA_TELA / 2, ALTURA_TELA / 4)
    mostrar_texto(tela, f"Sua pontuação: {pontuacao}", 30, BRANCO, LARGURA_TELA / 2, ALTURA_TELA / 2 - 30)
    if pontuacao > recorde:
        mostrar_texto(tela, "NOVO RECORDE!", 28, AMARELO_POWERUP, LARGURA_TELA / 2, ALTURA_TELA / 2 + 15)
    else:
        mostrar_texto(tela, f"Recorde: {recorde}", 22, BRANCO, LARGURA_TELA / 2, ALTURA_TELA / 2 + 15)
    mostrar_texto(tela, "Pressione qualquer tecla para jogar novamente", 18, BRANCO, LARGURA_TELA / 2, ALTURA_TELA * 3 / 4)
    pygame.display.flip()
    esperando = True
    while esperando:
        relogio.tick(FPS / 2)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYUP:
                esperando = False
