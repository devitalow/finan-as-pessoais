"""
URL configuration for financas_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from usuarios.views import CustomLoginView
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

def index_redirect(request):
    """
    Redireciona para o dashboard apropriado baseado na visão atual ou estado de autenticação
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    visao = request.session.get('visao', 'pessoal')
    return redirect('dashboard_juridico' if visao == 'juridico' else 'dashboard_pessoal')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Autenticação
    path('login/', CustomLoginView.as_view(), name='login'),
    
    # URLs para usuários (incluindo logout)
    path('usuarios/', include('usuarios.urls')),
    
    # Redirecionamento da raiz para o dashboard apropriado
    path('', index_redirect, name='index'),
    
    # URLs para finanças pessoais
    path('pessoal/', include('financas_pessoais.urls')),
    
    # URLs para finanças jurídicas
    path('juridico/', include('financas_juridicas.urls')),
]

# Adicionar URLs para arquivos de mídia em desenvolvimento
if settings.DEBUG:
    # Debug Toolbar deve ser o primeiro
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    
    # Arquivos estáticos e mídia
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
