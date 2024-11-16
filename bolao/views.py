import threading
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
import pandas as pd

from .models import *
from .utils import *
from .api_mercadopago import criar_pagamento


def homepage(request):
    if request.user.is_authenticated:
        tipo_aposta_usuario = Usuario.objects.get(usuario=request.user)
        #TODO Retirar a tabela Pontuacacao e colocar a Classificacao
        usuarios = Classificacao.objects.filter(usuario__pagamento=True, usuario__tipo_aposta=tipo_aposta_usuario.tipo_aposta).order_by('-pontos', '-placar_exato', '-vitorias', '-empates')
        # Itera sobre a classificação e atribui as posições

        context = {'usuarios':usuarios}
        return render(request, 'index.html',context)
    else:
        usuarios = Classificacao.objects.filter(usuario__pagamento=True, usuario__tipo_aposta="normal").order_by('-pontos', '-placar_exato', '-vitorias', '-empates')

        context = {'usuarios':usuarios}
        return render(request, 'index.html',context)


def palpites(request):

    if request.user.is_authenticated:
        user = request.user
        time_casa = []
        time_visitante = []
        rodada_dict = []
        placar_casa = []
        placar_visitante = []
        img_casa = []
        img_visitante = []
        verificacao_partida, criado = Verificacao.objects.get_or_create(user=user)
        rodadas = Rodada.objects.filter(rodada_atual=verificacao_partida.partida_atual )
        # calcular_pontuacao(user)

        if verificacao_partida.partida_atual == verificacao_partida.partida_final:
            verificacao_partida.verificado = True
            verificacao_partida.save()

        # adicionando os times casa e time visitantes dentros das lista para depois salvar no banco de dados
        for rodada in rodadas:
            time_casa.append(rodada.time_casa)
            time_visitante.append(rodada.time_visitante)
            img_casa.append(rodada.imagem_casa)
            img_visitante.append(rodada.imagem_fora)

        if request.method == "POST":
            # data = get_api_data(verificacao_partida.partida_atual)
            dados = request.POST
            resultados_form = dict(dados)


            #salvando os resultados dos times e rodadas no banco de dados
            if resultados_form["resultado_casa"] and resultados_form["resultado_visitante"]:
                for resultado_visitante in resultados_form["resultado_visitante"]:
                    placar_visitante.append(resultado_visitante)

                for resultado_casa in resultados_form["resultado_casa"]:
                    placar_casa.append(resultado_casa)

                for rodada in resultados_form["rodada_atual"]:
                    rodada_dict.append(rodada)


            resultado_tabela = {
                    "time_casa": time_casa,
                    "img_casa": img_casa,
                    "placar_casa": placar_casa,
                    "placar_visitante": placar_visitante,
                    "time_visitante": time_visitante,
                    "img_visitante": img_visitante,
                    "rodada_atual": rodada_dict
            }


            df_tabela = pd.DataFrame(resultado_tabela)
                # Iterar sobre o DataFrame e criar instâncias do modelo Rodada1
                #criando o banco de dados
            for _, row in df_tabela.iterrows():
                jogos_rodada_criado  = Palpite.objects.create(
                    time_casa=row['time_casa'],
                    imagem_casa=row['img_casa'],
                    placar_casa=row['placar_casa'],
                    placar_visitante=row['placar_visitante'],
                    time_visitante=row['time_visitante'],
                    imagem_fora=row['img_visitante'],
                    usuario=user,
                    rodada_atual=row['rodada_atual'],
                    )

            messages.error(request, f'{verificacao_partida.partida_atual}ª rodada salva com sucesso')
            verificacao_partida.partida_atual += 1
            verificacao_partida.save()

            return redirect('palpites')

        context = {"rodadas":rodadas, 'verificacao_partida':verificacao_partida.verificado}
        return render(request,'palpites.html', context)
    else:
        return redirect('login_bolao')


def meus_palpites(request):
    if request.user.is_authenticated:
        user = request.user
        rodadas = Palpite.objects.filter(usuario=user).order_by('rodada_atual')
        #pagination
        paginator = Paginator(rodadas, 10)
        page_obj = request.GET.get('page')
        posts = paginator.get_page(page_obj)

        context = {'posts':posts, 'rodadas':rodadas}
        return render(request,'meus_palpites.html', context)
    else:
        return redirect('login_bolao')

def regras(request):
    user = request.user
    palpites = Palpite.objects.filter(usuario=user,rodada_atual=5)
    total_pontos_rodadas = []
    for usuario in palpites:
        total_pontos_rodadas.append(usuario.vitorias)
        total_pontos_rodadas.append(usuario.placar_exato)
    print(sum(total_pontos_rodadas))
    return render(request,'regras.html')

@user_passes_test(lambda u: u.is_superuser)
def configuracoes(request):
    user = request.user
    if request.method == 'POST':
        rodada_inicial = request.POST.get('rodada_inicial')
        rodada_final = request.POST.get('rodada_final')
        rodada_original = request.POST.get('rodada_original')

        apagar_rodada = request.POST.get('apagar_rodada')
        criar_rodadas = request.POST.get('criar_rodadas')

        resetar_pontuacao_usuario_normal = request.POST.get('resetar_pontuacao')
        resetar_pontuacao_usuario_rodada = request.POST.get('resetar_pontuacao_usuario_por_rodada')
        zerar_palpites = request.POST.get('zerar_palpites')

        bloquear_partidas_por_rodada = request.POST.get('bloquear_partidas_por_rodada')
        desbloquear_partidas_por_rodada = request.POST.get('desbloquear_partidas_por_rodada')

        bloquear_partidas_normal = request.POST.get('bloquear_partidas_normal')
        desbloquear_partidas_normal = request.POST.get('desbloquear_partidas_normal')

        rodada_atualizada_por_rodada = request.POST.get('rodada_atualizada_por_rodada')
        rodada_atualizada_normal = request.POST.get('rodada_atualizada_normal')

        if zerar_palpites:
            thread = threading.Thread(target=zerar_palpites_usuarios(zerar_palpites))
            thread.start()

        # Atualizar classificação normal passando o número da rodada e o tipo_aposta do usuário
        if rodada_atualizada_normal:
            thread = threading.Thread(target=calcular_pontuacao_usuario(rodada_atualizada_normal, "normal"))
            thread.start()

        # Atualizar classificação por rodada passando o número da rodada e o tipo_aposta do usuário
        if rodada_atualizada_por_rodada:
            thread = threading.Thread(target=calcular_pontuacao_usuario(rodada_atualizada_por_rodada, "por_rodada"))
            thread.start()

        if rodada_original:
            thread = threading.Thread(target=salvar_rodada_original(rodada_original))
            thread.start()

        if apagar_rodada:
            RodadaOriginal.objects.filter(rodada_atual=apagar_rodada).delete()

        if resetar_pontuacao_usuario_normal:
            thread = threading.Thread(target=resetar_pontuacao_usuarios_normal())
            thread.start()

        if resetar_pontuacao_usuario_rodada:
            thread = threading.Thread(target=resetar_pontuacao_usuario_por_rodada())
            thread.start()

        # Desbloquear e Bloquear as partidas dos usuario que estão no modo Por Rodada
        if bloquear_partidas_por_rodada:
            usuarios = Usuario.objects.filter(tipo_aposta="por_rodada")
            for usuario in usuarios:
                bloquear = Verificacao.objects.filter(user=usuario.usuario)
                for partida in bloquear:
                    partida.verificado = True
                    partida.save()

        if desbloquear_partidas_por_rodada:
            usuarios = Usuario.objects.filter(tipo_aposta="por_rodada")
            for usuario in usuarios:
                bloquear = Verificacao.objects.filter(user=usuario.usuario)
                for partida in bloquear:
                    partida.verificado = False
                    partida.save()

        #TODO criar a verificação das partidas
        # Desbloquear e Bloquear as partidas dos usuario que estão no modo Normal
        if bloquear_partidas_normal:
            usuarios = Usuario.objects.filter(tipo_aposta="normal")
            for usuario in usuarios:
                bloquear = Verificacao.objects.filter(user=usuario.usuario)
                for partida in bloquear:
                    partida.verificado = True
                    partida.save()

        if desbloquear_partidas_normal:
            usuarios = Usuario.objects.filter(tipo_aposta="normal")
            for usuario in usuarios:
                bloquear = Verificacao.objects.filter(user=usuario.usuario)
                for partida in bloquear:
                    partida.verificado = False
                    partida.save()


        if criar_rodadas:
            if Rodada.objects.exists():
                messages.error(request, 'Rodadas campeonato já foram criadas!')
                return redirect('configuracoes')
            else:
                thread = threading.Thread(target=criar_rodadas_campeonato())
                thread.start()
                print("Rodadas Criadas com sucesso!")

        else:
            print("Checkbox desativo")


        # Pegando a rodada inicial, final e qual o tipo da aposta do usuario para desbloquear as partidas
        if rodada_inicial and rodada_final and desbloquear_partidas_normal:
            if int(rodada_inicial) >= int(rodada_final) or int(rodada_final) > 39:
                messages.error(request, 'A rodada inicial não pode ser maior ou igual que a rodada final. Rodada final não poede ser maior que 38')
                return redirect('configuracoes')
            else:
                setar_rodadaAtual_rodadaFinal(rodada_inicial, rodada_final,"normal")
                print('Rodadas setadas!')

        elif rodada_inicial and rodada_final and desbloquear_partidas_por_rodada:
            if int(rodada_inicial) >= int(rodada_final) or int(rodada_final) > 39:
                messages.error(request, 'A rodada inicial não pode ser maior ou igual que a rodada final. Rodada final não poede ser maior que 38')
                return redirect('configuracoes')
            else:
                setar_rodadaAtual_rodadaFinal(rodada_inicial, rodada_final,"por_rodada")
                print('Rodadas setadas!')
        else:
            messages.error(request, 'Campos rodadas vazios!')
            return redirect('configuracoes')

    return render(request,'configuracoes.html')


def perfil(request):
    user = request.user
    usuarios = Usuario.objects.filter(usuario=user)

    if request.method == 'POST':
        dados = request.POST.dict()

        try:
            img = request.FILES['img']
        except KeyError:
            img = 'imagens/perfil-null.png'

        for usuario in usuarios:
            usuario.avatar = img
            usuario.save()

    context = {"usuarios":usuarios}
    return render(request, 'perfil.html', context)

def pagamento_bolao(request):
    user = request.user
    usuario = Usuario.objects.get(usuario=user)
    bloquear = BloquearPartida.objects.get(id=1)
    print(bloquear)
    if request.method == "POST":
        dados = request.POST.dict()
        formato_bolao = dados.get("tipo_aposta")
        valor = dados.get("valor")
        link =request.build_absolute_uri(reverse("finalizar_pagamento"))
        link_pagamento, id_pagamento = criar_pagamento(valor,link)
        #TODO Criar a tabela pagamento e atribuir o id_pagamento a ela aqui
        pagamento = Pagamento.objects.create(id_pagamento=id_pagamento)
        pagamento.save()
        return redirect(link_pagamento)

    context = {"usuario":usuario, "bloquear":bloquear}
    return render(request, "pagamento_bolao.html", context)


def finalizar_pagamento(request):
    user = request.user

    dados = request.GET.dict()
    status = dados.get("status")
    id_pagamento = dados.get("preference_id")
    if status == "approved":
        pagamento = Pagamento.objects.get(id_pagamento=id_pagamento)
        pagamento.aprovado = True
        usuario = Usuario.objects.get(usuario=user)
        usuario.pagamento = True
        usuario.save()
        pagamento.save()
    return redirect("homepage")

def login_bolao(request):
    if request.user.is_authenticated:
        return redirect('homepage')
    if request.method == 'POST':
        nome = request.POST.get('usuario')
        senha = request.POST.get('senha')
        usuario = authenticate(request,username=nome,password=senha)
        if usuario:
            #fazer login
            login(request,usuario)
            return redirect('homepage')
        else:
            messages.error(request, 'usuário ou senha inválidos!')
            return redirect('login_bolao')
    return render(request,'autenticacao/login_bolao.html')



def cadastro(request):

    if request.method == 'POST':
        nome_form = request.POST.get('nome')
        nome = nome_form.strip()

        email = request.POST.get('email')
        whatsapp = request.POST.get('whatsapp')
        senha_form = request.POST.get('senha')
        senha = senha_form.strip()

        confirme_senha_form = request.POST.get('confirme_senha')
        confirme_senha = confirme_senha_form.strip()

        tipo_aposta = request.POST.get('tipo_aposta')

        if Usuario.objects.filter(nome=nome).exists():
            messages.error(request, 'Já existe um usuário cadastrado com esse nome.')
            return redirect('cadastro')

        if senha != confirme_senha:
            messages.error(request, "Senha inválida. senhas são diferentes")
            return redirect('cadastro')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Email já cadastrado')
            return redirect('cadastro')

        if Usuario.objects.filter(whatsapp=whatsapp).exists():
            messages.error(request, 'Número do Whatsapp já cadastrado')
            return redirect('cadastro')

        if len(whatsapp) < 15:
            messages.error(request, 'Número inválido! Tente novamente.')
            return redirect('cadastro')

        if tipo_aposta:
            print(f"Tipo da aposta: {tipo_aposta}")
        else:
            messages.error(request, 'Selecione uma forma de como participar do bolão virtual')
            return redirect('cadastro')
        try:
            # Criar o usuário do Django
            user = User.objects.create_user(username=nome, email=email, password=senha)

            # Criar o objeto Usuario e associar o campo 'usuario' com o usuário logado
            usuario = Usuario.objects.create(usuario=user,nome=nome,email=email, whatsapp=whatsapp, tipo_aposta=tipo_aposta)

            # Criar o objeto Classificacao e associar ao Usuario criado
            classificacao = Classificacao.objects.create(usuario=usuario)

            login(request, user)  # Faz o login automático após o cadastro
            return redirect('homepage')
        except Exception as e:
            return HttpResponse(f"Erro ao criar o usuário: {str(e)}", status=500)

          # Redireciona para a página inicial

    return render(request,'autenticacao/cadastro.html')


def fazer_logout(request):
    logout(request)
    return redirect('login_bolao')
