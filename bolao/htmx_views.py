import json
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import *
from .utils import remover_repetidos

def forma_bolao(request):
    forma_normal = '''
        <hr>
        <p><b>Forma Normal:</b> O usuário terá que preencher as rodadas(10) de uma vez com seus palpites antes da primeira rodada começar.
        As premiações serão pagas ao final de todas as rodadas(10)</p>
        <hr>
        '''

    forma_por_rodada = '''
        <hr>
        <p><b>Forma Por Rodada:</b> O usuário terá que preencher a rodada atual com seus palpites.
        As premiações serão pagas ao final da rodada atual.</p>
        <hr>
        '''
    mensagem = request.GET.get('tipo_aposta')
    if mensagem == "normal":
        return HttpResponse(forma_normal)
    else:
        return HttpResponse(forma_por_rodada)


def detalhes_usuario(request, usuario_id):
    usuarios = Usuario.objects.get(usuario=request.user)
    adversarios = Usuario.objects.get(id=usuario_id)
    palpites_usuario = Palpite.objects.filter(usuario=usuarios.usuario)
    bloquear = BloquearPartida.objects.get(id=1)
    rodadas_list = []
    total_pontos_usuario = []
    total_pontos_adversario = []
    for usuario in palpites_usuario:
        rodadas_list.append(usuario.rodada_atual)
    rodadas = remover_repetidos(rodadas_list)

    for rodada in rodadas:
        palpites = Palpite.objects.filter(usuario=usuario.usuario,rodada_atual=rodada)
        palpites_adversario = Palpite.objects.filter(usuario=adversarios.usuario,rodada_atual=rodada)

        pontos_usuario = []
        pontos_adversario = []
        total_vitoria_rodada = 0
        total_placar_exato = 0
        total_vitoria_rodada_adversario = 0
        total_placar_exato_adversario = 0

        for palpite in palpites:
            total_vitoria_rodada += palpite.vitorias
            total_placar_exato += palpite.placar_exato
            pontos_rodadas = total_vitoria_rodada + total_placar_exato
            pontos_usuario.append(pontos_rodadas)
        total_pontos_usuario.append(pontos_usuario)

        for palpite in palpites_adversario:
            total_vitoria_rodada_adversario += palpite.vitorias
            total_placar_exato_adversario += palpite.placar_exato
            pontos_rodadas = total_vitoria_rodada_adversario + total_placar_exato_adversario
            pontos_adversario.append(pontos_rodadas)
        total_pontos_adversario.append(pontos_adversario)
    resultado_pontos_usuario = [ sublista[-1] for sublista in total_pontos_usuario]
    resultado_pontos_adversario = [ sublista[-1] for sublista in total_pontos_adversario]

    dados_comparacao = {
        "rodadas":rodadas[-5:],
        "pontos_usuario":resultado_pontos_usuario[-5:],
        "pontos_adversario":resultado_pontos_adversario[-5:]
    }

    dados_json = json.dumps(dados_comparacao)


    context = {"usuarios":usuarios, "adversarios":adversarios,"dados_json": dados_json, "bloquear": bloquear}
    return render(request, 'htmx/detalhes_usuario.html', context)
