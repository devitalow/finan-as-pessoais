from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Categoria(models.Model):
    TIPO_CHOICES = [
        ('R', 'Receita'),
        ('D', 'Despesa'),
    ]
    
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    descricao = models.TextField(blank=True, null=True)
    cor = models.CharField(max_length=7, default='#3498db')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

class Conta(models.Model):
    TIPO_CHOICES = [
        ('CC', 'Conta Corrente'),
        ('CP', 'Conta Poupança'),
        ('CI', 'Conta Investimento'),
        ('DI', 'Dinheiro'),
        ('OU', 'Outros'),
    ]
    
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=2, choices=TIPO_CHOICES)
    saldo = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    saldo_inicial = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    descricao = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        # Se for uma nova conta, inicializa o saldo com o valor do saldo_inicial
        if not self.pk:
            self.saldo = self.saldo_inicial
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Conta'
        verbose_name_plural = 'Contas'

class Transacao(models.Model):
    TIPO_CHOICES = [
        ('R', 'Receita'),
        ('D', 'Despesa'),
        ('T', 'Transferência'),
    ]
    
    METODO_PAGAMENTO_CHOICES = [
        ('CC', 'Cartão de Crédito'),
        ('FI', 'Financiamento'),
        ('BO', 'Boleto'),
        ('PI', 'Pix'),
        ('DI', 'Dinheiro'),
        ('OU', 'Outros'),
    ]
    
    descricao = models.CharField(max_length=500)
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    data = models.DateField(default=timezone.now)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    conta = models.ForeignKey(Conta, on_delete=models.CASCADE, related_name='transacoes')
    conta_destino = models.ForeignKey(Conta, on_delete=models.CASCADE, null=True, blank=True, related_name='transacoes_destino')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Campos para financiamento
    metodo_pagamento = models.CharField(max_length=2, choices=METODO_PAGAMENTO_CHOICES, default='DI')
    is_financiamento = models.BooleanField(default=False)
    numero_parcelas = models.IntegerField(null=True, blank=True)
    valor_parcela = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    data_primeira_parcela = models.DateField(null=True, blank=True)
    juros = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='Taxa de juros em %')
    
    def __str__(self):
        return self.descricao
    
    class Meta:
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'
        ordering = ['-data']
    
    def save(self, *args, **kwargs):
        # Verifica se é uma nova transação
        is_new = self.pk is None
        
        # Se for financiamento, calcula o valor da parcela se não estiver definido
        if self.is_financiamento and not self.valor_parcela and self.numero_parcelas:
            if self.juros:
                # Cálculo com juros compostos
                taxa = self.juros / 100  # Converte percentual para decimal
                self.valor_parcela = (self.valor * (taxa * (1 + taxa) ** self.numero_parcelas)) / ((1 + taxa) ** self.numero_parcelas - 1)
            else:
                # Cálculo sem juros
                self.valor_parcela = self.valor / self.numero_parcelas
        
        # Salva a transação
        super().save(*args, **kwargs)
        
        # Atualiza o saldo da conta apenas se for uma nova transação
        if is_new:
            if self.tipo == 'R':  # Receita
                self.conta.saldo += self.valor
                self.conta.save()
            elif self.tipo == 'D':  # Despesa
                if not self.is_financiamento:  # Se não for financiamento, deduz o valor total
                    self.conta.saldo -= self.valor
                else:  # Se for financiamento, deduz apenas o valor da primeira parcela
                    self.conta.saldo -= self.valor_parcela
                self.conta.save()
            elif self.tipo == 'T' and self.conta_destino:  # Transferência
                self.conta.saldo -= self.valor
                self.conta.save()
                self.conta_destino.saldo += self.valor
                self.conta_destino.save()
