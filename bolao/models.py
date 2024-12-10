from django.db import models
from django.contrib.auth.models import User



class Usuario(models.Model):
    nome = models.CharField(max_length=200, null=True, blank=True)
    usuario = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    email = models.CharField(max_length=200, null=True, blank=True, unique=True)
    whatsapp = models.CharField(max_length=200, null=True, blank=True, unique=True)
    pagamento = models.BooleanField(default=False)
    imagem = models.ImageField( default='perfil-null.png')
    avatar = models.ImageField(default='perfil-null.png')

    def __str__(self):
        return f"{self.nome}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.user}"

class Classificacao(models.Model):
    usuario = models.OneToOneField(Usuario, null=True, blank=True, on_delete=models.CASCADE)
    pontos = models.IntegerField(default=0)
    placar_exato = models.IntegerField(default=0)
    vitorias = models.IntegerField(default=0)
    empates = models.IntegerField(default=0)
    posicao_atual = models.IntegerField(null=True, blank=True)
    posicao_anterior = models.IntegerField(null=True, blank=True)
    posicao_variacao = models.IntegerField(null=True, blank=True)

class Palpite(models.Model):
    usuario = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    rodada_atual = models.IntegerField(default=1)
    time_casa = models.CharField(max_length=50)
    placar_casa = models.IntegerField(default=0)
    time_visitante = models.CharField(max_length=50)
    placar_visitante = models.IntegerField(default=0)
    imagem_casa = models.ImageField(upload_to='emblemas_times')
    imagem_fora = models.ImageField(upload_to='emblemas_times')
    vencedor = models.CharField(max_length=50)
    finalizado = models.BooleanField(default=False)
    tipo_class = models.CharField(max_length=50, default='none')
    placar_exato = models.IntegerField(default=0)
    vitorias = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.placar_casa > self.placar_visitante:
            self.vencedor = self.time_casa
        elif self.placar_casa < self.placar_visitante:
            self.vencedor = self.time_visitante
        else:
            self.vencedor = 'empate'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.time_casa} x {self.time_visitante}"

class RodadaOriginal(models.Model):
    rodada_atual = models.IntegerField(default=1)
    time_casa = models.CharField(max_length=50)
    placar_casa = models.IntegerField(default=0)
    time_visitante = models.CharField(max_length=50)
    placar_visitante = models.IntegerField(default=0)
    vencedor = models.CharField(max_length=50)
    finalizado = models.BooleanField(default=False)

    def save(self, *args, **kwargs):

        if self.placar_casa > self.placar_visitante:
            self.vencedor = self.time_casa
        elif self.placar_casa < self.placar_visitante:
            self.vencedor = self.time_visitante
        else:
            self.vencedor = 'empate'

        if self.placar_casa == 9999 and self.placar_visitante == 9999:
            self.vencedor = 'andamento'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.time_casa} x {self.time_visitante}"

class Rodada(models.Model):
    rodada_atual = models.IntegerField(default=1)
    time_casa = models.CharField(max_length=50)
    placar_casa = models.CharField(null=True, blank=True)
    time_visitante = models.CharField(max_length=50)
    placar_visitante = models.CharField(null=True, blank=True)
    imagem_casa = models.ImageField(upload_to='emblemas_times')
    imagem_fora = models.ImageField(upload_to='emblemas_times')
    preenchido = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.time_casa} x {self.time_visitante}"

class Verificacao(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verificado = models.BooleanField(default=True)
    partida_atual = models.IntegerField(default=1)
    partida_final = models.IntegerField(default=39)

    def __str__(self):
        return f"Usuário: {self.user} - Verificado: {self.verificado} - partida atual: {self.partida_atual}ª - partida final: {self.partida_final}ª"

class BloquearPartida(models.Model):
    rodada_bloqueada = models.BooleanField(default=False)
    bloquear_grafico = models.BooleanField(default=False)
    bloquear_pagamento = models.BooleanField(default=False)

    def __str__(self):
        return f'Rodadas bloqueadas: {self.rodada_bloqueada} - Graficos Bloqueados: {self.bloquear_grafico} - Pagamento: {self.bloquear_pagamento}'

class Pagamento(models.Model):
    participante = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    id_pagamento = models.CharField(max_length=400)
    aprovado = models.BooleanField(default=False)
    data_pagamento = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pendente', 'Pendente'),
            ('aprovado', 'Aprovado'),
            ('rejeitado', 'Rejeitado'),
        ],
        default='pendente',
    )

    def __str__(self):
        return f"Usuario: {self.participante} | Status: {self.status}"
