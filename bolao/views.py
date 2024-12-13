import threading
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
import pandas as pd
from django.core.mail import send_mail
from django.utils.timezone import now

from .models import *
from .utils import *
from .api_mercadopago import criar_pagamento
from .tasks import *


def homepage(request):
    if request.user.is_authenticated:
        user = request.user
        participante = Classificacao.objects.get(usuario__usuario=user)
        usuarios = Classificacao.objects.filter(usuario__pagamento=True).order_by('-pontos', '-placar_exato', '-vitorias', '-empates')
        # Itera sobre a classificação e atribui as posições

        context = {'usuarios':usuarios, "participante":participante}
        return render(request, 'index.html',context)
    else:
        usuarios = Classificacao.objects.filter(usuario__pagamento=True).order_by('-pontos', '-placar_exato', '-vitorias', '-empates')

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
            rodada_verificacao = resultados_form["rodada_atual"][0]
            # Verificar se já existe a rodada
            if Palpite.objects.filter(rodada_atual=rodada_verificacao,usuario=user).exists():
                messages.error(request, f'Rodada {rodada_verificacao} já foi salva.')
                return redirect('palpites')
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

        zerar_palpites = request.POST.get('zerar_palpites')

        bloquear_partidas_normal = request.POST.get('bloquear_partidas_normal')
        desbloquear_partidas_normal = request.POST.get('desbloquear_partidas_normal')

        rodada_atualizada_normal = request.POST.get('rodada_atualizada_normal')

        resetar_pagamento_usuario = request.POST.get('resetar_pagamento')

        if zerar_palpites:
            thread = threading.Thread(target=zerar_palpites_usuarios(zerar_palpites))
            thread.start()

        if resetar_pagamento_usuario:
            thread = threading.Thread(target=resetar_pagamento())
            thread.start()

        # Atualizar classificação normal passando o número da rodada e o tipo_aposta do usuário
        if rodada_atualizada_normal:
            # classificacao = Classificacao.objects.filter(usuario__pagamento=True).order_by('-pontos', '-placar_exato', '-vitorias', '-empates')
            # thread = threading.Thread(target=calcular_pontuacao_usuario(rodada_atualizada_normal))
            # thread.start()
            calcular_pontuacao_usuario_tasks.delay(rodada_atualizada_normal)

        if rodada_original:
            thread = threading.Thread(target=salvar_rodada_original(rodada_original))
            thread.start()

        if apagar_rodada:
            RodadaOriginal.objects.filter(rodada_atual=apagar_rodada).delete()
        if resetar_pontuacao_usuario_normal:
            thread = threading.Thread(target=resetar_pontuacao_usuarios_normal())
            thread.start()
        # Desbloquear e Bloquear as partidas dos usuario que estão no modo Normal
        if bloquear_partidas_normal:
            bloquear = Verificacao.objects.all()
            for partida in bloquear:
                partida.verificado = True
                partida.save()
        if desbloquear_partidas_normal:
            bloquear = Verificacao.objects.all()
            for partida in bloquear:
                partida.verificado = False
                partida.save()
        if criar_rodadas:
            if Rodada.objects.exists():
                messages.error(request, 'Rodadas campeonato já foram criadas!')
                return redirect('configuracoes')
            else:
                criar_rodadas_campeonato_tasks.delay()
                print("Rodadas Criadas com sucesso!")
        else:
            print("Checkbox desativo")
        # Pegando a rodada inicial, final e qual o tipo da aposta do usuario para desbloquear as partidas
        if rodada_inicial and rodada_final:
            if int(rodada_inicial) >= int(rodada_final) or int(rodada_final) > 39:
                messages.error(request, 'A rodada inicial não pode ser maior ou igual que a rodada final. Rodada final não poede ser maior que 38')
                return redirect('configuracoes')
            else:
                setar_rodadaAtual_rodadaFinal(rodada_inicial, rodada_final)
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
    if request.method == "POST":
        dados = request.POST.dict()
        link =request.build_absolute_uri(reverse("finalizar_pagamento"))
        link_pagamento, id_pagamento = criar_pagamento(link)
        pagamento,criado = Pagamento.objects.get_or_create(participante=user,id_pagamento=id_pagamento)
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
        pagamento = Pagamento.objects.get(participante=user,id_pagamento=id_pagamento)
        desbloquear_rodadas = Verificacao.objects.get(user=user)
        desbloquear_rodadas.verificado = False
        pagamento.aprovado = True
        pagamento.status = "aprovado"
        pagamento.data_pagamento = now()
        usuario = Usuario.objects.get(usuario=user)
        email = usuario.email
        usuario.pagamento = True
        usuario.save()
        pagamento.save()
        desbloquear_rodadas.save()
        enviar_email(email)
    elif status == 'rejected':
        pagamento = Pagamento.objects.get(participante=user,id_pagamento=id_pagamento)
        pagamento.aprovado = False
        pagamento.status = "rejeitado"
        pagamento.data_pagamento = now()
    elif status == 'pending':
        pagamento = Pagamento.objects.get(participante=user,id_pagamento=id_pagamento)
        pagamento.aprovado = False
        pagamento.status = "pendente"
        pagamento.data_pagamento = now()
    else:
        print("Fim do pagamento")
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

        try:
            # Criar o usuário do Django
            user = User.objects.create_user(username=nome, email=email, password=senha)
            # Criar o objeto Usuario e associar o campo 'usuario' com o usuário logado
            usuario = Usuario.objects.create(usuario=user,nome=nome,email=email, whatsapp=whatsapp)
            # Criar o objeto Classificacao e associar ao Usuario criado
            classificacao = Classificacao.objects.create(usuario=usuario)
            destinatario = 'hiaguinhospencer@gmail.com'
            assunto = f"Novo cadastro no site Bolão Virtual!"
            corpo = f"""
            Nome: {nome}
            Email: {email}
            Whatsapp: {whatsapp}
            """
            remetente = "hiagosouzadev10@gmail.com"
            send_mail(assunto,corpo,remetente,[destinatario])
            login(request, user)  # Faz o login automático após o cadastro
            return redirect('homepage')
        except Exception as e:
            return HttpResponse(f"Erro ao criar o usuário: {str(e)}", status=500)
          # Redireciona para a página inicial
    return render(request,'autenticacao/cadastro.html')

def fazer_logout(request):
    logout(request)
    return redirect('login_bolao')
