# Generated by Django 5.1.2 on 2024-11-26 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bolao', '0017_alter_usuario_avatar_alter_usuario_imagem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='avatar',
            field=models.ImageField(default='perfil-null.png', upload_to=''),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='imagem',
            field=models.ImageField(default='perfil-null.png', upload_to=''),
        ),
    ]
