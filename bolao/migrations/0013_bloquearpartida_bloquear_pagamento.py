# Generated by Django 5.1.2 on 2024-11-15 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bolao', '0012_bloquearpartida_bloquear_grafico'),
    ]

    operations = [
        migrations.AddField(
            model_name='bloquearpartida',
            name='bloquear_pagamento',
            field=models.BooleanField(default=False),
        ),
    ]
