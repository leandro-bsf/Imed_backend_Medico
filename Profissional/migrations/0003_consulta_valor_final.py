# Generated by Django 5.1 on 2024-11-07 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profissional', '0002_consulta_desconto_consulta_valor_consulta_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='consulta',
            name='valor_final',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]