# Generated by Django 5.1.2 on 2024-11-05 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bolao', '0002_usuario_tipo_aposta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='tipo_aposta',
            field=models.CharField(max_length=30),
        ),
    ]