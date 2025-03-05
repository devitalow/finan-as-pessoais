from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard_juridico, name='dashboard_juridico'),
    path('selecionar-empresa/<int:empresa_id>/', views.selecionar_empresa, name='selecionar_empresa'),
    
    # Empresas
    path('empresas/', views.lista_empresas, name='lista_empresas'),
    path('empresas/criar/', views.criar_empresa, name='criar_empresa'),
    path('empresas/editar/<int:pk>/', views.editar_empresa, name='editar_empresa'),
    path('empresas/excluir/<int:pk>/', views.excluir_empresa, name='excluir_empresa'),
    
    # Categorias
    path('categorias/', views.lista_categorias_juridicas, name='lista_categorias_juridicas'),
    path('categorias/criar/', views.criar_categoria_juridica, name='criar_categoria_juridica'),
    path('categorias/editar/<int:pk>/', views.editar_categoria_juridica, name='editar_categoria_juridica'),
    path('categorias/excluir/<int:pk>/', views.excluir_categoria_juridica, name='excluir_categoria_juridica'),
    
    # Contas
    path('contas/', views.lista_contas_juridicas, name='lista_contas_juridicas'),
    path('contas/criar/', views.criar_conta_juridica, name='criar_conta_juridica'),
    path('contas/editar/<int:pk>/', views.editar_conta_juridica, name='editar_conta_juridica'),
    path('contas/excluir/<int:pk>/', views.excluir_conta_juridica, name='excluir_conta_juridica'),
    
    # Transações
    path('transacoes/', views.lista_transacoes_juridicas, name='lista_transacoes_juridicas'),
    path('transacoes/criar/', views.criar_transacao_juridica, name='criar_transacao_juridica'),
    path('transacoes/editar/<int:pk>/', views.editar_transacao_juridica, name='editar_transacao_juridica'),
    path('transacoes/excluir/<int:pk>/', views.excluir_transacao_juridica, name='excluir_transacao_juridica'),
    
    # Impostos
    path('impostos/', views.lista_impostos, name='lista_impostos'),
    path('impostos/criar/', views.criar_imposto, name='criar_imposto'),
    path('impostos/editar/<int:pk>/', views.editar_imposto, name='editar_imposto'),
    path('impostos/excluir/<int:pk>/', views.excluir_imposto, name='excluir_imposto'),
    path('impostos/pagar/<int:pk>/', views.marcar_imposto_pago, name='marcar_imposto_pago'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
] 