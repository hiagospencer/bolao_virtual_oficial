# Generated by Django 5.1.2 on 2024-11-11 23:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bolao', '0009_classificacao_posicao_variacao_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='classificacao',
            name='posicao_anterior',
        ),
        migrations.RemoveField(
            model_name='classificacao',
            name='posicao_atual',
        ),
        migrations.RemoveField(
            model_name='classificacao',
            name='posicao_variacao',
        ),
        migrations.DeleteModel(
            name='Pontuacao',
        ),
    ]
