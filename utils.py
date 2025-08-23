import os
from settings import ARQUIVO_HIGHSCORE

def carregar_highscore():

    if os.path.exists(ARQUIVO_HIGHSCORE):
        with open(ARQUIVO_HIGHSCORE, 'r') as f:
            try:
                return int(f.read())
            except (ValueError, TypeError):
                return 0
    return 0

def salvar_highscore(pontuacao, recorde_atual):

    if pontuacao > recorde_atual:
        with open(ARQUIVO_HIGHSCORE, 'w') as f:
            f.write(str(pontuacao))
        return pontuacao
    return recorde_atual
