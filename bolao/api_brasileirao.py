import requests
import os
import json

def get_api_data(rodada):
    '''
    Args:
        Recebe como argumento o número da Rodada do campeonato Brasileiro

    Return:
        Retorna o resultado dos jogos da rodada
    '''
    uri = f'https://api.football-data.org/v4/competitions/BSA/matches?matchday={rodada}'
    headers = { 'X-Auth-Token': os.getenv("TOKEN_API_BRASILEIRAO") }

    response = requests.get(uri, headers=headers)
    if response.status_code == 200:
        dados = response.json()
        return dados
    else:
        print("Não foi possivel conectar a API")
