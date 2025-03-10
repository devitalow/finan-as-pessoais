# Generated by Django 5.1.6 on 2025-03-05 04:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financas_pessoais', '0005_delete_meta'),
    ]

    operations = [
        migrations.AddField(
            model_name='transacao',
            name='data_primeira_parcela',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='transacao',
            name='is_financiamento',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='transacao',
            name='juros',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Taxa de juros em %', max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='transacao',
            name='metodo_pagamento',
            field=models.CharField(choices=[('AV', 'À Vista'), ('CC', 'Cartão de Crédito'), ('FI', 'Financiamento'), ('BO', 'Boleto'), ('PI', 'Pix'), ('DI', 'Dinheiro'), ('OU', 'Outros')], default='AV', max_length=2),
        ),
        migrations.AddField(
            model_name='transacao',
            name='numero_parcelas',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='transacao',
            name='valor_parcela',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
    ]
