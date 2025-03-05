from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Empresa(models.Model):
    SEGMENTO_CHOICES = [
        ('COM', 'Comércio'),
        ('SER', 'Serviços'),
        ('IND', 'Indústria'),
        ('TEC', 'Tecnologia'),
        ('SAU', 'Saúde'),
        ('EDU', 'Educação'),
        ('FIN', 'Finanças'),
        ('OUT', 'Outros'),
    ]
    
    nome = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=18, unique=True)
    razao_social = models.CharField(max_length=200)
    endereco = models.TextField()
    telefone = models.CharField(max_length=20)
    email = models.EmailField()
    data_fundacao = models.DateField()
    segmento = models.CharField(max_length=3, choices=SEGMENTO_CHOICES, default='OUT')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

class CategoriaJuridica(models.Model):
    TIPO_CHOICES = [
        ('R', 'Receita'),
        ('D', 'Despesa'),
    ]
    
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    cor = models.CharField(max_length=7, default='#000000')  # Campo para cor em formato hexadecimal
    descricao = models.TextField(blank=True, null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.nome} - {self.empresa.nome}"
    
    class Meta:
        verbose_name = 'Categoria Jurídica'
        verbose_name_plural = 'Categorias Jurídicas'

class ContaJuridica(models.Model):
    TIPO_CHOICES = [
        ('CC', 'Conta Corrente'),
        ('CP', 'Conta Poupança'),
        ('CI', 'Conta Investimento'),
        ('CX', 'Caixa'),
        ('OU', 'Outros'),
    ]
    
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=2, choices=TIPO_CHOICES)
    banco = models.CharField(max_length=100, blank=True, null=True)
    agencia = models.CharField(max_length=20, blank=True, null=True)
    numero = models.CharField(max_length=20, blank=True, null=True)
    saldo = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.nome} - {self.empresa.nome} - R$ {self.saldo}"
    
    class Meta:
        verbose_name = 'Conta Jurídica'
        verbose_name_plural = 'Contas Jurídicas'

class TransacaoJuridica(models.Model):
    TIPO_CHOICES = [
        ('R', 'Receita'),
        ('D', 'Despesa'),
        ('T', 'Transferência'),
    ]
    
    METODO_PAGAMENTO_CHOICES = [
        ('DI', 'Dinheiro'),
        ('CC', 'Cartão de Crédito'),
        ('CD', 'Cartão de Débito'),
        ('BO', 'Boleto'),
        ('PI', 'Pix'),
        ('TR', 'Transferência'),
        ('CH', 'Cheque'),
        ('OU', 'Outros'),
    ]
    
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    data = models.DateField(default=timezone.now)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    metodo_pagamento = models.CharField(max_length=2, choices=METODO_PAGAMENTO_CHOICES, default='DI')
    categoria = models.ForeignKey(CategoriaJuridica, on_delete=models.SET_NULL, null=True, blank=True)
    conta = models.ForeignKey(ContaJuridica, on_delete=models.CASCADE, related_name='transacoes')
    conta_destino = models.ForeignKey(ContaJuridica, on_delete=models.CASCADE, null=True, blank=True, related_name='transacoes_destino')
    observacao = models.TextField(blank=True, null=True)
    numero_nota = models.CharField(max_length=50, blank=True, null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.descricao} - {self.empresa.nome} - R$ {self.valor}"
    
    class Meta:
        verbose_name = 'Transação Jurídica'
        verbose_name_plural = 'Transações Jurídicas'
        ordering = ['-data']
    
    def save(self, *args, **kwargs):
        # Verifica se é uma nova transação
        nova_transacao = self.pk is None
        
        super().save(*args, **kwargs)
        
        # Atualiza o saldo da conta apenas se for uma nova transação
        if nova_transacao:
            if self.tipo == 'R':  # Receita
                self.conta.saldo += self.valor
                self.conta.save()
            elif self.tipo == 'D':  # Despesa
                self.conta.saldo -= self.valor
                self.conta.save()
            elif self.tipo == 'T' and self.conta_destino:  # Transferência
                self.conta.saldo -= self.valor
                self.conta_destino.saldo += self.valor
                self.conta.save()
                self.conta_destino.save()

class Imposto(models.Model):
    TIPO_CHOICES = [
        ('IRPJ', 'Imposto de Renda Pessoa Jurídica'),
        ('CSLL', 'Contribuição Social sobre o Lucro Líquido'),
        ('PIS', 'Programa de Integração Social'),
        ('COFINS', 'Contribuição para o Financiamento da Seguridade Social'),
        ('ISS', 'Imposto Sobre Serviços'),
        ('ICMS', 'Imposto sobre Circulação de Mercadorias e Serviços'),
        ('IPI', 'Imposto sobre Produtos Industrializados'),
        ('INSS', 'Instituto Nacional do Seguro Social'),
        ('FGTS', 'Fundo de Garantia do Tempo de Serviço'),
        ('OUTROS', 'Outros Impostos'),
    ]
    
    nome = models.CharField(max_length=50, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    data_vencimento = models.DateField()
    data_pagamento = models.DateField(null=True, blank=True)
    status = models.BooleanField(default=False)  # False: não pago, True: pago
    periodo_referencia = models.CharField(max_length=7)  # Formato: MM/AAAA
    observacao = models.TextField(blank=True, null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.get_nome_display()} - {self.periodo_referencia} - {self.empresa.nome}"
    
    class Meta:
        verbose_name = 'Imposto'
        verbose_name_plural = 'Impostos'
        ordering = ['data_vencimento']
