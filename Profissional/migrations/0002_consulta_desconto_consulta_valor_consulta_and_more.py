# Generated by Django 5.1 on 2024-11-05 16:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profissional', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='consulta',
            name='desconto',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='consulta',
            name='valor_consulta',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='paciente',
            name='dt_ultima_consulta',
            field=models.DateField(default='2024-11-05'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paciente',
            name='qtd_consultas',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='paciente',
            name='status',
            field=models.CharField(choices=[('A', 'Ativo'), ('I', 'Inativo')], default='A', max_length=1),
        ),
        migrations.CreateModel(
            name='Despesa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao', models.CharField(max_length=255)),
                ('tipo', models.CharField(choices=[('FIXA', 'Fixa'), ('VARIAVEL', 'Variável'), ('OUTRA', 'Outra')], max_length=20)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('data', models.DateField()),
                ('profissional', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Profissional.profissional')),
            ],
        ),
    ]