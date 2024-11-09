from django.http import HttpResponse

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
