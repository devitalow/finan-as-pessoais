from django.contrib import admin
from .models import Categoria, Conta, Transacao

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'usuario')
    list_filter = ('tipo', 'usuario')
    search_fields = ('nome', 'descricao')

@admin.register(Conta)
class ContaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'saldo', 'usuario')
    list_filter = ('tipo', 'usuario')
    search_fields = ('nome',)

@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'valor', 'data', 'tipo', 'categoria', 'conta', 'usuario')
    list_filter = ('tipo', 'data', 'categoria', 'conta', 'usuario')
    search_fields = ('descricao', 'observacao')
    date_hierarchy = 'data'
