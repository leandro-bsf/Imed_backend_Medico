# Generated by Django 5.1 on 2024-09-10 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profissional', '0003_alter_profissional_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='profissional',
            name='chave_pix',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='profissional',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to='fotos_profissionais/'),
        ),
        migrations.AddField(
            model_name='profissional',
            name='fuso_horario',
            field=models.CharField(default='UTC', max_length=50),
        ),
        migrations.AddField(
            model_name='profissional',
            name='id_horario',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profissional',
            name='tempo_atuacao',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='profissional',
            name='valor_consulta',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]