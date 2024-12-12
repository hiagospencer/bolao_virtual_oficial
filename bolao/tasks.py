from celery import shared_task
from .models import *
from .api_brasileirao import *
import time
import pandas as pd


@shared_task
def criar_rodadas_campeonato_tasks():

  contador = 1
  while contador <= 38:
    time.sleep(2)
    data = get_api_data(contador)
    time_casa = []
    img_casa = []
    time_visitante = []
    img_visitante = []
    rodada = []

    for jogo in data["matches"]:
      time_casa.append(jogo['homeTeam']['shortName'])
      img_casa.append(jogo['homeTeam']['crest'])
      time_visitante.append(jogo['awayTeam']['shortName'])
      img_visitante.append(jogo['awayTeam']['crest'])
      rodada.append(jogo['matchday'])

    resultado_tabela = {
      "time_casa": time_casa,
      "img_casa": img_casa,
      "img_visitante": img_visitante,
      "time_visitante": time_visitante,
      "rodada": rodada
      }

    df_tabela = pd.DataFrame(resultado_tabela)
    for _, row in df_tabela.iterrows():
      jogos_rodada_criado  = Rodada.objects.create(
        time_casa=row['time_casa'],
        imagem_casa=row['img_casa'],
        time_visitante=row['time_visitante'],
        imagem_fora=row['img_visitante'],
        rodada_atual= row['rodada'],
          )
    print(f'Rodada {contador} criada!')
    contador += 1  # Incrementa o contador em 1 a cada iteração
    time.sleep(5)

@shared_task
def calcular_pontuacao_usuario_tasks(rodada_atualizada):
  todos_usuarios = Usuario.objects.all()
  try:
    for usuario in todos_usuarios:
      rodadas = Palpite.objects.filter(finalizado=False, usuario=usuario.usuario, rodada_atual=rodada_atualizada)
      pontuacao_usuario = Classificacao.objects.get(usuario__usuario=usuario.usuario)
      for rodada in rodadas:
        try:
          resultado_original = RodadaOriginal.objects.get(rodada_atual=rodada.rodada_atual, time_casa=rodada.time_casa,time_visitante=rodada.time_visitante)

          if rodada.vencedor == "empate" and resultado_original.vencedor == 'empate':
            pontuacao_usuario.empates += 1
            pontuacao_usuario.save()

          # Verifica se os placares coincidem
          if (rodada.vencedor == resultado_original.vencedor):
            pontuacao_usuario.pontos += 2
            pontuacao_usuario.vitorias += 1
            rodada.vitorias = 2
            rodada.tipo_class = "sucesso"
            rodada.finalizado = True
            pontuacao_usuario.save()

          else:
            rodada.tipo_class = "erro"
            rodada.finalizado = True

          # verifica os placares exatos
          if (rodada.placar_casa == resultado_original.placar_casa and
              rodada.placar_visitante == resultado_original.placar_visitante):
            pontuacao_usuario.pontos += 3
            pontuacao_usuario.placar_exato += 1
            rodada.placar_exato = 3
            rodada.tipo_class = "placar_exato"
            rodada.finalizado = True
            pontuacao_usuario.save()

          else:
            print("Resultados não exatos")  # Atribui 0 se os resultados não forem iguais
            rodada.finalizado = True

          # Verificando quais os jogos que não foram realizados
          if resultado_original.placar_casa == 9999 and resultado_original.placar_visitante == 9999:
            rodada.finalizado = False
            rodada.tipo_class = "none"
            rodada.save()
            print(f'Jogo para ser realizado: {rodada.time_casa} x {rodada.time_visitante}')

          rodada.save()
          pontuacao_usuario.save()
        except :
          continue
    classificacao = Classificacao.objects.filter(usuario__pagamento=True).order_by('-pontos', '-placar_exato', '-vitorias', '-empates')
    for index, item in enumerate(classificacao, start=1):
      # Salva a posição anterior
      item.posicao_anterior = item.posicao_atual
      # Atualiza a posição atual
      item.posicao_atual = index
      # Calcula a variação de posição (subiu ou desceu)
      if item.posicao_anterior is not None:
        item.posicao_variacao = item.posicao_anterior - item.posicao_atual
      else:
        item.posicao_variacao = 0  # Nenhuma variação se não há posição anterior
      item.save()
  except:
    print('tabela pontuação não encontrada')

  print("Classificação atualizada")
