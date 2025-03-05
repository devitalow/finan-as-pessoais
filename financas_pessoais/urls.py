from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard_pessoal'),
    
    # Categorias
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/criar/', views.criar_categoria, name='criar_categoria'),
    path('categorias/editar/<int:pk>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/excluir/<int:pk>/', views.excluir_categoria, name='excluir_categoria'),
    
    # Contas
    path('contas/', views.lista_contas, name='lista_contas'),
    path('contas/criar/', views.criar_conta, name='criar_conta'),
    path('contas/editar/<int:pk>/', views.editar_conta, name='editar_conta'),
    path('contas/excluir/<int:pk>/', views.excluir_conta, name='excluir_conta'),
    
    # Transações
    path('transacoes/', views.lista_transacoes, name='lista_transacoes'),
    path('transacoes/criar/', views.criar_transacao, name='criar_transacao'),
    path('transacoes/editar/<int:pk>/', views.editar_transacao, name='editar_transacao'),
    path('transacoes/excluir/<int:pk>/', views.excluir_transacao, name='excluir_transacao'),
    
    # Relatórios
    path('relatorios/', views.relatorios, name='relatorios'),
    path('relatorios/por-periodo/', views.relatorio_por_periodo, name='relatorio_por_periodo'),
    path('relatorios/por-categoria/', views.relatorio_por_categoria, name='relatorio_por_categoria'),
    path('relatorios/exportar-csv/', views.exportar_transacoes_csv, name='exportar_transacoes_csv'),
    
    # Metas (comentadas pois o modelo Meta foi removido)
    # path('metas/', views.lista_metas, name='lista_metas'),
    # path('metas/criar/', views.criar_meta, name='criar_meta'),
    # path('metas/editar/<int:pk>/', views.editar_meta, name='editar_meta'),
    # path('metas/atualizar/<int:pk>/', views.atualizar_meta, name='atualizar_meta'),
    # path('metas/excluir/<int:pk>/', views.excluir_meta, name='excluir_meta'),
] 