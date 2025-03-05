from django.contrib import admin
from .models import Empresa, CategoriaJuridica, ContaJuridica, TransacaoJuridica, Imposto

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'razao_social', 'usuario')
    search_fields = ('nome', 'cnpj', 'razao_social')
    list_filter = ('usuario',)

@admin.register(CategoriaJuridica)
class CategoriaJuridicaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'empresa', 'usuario')
    list_filter = ('tipo', 'empresa', 'usuario')
    search_fields = ('nome', 'descricao')

@admin.register(ContaJuridica)
class ContaJuridicaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'banco', 'saldo', 'empresa', 'usuario')
    list_filter = ('tipo', 'empresa', 'usuario')
    search_fields = ('nome', 'banco', 'agencia', 'numero')

@admin.register(TransacaoJuridica)
class TransacaoJuridicaAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'valor', 'data', 'tipo', 'metodo_pagamento', 'categoria', 'conta', 'empresa', 'usuario')
    list_filter = ('tipo', 'metodo_pagamento', 'data', 'categoria', 'conta', 'empresa', 'usuario')
    search_fields = ('descricao', 'observacao', 'numero_nota')
    date_hierarchy = 'data'

@admin.register(Imposto)
class ImpostoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor', 'data_vencimento', 'status', 'periodo_referencia', 'empresa', 'usuario')
    list_filter = ('nome', 'status', 'data_vencimento', 'empresa', 'usuario')
    search_fields = ('observacao', 'periodo_referencia')
    date_hierarchy = 'data_vencimento'
