from datetime import datetime, timedelta
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from django.http import HttpResponse
import csv
import io
from .models import Categoria, Conta, Transacao
from .forms import CategoriaForm, ContaForm, TransacaoForm, FiltroTransacaoForm

# Configurar logger
logger = logging.getLogger(__name__)

@login_required
def dashboard(request):
    # Obter contas do usuário
    contas = Conta.objects.filter(usuario=request.user)
    total_contas = contas.aggregate(total=Sum('saldo'))['total'] or 0
    
    # Obter data do primeiro e último dia do mês atual
    hoje = timezone.now().date()
    primeiro_dia_mes = hoje.replace(day=1)
    if hoje.month == 12:
        ultimo_dia_mes = hoje.replace(year=hoje.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        ultimo_dia_mes = hoje.replace(month=hoje.month + 1, day=1) - timedelta(days=1)
    
    # Adicionando logs para depuração
    logger.debug(f"Primeiro dia do mês: {primeiro_dia_mes}")
    logger.debug(f"Último dia do mês: {ultimo_dia_mes}")
    
    # Calcular receitas e despesas do mês atual
    receitas_mes = Transacao.objects.filter(
        usuario=request.user,
        tipo='R',
        data__range=[primeiro_dia_mes, ultimo_dia_mes]
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    despesas_mes = Transacao.objects.filter(
        usuario=request.user,
        tipo='D',
        data__range=[primeiro_dia_mes, ultimo_dia_mes]
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    # Adicionando logs para depuração
    logger.debug(f"Receitas do mês: {receitas_mes}")
    logger.debug(f"Despesas do mês: {despesas_mes}")
    logger.debug(f"Número de transações de receita: {Transacao.objects.filter(usuario=request.user, tipo='R', data__gte=primeiro_dia_mes, data__lte=ultimo_dia_mes).count()}")
    logger.debug(f"Número de transações de despesa: {Transacao.objects.filter(usuario=request.user, tipo='D', data__gte=primeiro_dia_mes, data__lte=ultimo_dia_mes).count()}")
    
    # Calcular saldo do mês
    saldo_mes = receitas_mes - despesas_mes
    
    # Obter transações recentes
    transacoes_recentes = Transacao.objects.filter(
        usuario=request.user
    ).order_by('-data')[:5]
    
    # Obter despesas por categoria
    despesas_por_categoria = Transacao.objects.filter(
        usuario=request.user,
        tipo='D',
        data__gte=primeiro_dia_mes,
        data__lte=ultimo_dia_mes,
        categoria__isnull=False
    ).values('categoria__nome', 'categoria__cor').annotate(
        total=Sum('valor')
    ).order_by('-total')
    
    # Calcular percentual de cada categoria em relação ao total de despesas
    for despesa in despesas_por_categoria:
        if despesas_mes > 0:
            despesa['percentual'] = (despesa['total'] / despesas_mes) * 100
        else:
            despesa['percentual'] = 0
    
    context = {
        'contas': contas,
        'total_contas': total_contas,
        'receitas_mes': receitas_mes,
        'despesas_mes': despesas_mes,
        'saldo_mes': saldo_mes,
        'transacoes_recentes': transacoes_recentes,
        'despesas_por_categoria': despesas_por_categoria,
        'mes_atual': hoje.strftime('%B %Y'),
        'view_type': 'pessoal',
        'hide_back_button': True,  # Ocultar o botão de voltar no dashboard
    }
    
    return render(request, 'financas_pessoais/dashboard.html', context)

# Views para Categorias
@login_required
def lista_categorias(request):
    categorias = Categoria.objects.filter(usuario=request.user)
    return render(request, 'financas_pessoais/categorias/lista.html', {'categorias': categorias, 'view_type': 'pessoal'})

@login_required
def criar_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.usuario = request.user
            categoria.save()
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('lista_categorias')
    else:
        form = CategoriaForm()
    
    return render(request, 'financas_pessoais/categorias/form.html', {'form': form, 'view_type': 'pessoal'})

@login_required
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('lista_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    
    return render(request, 'financas_pessoais/categorias/form.html', {'form': form, 'view_type': 'pessoal'})

@login_required
def excluir_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoria excluída com sucesso!')
        return redirect('lista_categorias')
    
    return render(request, 'financas_pessoais/categorias/confirmar_exclusao.html', {'categoria': categoria, 'view_type': 'pessoal'})

# Views para Contas
@login_required
def lista_contas(request):
    contas = Conta.objects.filter(usuario=request.user)
    total = contas.aggregate(total=Sum('saldo'))['total'] or 0
    return render(request, 'financas_pessoais/contas/lista.html', {'contas': contas, 'total': total, 'view_type': 'pessoal'})

@login_required
def criar_conta(request):
    if request.method == 'POST':
        form = ContaForm(request.POST)
        if form.is_valid():
            conta = form.save(commit=False)
            conta.usuario = request.user
            conta.save()
            messages.success(request, 'Conta criada com sucesso!')
            return redirect('lista_contas')
    else:
        form = ContaForm()
    
    return render(request, 'financas_pessoais/contas/form.html', {'form': form, 'view_type': 'pessoal'})

@login_required
def editar_conta(request, pk):
    conta = get_object_or_404(Conta, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        form = ContaForm(request.POST, instance=conta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conta atualizada com sucesso!')
            return redirect('lista_contas')
    else:
        form = ContaForm(instance=conta)
    
    return render(request, 'financas_pessoais/contas/form.html', {'form': form, 'view_type': 'pessoal'})

@login_required
def excluir_conta(request, pk):
    conta = get_object_or_404(Conta, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        conta.delete()
        messages.success(request, 'Conta excluída com sucesso!')
        return redirect('lista_contas')
    
    return render(request, 'financas_pessoais/contas/confirmar_exclusao.html', {'conta': conta, 'view_type': 'pessoal'})

# Views para Transações
@login_required
def lista_transacoes(request):
    form = FiltroTransacaoForm(request.GET, usuario=request.user)
    
    # Iniciar com todas as transações do usuário
    transacoes = Transacao.objects.filter(usuario=request.user)
    
    # Aplicar filtros se o formulário for válido
    if form.is_valid():
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')
        tipo = form.cleaned_data.get('tipo')
        categoria = form.cleaned_data.get('categoria')
        conta = form.cleaned_data.get('conta')
        
        if data_inicio:
            transacoes = transacoes.filter(data__gte=data_inicio)
        
        if data_fim:
            transacoes = transacoes.filter(data__lte=data_fim)
        
        if tipo:
            transacoes = transacoes.filter(tipo=tipo)
        
        if categoria:
            transacoes = transacoes.filter(categoria=categoria)
        
        if conta:
            transacoes = transacoes.filter(Q(conta=conta) | Q(conta_destino=conta))
    
    # Ordenar por data decrescente
    transacoes = transacoes.order_by('-data')
    
    # Calcular totais
    total_receitas = transacoes.filter(tipo='R').aggregate(total=Sum('valor'))['total'] or 0
    total_despesas = transacoes.filter(tipo='D').aggregate(total=Sum('valor'))['total'] or 0
    saldo = total_receitas - total_despesas
    
    context = {
        'transacoes': transacoes,
        'form': form,
        'total_receitas': total_receitas,
        'total_despesas': total_despesas,
        'saldo': saldo,
        'view_type': 'pessoal',
    }
    
    return render(request, 'financas_pessoais/transacoes/lista.html', context)

@login_required
def criar_transacao(request):
    if request.method == 'POST':
        form = TransacaoForm(request.POST, usuario=request.user)
        if form.is_valid():
            transacao = form.save(commit=False)
            transacao.usuario = request.user
            transacao.save()
            messages.success(request, 'Transação registrada com sucesso!')
            return redirect('lista_transacoes')
    else:
        # Pré-selecionar o tipo de transação com base no parâmetro da URL
        tipo = request.GET.get('tipo')
        initial_data = {}
        if tipo in ['R', 'D', 'T']:
            initial_data['tipo'] = tipo
        form = TransacaoForm(usuario=request.user, initial=initial_data)
    
    context = {
        'form': form,
        'titulo': 'Nova Transação',
        'view_type': 'pessoal'
    }
    
    return render(request, 'financas_pessoais/criar_transacao.html', context)

@login_required
def editar_transacao(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        form = TransacaoForm(request.POST, instance=transacao, usuario=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transação atualizada com sucesso!')
            return redirect('lista_transacoes')
    else:
        form = TransacaoForm(instance=transacao, usuario=request.user)
    
    return render(request, 'financas_pessoais/transacoes/form.html', {'form': form, 'view_type': 'pessoal'})

@login_required
def excluir_transacao(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk, usuario=request.user)
    
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
            transacao.conta.save()
            transacao.conta_destino.saldo -= transacao.valor
            transacao.conta_destino.save()
        
        transacao.delete()
        messages.success(request, 'Transação excluída com sucesso!')
        return redirect('lista_transacoes')
    
    return render(request, 'financas_pessoais/transacoes/confirmar_exclusao.html', {'transacao': transacao, 'view_type': 'pessoal'})

@login_required
def relatorios(request):
    return render(request, 'financas_pessoais/relatorios/index.html', {'view_type': 'pessoal'})

@login_required
def relatorio_por_periodo(request):
    # Definir período padrão (mês atual)
    hoje = timezone.now().date()
    primeiro_dia_mes = hoje.replace(day=1)
    if hoje.month == 12:
        ultimo_dia_mes = hoje.replace(year=hoje.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        ultimo_dia_mes = hoje.replace(month=hoje.month + 1, day=1) - timedelta(days=1)
    
    # Obter parâmetros do formulário
    data_inicio = request.GET.get('data_inicio', primeiro_dia_mes.strftime('%Y-%m-%d'))
    data_fim = request.GET.get('data_fim', ultimo_dia_mes.strftime('%Y-%m-%d'))
    
    # Converter para objetos date
    try:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
    except ValueError:
        data_inicio = primeiro_dia_mes
        data_fim = ultimo_dia_mes
    
    # Obter transações no período
    transacoes = Transacao.objects.filter(
        usuario=request.user,
        data__gte=data_inicio,
        data__lte=data_fim
    ).order_by('data')
    
    # Calcular totais
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
        'view_type': 'pessoal',
    }
    
    return render(request, 'financas_pessoais/relatorios/por_periodo.html', context)

@login_required
def relatorio_por_categoria(request):
    # Definir período padrão (mês atual)
    hoje = timezone.now().date()
    primeiro_dia_mes = hoje.replace(day=1)
    if hoje.month == 12:
        ultimo_dia_mes = hoje.replace(year=hoje.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        ultimo_dia_mes = hoje.replace(month=hoje.month + 1, day=1) - timedelta(days=1)
    
    # Obter parâmetros do formulário
    data_inicio = request.GET.get('data_inicio', primeiro_dia_mes.strftime('%Y-%m-%d'))
    data_fim = request.GET.get('data_fim', ultimo_dia_mes.strftime('%Y-%m-%d'))
    tipo_transacao = request.GET.get('tipo', 'D')  # Padrão: Despesas
    
    # Converter para objetos date
    try:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
    except ValueError:
        data_inicio = primeiro_dia_mes
        data_fim = ultimo_dia_mes
    
    # Obter transações por categoria
    transacoes_por_categoria = Transacao.objects.filter(
        usuario=request.user,
        tipo=tipo_transacao,
        data__gte=data_inicio,
        data__lte=data_fim,
        categoria__isnull=False
    ).values('categoria__nome', 'categoria__cor').annotate(
        total=Sum('valor')
    ).order_by('-total')
    
    # Calcular total geral
    total_geral = sum(item['total'] for item in transacoes_por_categoria)
    
    # Calcular percentual de cada categoria
    for item in transacoes_por_categoria:
        if total_geral > 0:
            item['percentual'] = (item['total'] / total_geral) * 100
        else:
            item['percentual'] = 0
    
    # Obter detalhes das transações por categoria
    categorias = {}
    for item in transacoes_por_categoria:
        categoria_nome = item['categoria__nome']
        categorias[categoria_nome] = Transacao.objects.filter(
            usuario=request.user,
            tipo=tipo_transacao,
            data__gte=data_inicio,
            data__lte=data_fim,
            categoria__nome=categoria_nome
        ).order_by('data')
    
    context = {
        'transacoes_por_categoria': transacoes_por_categoria,
        'categorias': categorias,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'tipo_transacao': tipo_transacao,
        'total_geral': total_geral,
        'view_type': 'pessoal',
    }
    
    return render(request, 'financas_pessoais/relatorios/por_categoria.html', context)

@login_required
def exportar_transacoes_csv(request):
    # Obter parâmetros do formulário
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    # Converter para objetos date
    try:
        if data_inicio:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        if data_fim:
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
    except ValueError:
        # Em caso de erro, usar o mês atual
        hoje = timezone.now().date()
        data_inicio = hoje.replace(day=1)
        if hoje.month == 12:
            data_fim = hoje.replace(year=hoje.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            data_fim = hoje.replace(month=hoje.month + 1, day=1) - timedelta(days=1)
    
    # Obter transações no período
    transacoes = Transacao.objects.filter(
        usuario=request.user
    )
    
    if data_inicio:
        transacoes = transacoes.filter(data__gte=data_inicio)
    
    if data_fim:
        transacoes = transacoes.filter(data__lte=data_fim)
    
    # Ordenar por data
    transacoes = transacoes.order_by('data')
    
    # Criar arquivo CSV em memória
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Escrever cabeçalho
    writer.writerow(['Data', 'Descrição', 'Valor', 'Tipo', 'Categoria', 'Conta', 'Conta Destino', 'Observação'])
    
    # Escrever dados
    for transacao in transacoes:
        tipo_texto = dict(Transacao.TIPO_CHOICES).get(transacao.tipo, '')
        categoria_nome = transacao.categoria.nome if transacao.categoria else ''
        conta_destino_nome = transacao.conta_destino.nome if transacao.conta_destino else ''
        
        writer.writerow([
            transacao.data.strftime('%d/%m/%Y'),
            transacao.descricao,
            str(transacao.valor).replace('.', ','),
            tipo_texto,
            categoria_nome,
            transacao.conta.nome,
            conta_destino_nome,
            transacao.observacao or ''
        ])
    
    # Configurar resposta HTTP
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transacoes.csv"'
    
    return response

# Views para Metas - Comentadas pois o modelo Meta foi removido
'''
@login_required
def lista_metas(request):
    metas = Meta.objects.filter(usuario=request.user)
    
    # Estatísticas
    total_metas = metas.count()
    metas_concluidas = sum(1 for meta in metas if meta.concluida)
    metas_atrasadas = sum(1 for meta in metas if meta.atrasada)
    metas_em_andamento = total_metas - metas_concluidas - metas_atrasadas
    
    porcentagem_concluidas = 0
    if total_metas > 0:
        porcentagem_concluidas = (metas_concluidas / total_metas) * 100
    
    context = {
        'metas': metas,
        'total_metas': total_metas,
        'metas_concluidas': metas_concluidas,
        'metas_atrasadas': metas_atrasadas,
        'metas_em_andamento': metas_em_andamento,
        'porcentagem_concluidas': porcentagem_concluidas,
    }
    return render(request, 'financas_pessoais/metas/lista.html', context)

@login_required
def criar_meta(request):
    if request.method == 'POST':
        form = MetaForm(request.POST, usuario=request.user)
        if form.is_valid():
            meta = form.save(commit=False)
            meta.usuario = request.user
            meta.save()
            messages.success(request, 'Meta criada com sucesso!')
            return redirect('lista_metas')
    else:
        form = MetaForm(usuario=request.user)
    
    return render(request, 'financas_pessoais/metas/form.html', {'form': form})

@login_required
def editar_meta(request, pk):
    meta = get_object_or_404(Meta, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        form = MetaForm(request.POST, instance=meta, usuario=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Meta atualizada com sucesso!')
            return redirect('lista_metas')
    else:
        form = MetaForm(instance=meta, usuario=request.user)
    
    return render(request, 'financas_pessoais/metas/form.html', {'form': form})

@login_required
def atualizar_meta(request, pk):
    meta = get_object_or_404(Meta, pk=pk, usuario=request.user)
    historico = HistoricoMeta.objects.filter(meta=meta).order_by('-data_atualizacao')
    
    if request.method == 'POST':
        form = AtualizarMetaForm(request.POST)
        if form.is_valid():
            valor_anterior = meta.valor_atual
            valor_novo = form.cleaned_data['valor_atual']
            observacao = form.cleaned_data['observacao']
            
            # Registrar no histórico
            HistoricoMeta.objects.create(
                meta=meta,
                valor_anterior=valor_anterior,
                valor_novo=valor_novo,
                observacao=observacao
            )
            
            # Atualizar o valor atual da meta
            meta.valor_atual = valor_novo
            meta.save()
            
            messages.success(request, 'Progresso da meta atualizado com sucesso!')
            return redirect('lista_metas')
    else:
        form = AtualizarMetaForm(initial={'valor_atual': meta.valor_atual})
    
    context = {
        'meta': meta,
        'form': form,
        'historico': historico,
    }
    return render(request, 'financas_pessoais/metas/atualizar.html', context)

@login_required
def excluir_meta(request, pk):
    meta = get_object_or_404(Meta, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        meta.delete()
        messages.success(request, 'Meta excluída com sucesso!')
        return redirect('lista_metas')
    
    return render(request, 'financas_pessoais/metas/excluir.html', {'meta': meta})
'''
