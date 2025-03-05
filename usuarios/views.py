from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from .forms import UsuarioRegistroForm, UsuarioAtualizacaoForm, PerfilForm
from django.contrib.auth.views import LoginView
from django.views.decorators.http import require_http_methods

class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'
    
    def form_valid(self, form):
        # Define a visão padrão como 'pessoal' quando o usuário faz login
        self.request.session['visao'] = 'pessoal'
        return super().form_valid(form)

def registro(request):
    if request.method == 'POST':
        form = UsuarioRegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {username}! Agora você pode fazer login.')
            return redirect('login')
    else:
        form = UsuarioRegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})

@login_required
def perfil(request):
    if request.method == 'POST':
        u_form = UsuarioAtualizacaoForm(request.POST, instance=request.user)
        p_form = PerfilForm(request.POST, request.FILES, instance=request.user.perfil)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Seu perfil foi atualizado com sucesso!')
            return redirect('perfil')
    else:
        u_form = UsuarioAtualizacaoForm(instance=request.user)
        p_form = PerfilForm(instance=request.user.perfil)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    
    return render(request, 'usuarios/perfil.html', context)

@require_http_methods(["POST"])
def alternar_visao(request):
    """
    Alterna entre a visão de finanças pessoais e jurídicas.
    Aceita apenas requisições POST para evitar problemas de cache.
    """
    visao_atual = request.session.get('visao', 'pessoal')
    nova_visao = 'juridico' if visao_atual == 'pessoal' else 'pessoal'
    request.session['visao'] = nova_visao
    
    # Adiciona uma mensagem de feedback
    mensagem = 'Alterado para Finanças Jurídicas' if nova_visao == 'juridico' else 'Alterado para Finanças Pessoais'
    messages.success(request, mensagem)
    
    # Redireciona para o dashboard apropriado
    return redirect('dashboard_juridico' if nova_visao == 'juridico' else 'dashboard_pessoal')

@require_http_methods(["GET", "POST"])
def logout_view(request):
    """
    View para realizar o logout do usuário.
    Aceita tanto requisições GET quanto POST.
    """
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Você foi desconectado com sucesso!')
    return redirect('login')
