from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Empresa, CategoriaJuridica, ContaJuridica, TransacaoJuridica, Imposto
from .forms import EmpresaForm, CategoriaJuridicaForm, ContaJuridicaForm, TransacaoJuridicaForm, ImpostoForm

@login_required
def dashboard_juridico(request):
    # Verificar se o usuário tem empresas cadastradas
    empresas = Empresa.objects.filter(usuario=request.user)
    
    if not empresas.exists():
        messages.warning(request, 'Você precisa cadastrar uma empresa primeiro.')
        return redirect('criar_empresa')
    
    # Selecionar empresa ativa
    empresa_id = request.session.get('empresa_ativa')
    if not empresa_id or not empresas.filter(id=empresa_id).exists():
        empresa_selecionada = empresas.first()
        request.session['empresa_ativa'] = empresa_selecionada.id
    else:
        empresa_selecionada = empresas.get(id=empresa_id)
    
    # Obter contas da empresa
    contas = ContaJuridica.objects.filter(empresa=empresa_selecionada, usuario=request.user)
    saldo_total = contas.aggregate(total=Sum('saldo'))['total'] or 0
    
    # Obter transações recentes
    transacoes_recentes = TransacaoJuridica.objects.filter(
        empresa=empresa_selecionada, 
        usuario=request.user
    ).order_by('-data')[:10]
    
    # Calcular receitas e despesas do mês atual
    hoje = timezone.now().date()
    primeiro_dia_mes = hoje.replace(day=1)
    ultimo_dia_mes = (primeiro_dia_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    receitas_mes = TransacaoJuridica.objects.filter(
        empresa=empresa_selecionada,
        usuario=request.user,
        tipo='R',
        data__range=[primeiro_dia_mes, ultimo_dia_mes]
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    despesas_mes = TransacaoJuridica.objects.filter(
        empresa=empresa_selecionada,
        usuario=request.user,
        tipo='D',
        data__range=[primeiro_dia_mes, ultimo_dia_mes]
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    # Impostos pendentes
    impostos_pendentes = Imposto.objects.filter(
        empresa=empresa_selecionada,
        usuario=request.user,
        status=False,
        data_vencimento__gte=hoje
    ).order_by('data_vencimento')[:5]
    
    # Impostos vencidos
    impostos_vencidos = Imposto.objects.filter(
        empresa=empresa_selecionada,
        usuario=request.user,
        status=False,
        data_vencimento__lt=hoje
    ).order_by('data_vencimento')[:5]
    
    # Impostos do mês
    impostos_mes = Imposto.objects.filter(
        empresa=empresa_selecionada,
        usuario=request.user,
        data_vencimento__range=[primeiro_dia_mes, ultimo_dia_mes]
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    # Dados para o gráfico de despesas por categoria
    categorias_despesas = CategoriaJuridica.objects.filter(empresa=empresa_selecionada, usuario=request.user, tipo='D')
    dados_categorias = []
    
    for categoria in categorias_despesas:
        total = TransacaoJuridica.objects.filter(
            empresa=empresa_selecionada,
            usuario=request.user,
            categoria=categoria,
            tipo='D',
            data__range=[primeiro_dia_mes, ultimo_dia_mes]
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        if total > 0:
            dados_categorias.append({
                'categoria': categoria.nome,
                'valor': total
            })
    
    # Dados para o gráfico mensal (últimos 6 meses)
    dados_mensais = []
    for i in range(5, -1, -1):
        data_inicio = (hoje.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        data_fim = (data_inicio.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        
        receitas = TransacaoJuridica.objects.filter(
            empresa=empresa_selecionada,
            usuario=request.user,
            tipo='R',
            data__range=[data_inicio, data_fim]
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        despesas = TransacaoJuridica.objects.filter(
            empresa=empresa_selecionada,
            usuario=request.user,
            tipo='D',
            data__range=[data_inicio, data_fim]
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        dados_mensais.append({
            'mes': data_inicio.strftime('%b/%Y'),
            'receitas': receitas,
            'despesas': despesas
        })
    
    context = {
        'empresa_selecionada': empresa_selecionada,
        'empresas': empresas,
        'contas': contas,
        'saldo_total': saldo_total,
        'transacoes_recentes': transacoes_recentes,
        'receitas_mes': receitas_mes,
        'despesas_mes': despesas_mes,
        'saldo_mes': receitas_mes - despesas_mes,
        'impostos_pendentes': impostos_pendentes,
        'impostos_vencidos': impostos_vencidos,
        'impostos_mes': impostos_mes,
        'dados_categorias': dados_categorias,
        'dados_mensais': dados_mensais,
        'mes_atual': hoje.strftime('%B/%Y'),
        'view_type': 'juridico'
    }
    
    return render(request, 'financas_juridicas/dashboard.html', context)

@login_required
def selecionar_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id, usuario=request.user)
    request.session['empresa_ativa'] = empresa.id
    return redirect('dashboard_juridico')

# Views para Empresas
@login_required
def lista_empresas(request):
    empresas = Empresa.objects.filter(usuario=request.user)
    return render(request, 'financas_juridicas/empresas/lista.html', {'empresas': empresas, 'view_type': 'juridico'})

@login_required
def criar_empresa(request):
    if request.method == 'POST':
        form = EmpresaForm(request.POST)
        if form.is_valid():
            empresa = form.save(commit=False)
            empresa.usuario = request.user
            empresa.save()
            messages.success(request, 'Empresa cadastrada com sucesso!')
            return redirect('lista_empresas')
    else:
        form = EmpresaForm()
    
    return render(request, 'financas_juridicas/empresas/form.html', {'form': form, 'view_type': 'juridico'})

@login_required
def editar_empresa(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        form = EmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empresa atualizada com sucesso!')
            return redirect('lista_empresas')
    else:
        form = EmpresaForm(instance=empresa)
    
    return render(request, 'financas_juridicas/empresas/form.html', {'form': form, 'view_type': 'juridico'})

@login_required
def excluir_empresa(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        empresa.delete()
        messages.success(request, 'Empresa excluída com sucesso!')
        return redirect('lista_empresas')
    
    return render(request, 'financas_juridicas/empresas/confirmar_exclusao.html', {'empresa': empresa, 'view_type': 'juridico'})

# Views para Categorias Jurídicas
@login_required
def lista_categorias_juridicas(request):
    # Obter empresa ativa
    empresa_id = request.session.get('empresa_ativa')
    if not empresa_id:
        messages.warning(request, 'Selecione uma empresa primeiro.')
        return redirect('lista_empresas')
    
    empresa = get_object_or_404(Empresa, id=empresa_id, usuario=request.user)
    categorias = CategoriaJuridica.objects.filter(empresa=empresa, usuario=request.user)
    
    context = {
        'categorias': categorias,
        'empresa': empresa,
        'view_type': 'juridico'
    }
    
    return render(request, 'financas_juridicas/categorias/lista.html', context)

@login_required
def criar_categoria_juridica(request):
    # Obter empresa ativa
    empresa_id = request.session.get('empresa_ativa')
    if not empresa_id:
        messages.warning(request, 'Selecione uma empresa primeiro.')
        return redirect('lista_empresas')
    
    empresa = get_object_or_404(Empresa, id=empresa_id, usuario=request.user)
    
    if request.method == 'POST':
        form = CategoriaJuridicaForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.empresa = empresa
            categoria.usuario = request.user
            categoria.save()
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('lista_categorias_juridicas')
    else:
        form = CategoriaJuridicaForm()
    
    context = {
        'form': form,
        'empresa': empresa,
        'view_type': 'juridico'
    }
    
    return render(request, 'financas_juridicas/categorias/form.html', context)

@login_required
def editar_categoria_juridica(request, pk):
    categoria = get_object_or_404(CategoriaJuridica, pk=pk, usuario=request.user)
    empresa = categoria.empresa
    
    if request.method == 'POST':
        form = CategoriaJuridicaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('lista_categorias_juridicas')
    else:
        form = CategoriaJuridicaForm(instance=categoria)
    
    context = {
        'form': form,
        'empresa': empresa,
        'view_type': 'juridico'
    }
    
    return render(request, 'financas_juridicas/categorias/form.html', context)

@login_required
def excluir_categoria_juridica(request, pk):
    categoria = get_object_or_404(CategoriaJuridica, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoria excluída com sucesso!')
        return redirect('lista_categorias_juridicas')
    
    return render(request, 'financas_juridicas/categorias/confirmar_exclusao.html', {'categoria': categoria, 'view_type': 'juridico'})

# Views para Contas Jurídicas
@login_required
def lista_contas_juridicas(request):
    # Obter empresa ativa
    empresa_id = request.session.get('empresa_ativa')
    if not empresa_id:
        messages.warning(request, 'Selecione uma empresa primeiro.')
        return redirect('lista_empresas')
    
    empresa = get_object_or_404(Empresa, id=empresa_id, usuario=request.user)
    contas = ContaJuridica.objects.filter(empresa=empresa, usuario=request.user)
    saldo_total = contas.aggregate(total=Sum('saldo'))['total'] or 0
    
    context = {
        'contas': contas,
        'empresa': empresa,
        'saldo_total': saldo_total,
        'view_type': 'juridico'
    }
    
    return render(request, 'financas_juridicas/contas/lista.html', context)

@login_required
def criar_conta_juridica(request):
    # Obter empresa ativa
    empresa_id = request.session.get('empresa_ativa')
    if not empresa_id:
        messages.warning(request, 'Selecione uma empresa primeiro.')
        return redirect('lista_empresas')
    
    empresa = get_object_or_404(Empresa, id=empresa_id, usuario=request.user)
    
    if request.method == 'POST':
        form = ContaJuridicaForm(request.POST)
        if form.is_valid():
            conta = form.save(commit=False)
            conta.empresa = empresa
            conta.usuario = request.user
            conta.save()
            messages.success(request, 'Conta criada com sucesso!')
            return redirect('lista_contas_juridicas')
    else:
        form = ContaJuridicaForm()
    
    context = {
        'form': form,
        'empresa': empresa,
        'view_type': 'juridico'
    }
    
    return render(request, 'financas_juridicas/contas/form.html', context)

@login_required
def editar_conta_juridica(request, pk):
    conta = get_object_or_404(ContaJuridica, pk=pk, usuario=request.user)
    empresa = conta.empresa
    
    if request.method == 'POST':
        form = ContaJuridicaForm(request.POST, instance=conta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conta atualizada com sucesso!')
            return redirect('lista_contas_juridicas')
    else:
        form = ContaJuridicaForm(instance=conta)
    
    context = {
        'form': form,
        'empresa': empresa,
        'view_type': 'juridico'
    }
    
    return render(request, 'financas_juridicas/contas/form.html', context)

@login_required
def excluir_conta_juridica(request, pk):
    conta = get_object_or_404(ContaJuridica, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        conta.delete()
        messages.success(request, 'Conta excluída com sucesso!')
        return redirect('lista_contas_juridicas')
    
    return render(request, 'financas_juridicas/contas/confirmar_exclusao.html', {'conta': conta, 'view_type': 'juridico'})

# Views para Transações Jurídicas
@login_required
def lista_transacoes_juridicas(request):
    # Obter empresa ativa
    empresa_id = request.session.get('empresa_ativa')
    if not empresa_id:
        messages.warning(request, 'Selecione uma empresa primeiro.')
        return redirect('lista_empresas')
    
    empresa = get_object_or_404(Empresa, id=empresa_id, usuario=request.user)
    transacoes = TransacaoJuridica.objects.filter(empresa=empresa, usuario=request.user)
    
    # Filtros
    categoria_id = request.GET.get('categoria')
    conta_id = request.GET.get('conta')
    tipo = request.GET.get('tipo')
    metodo_pagamento = request.GET.get('metodo_pagamento')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    if categoria_id:
        transacoes = transacoes.filter(categoria_id=categoria_id)
    
    if conta_id:
        transacoes = transacoes.filter(conta_id=conta_id)
    
    if tipo:
        transacoes = transacoes.filter(tipo=tipo)
    
    if metodo_pagamento:
        transacoes = transacoes.filter(metodo_pagamento=metodo_pagamento)
    
    if data_inicio:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        transacoes = transacoes.filter(data__gte=data_inicio)
    
    if data_fim:
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        transacoes = transacoes.filter(data__lte=data_fim)
    
    # Ordenação
    transacoes = transacoes.order_by('-data')
    
    # Dados para filtros
    categorias = CategoriaJuridica.objects.filter(empresa=empresa, usuario=request.user)
    contas = ContaJuridica.objects.filter(empresa=empresa, usuario=request.user)
    
    context = {
        'transacoes': transacoes,
        'categorias': categorias,
        'contas': contas,
        'empresa': empresa,
        'view_type': 'juridico'
    }
    
    return render(request, 'financas_juridicas/transacoes/lista.html', context)

@login_required
def criar_transacao_juridica(request):
    # Obter empresa ativa
    empresa_id = request.session.get('empresa_ativa')
    if not empresa_id:
        messages.warning(request, 'Selecione uma empresa primeiro.')
        return redirect('lista_empresas')
    
    empresa = get_object_or_404(Empresa, id=empresa_id, usuario=request.user)
    
    if request.method == 'POST':
        form = TransacaoJuridicaForm(request.POST, empresa=empresa, user=request.user)
        if form.is_valid():
            transacao = form.save(commit=False)
            transacao.empresa = empresa
            transacao.usuario = request.user
            transacao.save()
            messages.success(request, 'Transação registrada com sucesso!')
            return redirect('lista_transacoes_juridicas')
    else:
        # Pré-selecionar o tipo de transação com base no parâmetro da URL
        tipo = request.GET.get('tipo')
        initial_data = {}
        if tipo in ['R', 'D', 'T']:
            initial_data['tipo'] = tipo
        form = TransacaoJuridicaForm(empresa=empresa, user=request.user, initial=initial_data)
    
    context = {
        'form': form,
        'empresa': empresa,
        'view_type': 'juridico'
    }
    
    return render(request, 'financas_juridicas/transacoes/form.html', context)

@login_required
def editar_transacao_juridica(request, pk):
    transacao = get_object_or_404(TransacaoJuridica, pk=pk, usuario=request.user)
    empresa = transacao.empresa
    
    if request.method == 'POST':
        form = TransacaoJuridicaForm(request.POST, instance=transacao, empresa=empresa, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transação atualizada com sucesso!')
            return redirect('lista_transacoes_juridicas')
    else:
        form = TransacaoJuridicaForm(instance=transacao, empresa=empresa, user=request.user)
    
    context = {
        'form': form,
        'empresa': empresa,
        'view_type': 'juridico'
    }
    
    return render(request, 'financas_juridicas/transacoes/form.html', context)

@login_required
def excluir_transacao_juridica(request, pk):
    transacao = get_object_or_404(TransacaoJuridica, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        # Reverter o efeito da transação no saldo da conta
        if transacao.tipo == 'R':  # Receita
            transacao.conta.saldo -= transacao.valor
            transacao.conta.save()
        elif transacao.tipo == 'D':  # Despesa
            transacao.conta.saldo += transacao.valor
            transacao.conta.save()
        elif transacao.tipo == 'T' and transacao.conta_destino:  # Transferência
            transacao.conta.saldo += transacao.valor
            transacao.conta_destino.saldo -= transacao.valor
            transacao.conta.save()
            transacao.conta_destino.save()
        
        transacao.delete()
        messages.success(request, 'Transação excluída com sucesso!')
        return redirect('lista_transacoes_juridicas')
    
    return render(request, 'financas_juridicas/transacoes/confirmar_exclusao.html', {'transacao': transacao, 'view_type': 'juridico'})

# Views para Impostos
@login_required
def lista_impostos(request):
    # Obter empresa ativa
    empresa_id = request.session.get('empresa_ativa')
    if not empresa_id:
        messages.warning(request, 'Selecione uma empresa primeiro.')
        return redirect('lista_empresas')
    
    empresa = get_object_or_404(Empresa, id=empresa_id, usuario=request.user)
    impostos = Imposto.objects.filter(empresa=empresa, usuario=request.user)
    
    # Filtros
    status = request.GET.get('status')
    nome = request.GET.get('nome')
    periodo = request.GET.get('periodo')
    
    if status:
        if status == 'pago':
            impostos = impostos.filter(status=True)
        elif status == 'pendente':
            impostos = impostos.filter(status=False)
    
    if nome:
        impostos = impostos.filter(nome=nome)
    
    if periodo:
        impostos = impostos.filter(periodo_referencia=periodo)
    
    # Ordenação
    impostos = impostos.order_by('status', 'data_vencimento')
    
    context = {
        'impostos': impostos,
        'empresa': empresa,
        'view_type': 'juridico'
    }
    
    return render(request, 'financas_juridicas/impostos/lista.html', context)

@login_required
def criar_imposto(request):
    # Obter empresa ativa
    empresa_id = request.session.get('empresa_ativa')
    if not empresa_id:
        messages.warning(request, 'Selecione uma empresa primeiro.')
        return redirect('lista_empresas')
    
    empresa = get_object_or_404(Empresa, id=empresa_id, usuario=request.user)
    
    if request.method == 'POST':
        form = ImpostoForm(request.POST)
        if form.is_valid():
            imposto = form.save(commit=False)
            imposto.empresa = empresa
            imposto.usuario = request.user
            imposto.save()
            messages.success(request, 'Imposto registrado com sucesso!')
            return redirect('lista_impostos')
    else:
        form = ImpostoForm()
    
    context = {
        'form': form,
        'empresa': empresa,
        'view_type': 'juridico'
    }
    
    return render(request, 'financas_juridicas/impostos/form.html', context)

@login_required
def editar_imposto(request, pk):
    imposto = get_object_or_404(Imposto, pk=pk, usuario=request.user)
    empresa = imposto.empresa
    
    if request.method == 'POST':
        form = ImpostoForm(request.POST, instance=imposto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Imposto atualizado com sucesso!')
            return redirect('lista_impostos')
    else:
        form = ImpostoForm(instance=imposto)
    
    context = {
        'form': form,
        'empresa': empresa,
        'view_type': 'juridico'
    }
    
    return render(request, 'financas_juridicas/impostos/form.html', context)

@login_required
def excluir_imposto(request, pk):
    imposto = get_object_or_404(Imposto, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        imposto.delete()
        messages.success(request, 'Imposto excluído com sucesso!')
        return redirect('lista_impostos')
    
    return render(request, 'financas_juridicas/impostos/confirmar_exclusao.html', {'imposto': imposto, 'view_type': 'juridico'})

@login_required
def marcar_imposto_pago(request, pk):
    imposto = get_object_or_404(Imposto, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        imposto.status = True
        imposto.data_pagamento = timezone.now().date()
        imposto.save()
        messages.success(request, 'Imposto marcado como pago!')
        return redirect('lista_impostos')
    
    return render(request, 'financas_juridicas/impostos/confirmar_pagamento.html', {'imposto': imposto, 'view_type': 'juridico'})

@login_required
def relatorio_por_periodo_juridico(request):
    hoje = timezone.now().date()
    primeiro_dia_mes = hoje.replace(day=1)
    ultimo_dia_mes = (primeiro_dia_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    data_inicio = request.GET.get('data_inicio', primeiro_dia_mes.strftime('%Y-%m-%d'))
    data_fim = request.GET.get('data_fim', ultimo_dia_mes.strftime('%Y-%m-%d'))

    try:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
    except ValueError:
        data_inicio = primeiro_dia_mes
        data_fim = ultimo_dia_mes

    transacoes = TransacaoJuridica.objects.filter(
        empresa=empresa_selecionada,
        usuario=request.user,
        data__range=[data_inicio, data_fim]
    ).order_by('data')

    total_receitas = transacoes.filter(tipo='R').aggregate(total=Sum('valor'))['total'] or 0
    total_despesas = transacoes.filter(tipo='D').aggregate(total=Sum('valor'))['total'] or 0
    saldo_periodo = total_receitas - total_despesas

    context = {
        'transacoes': transacoes,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'total_receitas': total_receitas,
        'total_despesas': total_despesas,
        'saldo_periodo': saldo_periodo,
        'view_type': 'juridico',
    }

    return render(request, 'financas_juridicas/relatorios/por_periodo.html', context)

@login_required
def relatorio_por_categoria_juridico(request):
    hoje = timezone.now().date()
    primeiro_dia_mes = hoje.replace(day=1)
    ultimo_dia_mes = (primeiro_dia_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    data_inicio = request.GET.get('data_inicio', primeiro_dia_mes.strftime('%Y-%m-%d'))
    data_fim = request.GET.get('data_fim', ultimo_dia_mes.strftime('%Y-%m-%d'))
    tipo_transacao = request.GET.get('tipo', 'D')

    try:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
    except ValueError:
        data_inicio = primeiro_dia_mes
        data_fim = ultimo_dia_mes

    transacoes_por_categoria = TransacaoJuridica.objects.filter(
        empresa=empresa_selecionada,
        usuario=request.user,
        tipo=tipo_transacao,
        data__range=[data_inicio, data_fim],
        categoria__isnull=False
    ).values('categoria__nome', 'categoria__cor').annotate(
        total=Sum('valor')
    ).order_by('-total')

    total_geral = sum(item['total'] for item in transacoes_por_categoria)

    for item in transacoes_por_categoria:
        if total_geral > 0:
            item['percentual'] = (item['total'] / total_geral) * 100
        else:
            item['percentual'] = 0

    context = {
        'transacoes_por_categoria': transacoes_por_categoria,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'tipo_transacao': tipo_transacao,
        'total_geral': total_geral,
        'view_type': 'juridico',
    }

    return render(request, 'financas_juridicas/relatorios/por_categoria.html', context)
