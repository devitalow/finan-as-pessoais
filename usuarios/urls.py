from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Registro e Perfil
    path('registro/', views.registro, name='registro'),
    path('perfil/', views.perfil, name='perfil'),
    
    # Alteração de Senha
    path('alterar-senha/', auth_views.PasswordChangeView.as_view(
        template_name='usuarios/alterar_senha.html',
        success_url='/usuarios/alterar-senha/concluido/'
    ), name='alterar_senha'),
    path('alterar-senha/concluido/', auth_views.PasswordChangeDoneView.as_view(
        template_name='usuarios/password_change_done.html'
    ), name='password_change_done'),
    
    # Redefinição de Senha
    path('redefinir-senha/', auth_views.PasswordResetView.as_view(
        template_name='usuarios/password_reset.html',
        email_template_name='usuarios/password_reset_email.html',
        subject_template_name='usuarios/password_reset_subject.txt',
        success_url='/usuarios/redefinir-senha/enviado/'
    ), name='password_reset'),
    path('redefinir-senha/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='usuarios/password_reset_done.html'
    ), name='password_reset_done'),
    path('redefinir-senha/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='usuarios/password_reset_confirm.html',
        success_url='/usuarios/redefinir-senha/concluido/'
    ), name='password_reset_confirm'),
    path('redefinir-senha/concluido/', auth_views.PasswordResetCompleteView.as_view(
        template_name='usuarios/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Alternar entre visão pessoal e jurídica
    path('alternar-visao/', views.alternar_visao, name='alternar_visao'),
] 