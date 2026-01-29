from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from decimal import Decimal
from mensalidades.models import Mensalidade
from .models import Pagamento, MovimentacaoCaixa, AberturaCaixa
from .forms import PagamentoForm, SessaoAvulsaForm, SaidaCaixaForm


def dashboard_caixa(request):
    # Verificar se existe caixa aberto
    caixa_aberto = AberturaCaixa.objects.filter(aberto=True).first()
    
    # Verificar se está consultando um caixa específico
    caixa_id = request.GET.get('caixa_id')
    
    if caixa_id:
        # Consultar caixa específico (histórico)
        caixa_atual = get_object_or_404(AberturaCaixa, id=caixa_id)
        modo_consulta = True
    elif caixa_aberto:
        # Mostrar caixa aberto atual
        caixa_atual = caixa_aberto
        modo_consulta = False
    else:
        # Não há caixa aberto e não está consultando histórico
        caixas_anteriores = AberturaCaixa.objects.filter(aberto=False)[:10]
        context = {
            'sem_caixa_aberto': True,
            'caixas_anteriores': caixas_anteriores,
        }
        return render(request, 'caixa/dashboard.html', context)
    
    # Buscar todas as movimentações deste caixa
    pagamentos = Pagamento.objects.filter(caixa=caixa_atual).select_related(
        'mensalidade__paciente', 'mensalidade__servico'
    )
    
    movimentacoes_caixa = MovimentacaoCaixa.objects.filter(caixa=caixa_atual).select_related('paciente')
    
    # Unir tudo em uma lista
    movimentacoes = []
    
    # Adicionar pagamentos de mensalidades
    for pag in pagamentos:
        movimentacoes.append({
            'data_movimentacao': pag.data_pagamento,
            'descricao': f"Mensalidade - {pag.mensalidade.servico.nome if pag.mensalidade else 'N/A'}",
            'paciente': pag.mensalidade.paciente if pag.mensalidade else None,
            'tipo': 'entrada',
            'valor': pag.valor_pago,
            'get_tipo_display': 'Entrada',
            'metodo': pag.get_metodo_pagamento_display(),
        })
    
    # Adicionar movimentações de caixa
    for mov in movimentacoes_caixa:
        movimentacoes.append({
            'data_movimentacao': mov.data_movimentacao,
            'descricao': mov.descricao,
            'paciente': mov.paciente,
            'tipo': mov.tipo,
            'valor': mov.valor,
            'get_tipo_display': mov.get_tipo_display(),
            'metodo': mov.categoria_entrada if mov.tipo == 'entrada' else mov.categoria_saida,
        })
    
    # Ordenar por data (mais ANTIGA primeiro para calcular saldo progressivo)
    movimentacoes.sort(key=lambda x: x['data_movimentacao'])
    
    # Calcular saldo progressivo
    saldo_atual = caixa_atual.saldo_inicial
    
    for mov in movimentacoes:
        if mov['tipo'] == 'entrada':
            saldo_atual += mov['valor']
        else:  # saida
            saldo_atual -= mov['valor']
        mov['saldo_progressivo'] = saldo_atual
    
    # Inverter para mostrar mais recente primeiro
    movimentacoes.reverse()
    
    # Calcular estatísticas
    total_entradas_pag = pagamentos.aggregate(Sum('valor_pago'))['valor_pago__sum'] or Decimal('0')
    entradas_caixa = movimentacoes_caixa.filter(tipo='entrada').aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
    saidas_caixa = movimentacoes_caixa.filter(tipo='saida').aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
    
    total_entradas = total_entradas_pag + entradas_caixa
    total_saidas = saidas_caixa
    saldo_final = caixa_atual.saldo_inicial + total_entradas - total_saidas
    
    stats = {
        'saldo_inicial': caixa_atual.saldo_inicial,
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
        'saldo': saldo_final,
        'total_movimentacoes': len(movimentacoes),
    }
    
    # Buscar caixas anteriores para o dropdown
    caixas_anteriores = AberturaCaixa.objects.all()[:30]
    
    context = {
        'stats': stats,
        'movimentacoes': movimentacoes,
        'caixa_atual': caixa_atual,
        'caixa_aberto': caixa_aberto,
        'modo_consulta': modo_consulta,
        'caixas_anteriores': caixas_anteriores,
    }
    return render(request, 'caixa/dashboard.html', context)


def abrir_caixa(request):
    # Verificar se já existe caixa aberto
    if AberturaCaixa.objects.filter(aberto=True).exists():
        return redirect('dashboard_caixa')
    
    if request.method == 'POST':
        saldo_inicial = request.POST.get('saldo_inicial', '0')
        
        # Remover separadores de milhar e trocar vírgula por ponto
        saldo_inicial = saldo_inicial.replace('.', '').replace(',', '.')
        
        # Tratar valor vazio
        try:
            saldo_inicial = Decimal(saldo_inicial) if saldo_inicial else Decimal('0')
        except Exception as e:
            print(f"Erro ao converter saldo: {e}")
            saldo_inicial = Decimal('0')
        
        print(f"DEBUG - Salvando caixa com saldo inicial: {saldo_inicial}")  # DEBUG
        
        caixa_novo = AberturaCaixa.objects.create(
            saldo_inicial=saldo_inicial,
            aberto=True
        )
        
        print(f"DEBUG - Caixa criado: {caixa_novo.id}, Saldo: {caixa_novo.saldo_inicial}")  # DEBUG
        
        return redirect('dashboard_caixa')
    
    # Buscar saldo final do último caixa fechado
    ultimo_caixa = AberturaCaixa.objects.filter(aberto=False).order_by('-data_fechamento').first()
    
    saldo_sugerido = ultimo_caixa.saldo_final if ultimo_caixa and ultimo_caixa.saldo_final else Decimal('0')
    
    context = {
        'saldo_sugerido': saldo_sugerido,
        'ultimo_caixa': ultimo_caixa,
    }
    return render(request, 'caixa/abrir_caixa.html', context)

def fechar_caixa(request):
    caixa = AberturaCaixa.objects.filter(aberto=True).first()
    
    if not caixa:
        return redirect('dashboard_caixa')
    
    if request.method == 'POST':
        # Calcular totais
        pagamentos = Pagamento.objects.filter(caixa=caixa)
        movimentacoes = MovimentacaoCaixa.objects.filter(caixa=caixa)
        
        total_entradas_pag = pagamentos.aggregate(Sum('valor_pago'))['valor_pago__sum'] or Decimal('0')
        entradas_caixa = movimentacoes.filter(tipo='entrada').aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
        saidas_caixa = movimentacoes.filter(tipo='saida').aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
        
        caixa.total_entradas = total_entradas_pag + entradas_caixa
        caixa.total_saidas = saidas_caixa
        caixa.saldo_final = caixa.saldo_inicial + caixa.total_entradas - caixa.total_saidas
        caixa.data_fechamento = datetime.now()
        caixa.aberto = False
        caixa.observacoes = request.POST.get('observacoes', '')
        caixa.save()
        
        return redirect('dashboard_caixa')
    
    # Calcular valores para exibir no formulário
    pagamentos = Pagamento.objects.filter(caixa=caixa)
    movimentacoes = MovimentacaoCaixa.objects.filter(caixa=caixa)
    
    total_entradas_pag = pagamentos.aggregate(Sum('valor_pago'))['valor_pago__sum'] or Decimal('0')
    entradas_caixa = movimentacoes.filter(tipo='entrada').aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
    saidas_caixa = movimentacoes.filter(tipo='saida').aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
    
    total_entradas = total_entradas_pag + entradas_caixa
    saldo_final = caixa.saldo_inicial + total_entradas - saidas_caixa
    
    # Contar movimentações
    total_movimentacoes = pagamentos.count() + movimentacoes.count()
    
    context = {
        'caixa': caixa,
        'total_entradas': total_entradas,
        'total_saidas': saidas_caixa,
        'saldo_final': saldo_final,
        'total_movimentacoes': total_movimentacoes,
    }
    
    return render(request, 'caixa/fechar_caixa.html', context)


def registrar_pagamento(request):
    # Verificar se há caixa aberto
    caixa_aberto = AberturaCaixa.objects.filter(aberto=True).first()
    if not caixa_aberto:
        return redirect('abrir_caixa')
    
    mensalidade_id = request.GET.get('mensalidade_id', None)
    
    if request.method == 'POST':
        form = PagamentoForm(request.POST)
        if form.is_valid():
            pagamento = form.save(commit=False)
            pagamento.caixa = caixa_aberto
            pagamento.save()
            
            # Verificar se deve ajustar a próxima mensalidade
            ajustar_proxima = request.POST.get('ajustar_proxima') == 'on'
            mensalidade_atual = pagamento.mensalidade
            valor_mensalidade = mensalidade_atual.valor
            valor_pago = pagamento.valor_pago
            diferenca = valor_pago - valor_mensalidade
            
            if ajustar_proxima and diferenca != 0:
                # Buscar próxima mensalidade pendente do mesmo paciente
                proxima_mensalidade = Mensalidade.objects.filter(
                    paciente=mensalidade_atual.paciente,
                    status__in=['pendente', 'parcial'],
                    data_vencimento__gt=mensalidade_atual.data_vencimento
                ).order_by('data_vencimento').first()
                
                if proxima_mensalidade:
                    if diferenca > 0:
                        # Pagou a mais - abater da próxima
                        proxima_mensalidade.valor -= diferenca
                        mensagem_ajuste = f"Crédito de R$ {diferenca:.2f} aplicado na mensalidade de {proxima_mensalidade.data_vencimento.strftime('%m/%Y')}"
                    else:
                        # Pagou a menos - adicionar na próxima
                        proxima_mensalidade.valor += abs(diferenca)
                        mensagem_ajuste = f"Débito de R$ {abs(diferenca):.2f} adicionado na mensalidade de {proxima_mensalidade.data_vencimento.strftime('%m/%Y')}"
                    
                    proxima_mensalidade.save()
                    messages.success(request, f'Pagamento registrado! {mensagem_ajuste}')
                else:
                    messages.warning(request, f'Pagamento registrado, mas não há próxima mensalidade para ajustar a diferença de R$ {abs(diferenca):.2f}')
            else:
                messages.success(request, 'Pagamento registrado com sucesso!')
            
            return redirect('dashboard_caixa')
    else:
        form = PagamentoForm()
        if mensalidade_id:
            try:
                mensalidade = Mensalidade.objects.get(id=mensalidade_id)
                form.fields['mensalidade'].initial = mensalidade
                form.fields['valor_pago'].initial = mensalidade.valor
            except Mensalidade.DoesNotExist:
                pass
    
    mensalidades_pendentes = Mensalidade.objects.filter(
        status__in=['pendente', 'parcial']
    ).select_related('paciente', 'servico').order_by('paciente__nome', '-data_vencimento')
    
    context = {
        'form': form,
        'mensalidades': mensalidades_pendentes,
    }
    return render(request, 'caixa/registrar_pagamento.html', context)

def registrar_sessao_avulsa(request):
    # Verificar se há caixa aberto
    caixa_aberto = AberturaCaixa.objects.filter(aberto=True).first()
    if not caixa_aberto:
        return redirect('abrir_caixa')
    
    if request.method == 'POST':
        form = SessaoAvulsaForm(request.POST)
        if form.is_valid():
            sessao = form.save(commit=False)
            sessao.tipo = 'entrada'
            sessao.categoria_entrada = 'sessao_avulsa'
            sessao.caixa = AberturaCaixa.objects.filter(aberto=True).first()  # ← ADICIONE
            sessao.save()
            return redirect('dashboard_caixa')
    else:
        form = SessaoAvulsaForm()
    
    context = {'form': form}
    return render(request, 'caixa/registrar_sessao_avulsa.html', context)


def registrar_saida_caixa(request):
    # Verificar se há caixa aberto
    caixa_aberto = AberturaCaixa.objects.filter(aberto=True).first()
    if not caixa_aberto:
        return redirect('abrir_caixa')
    
    if request.method == 'POST':
        form = SaidaCaixaForm(request.POST)
        if form.is_valid():
            saida = form.save(commit=False)
            saida.tipo = 'saida'
            saida.caixa = AberturaCaixa.objects.filter(aberto=True).first()  # ← ADICIONE
            saida.save()
            return redirect('dashboard_caixa')
    else:
        form = SaidaCaixaForm()
    
    context = {'form': form}
    return render(request, 'caixa/registrar_saida.html', context)


def relatorio_faturamento(request):
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    pagamentos = Pagamento.objects.all()
    
    if data_inicio:
        pagamentos = pagamentos.filter(data_pagamento__date__gte=data_inicio)
    if data_fim:
        pagamentos = pagamentos.filter(data_pagamento__date__lte=data_fim)
    
    total_faturado = pagamentos.aggregate(Sum('valor_pago'))['valor_pago__sum'] or 0
    
    por_servico = pagamentos.values(
        'mensalidade__servico__nome'
    ).annotate(
        total=Sum('valor_pago'),
        count=Count('id')
    )
    
    por_metodo = pagamentos.values(
        'metodo_pagamento'
    ).annotate(
        total=Sum('valor_pago'),
        count=Count('id')
    )
    
    faturamento_diario = pagamentos.values(
        'data_pagamento__date'
    ).annotate(
        total=Sum('valor_pago')
    ).order_by('data_pagamento__date')
    
    context = {
        'total_faturado': total_faturado,
        'por_servico': por_servico,
        'por_metodo': por_metodo,
        'faturamento_diario': faturamento_diario,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    }
    return render(request, 'caixa/relatorio.html', context)

def relatorio_fechamento_caixa(request, caixa_id):
    caixa = get_object_or_404(AberturaCaixa, id=caixa_id)
    
    # Buscar todas as movimentações deste caixa
    pagamentos = Pagamento.objects.filter(caixa=caixa).select_related(
        'mensalidade__paciente', 'mensalidade__servico'
    )
    
    movimentacoes_caixa = MovimentacaoCaixa.objects.filter(caixa=caixa).select_related('paciente')
    
    # Calcular totais (sempre recalcular, não confiar nos campos salvos)
    total_entradas_pag = pagamentos.aggregate(Sum('valor_pago'))['valor_pago__sum'] or Decimal('0')
    entradas_caixa = movimentacoes_caixa.filter(tipo='entrada').aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
    saidas_caixa = movimentacoes_caixa.filter(tipo='saida').aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
    
    total_entradas = total_entradas_pag + entradas_caixa
    total_saidas = saidas_caixa
    saldo_final = caixa.saldo_inicial + total_entradas - total_saidas
    
    # Unir tudo em uma lista
    movimentacoes = []
    
    # Adicionar pagamentos
    for pag in pagamentos:
        movimentacoes.append({
            'data': pag.data_pagamento,
            'descricao': f"Mensalidade - {pag.mensalidade.servico.nome if pag.mensalidade else 'N/A'}",
            'paciente': pag.mensalidade.paciente.nome if pag.mensalidade else '-',
            'tipo': 'entrada',
            'valor': pag.valor_pago,
            'metodo': pag.get_metodo_pagamento_display(),
        })
    
    # Adicionar movimentações
    for mov in movimentacoes_caixa:
        movimentacoes.append({
            'data': mov.data_movimentacao,
            'descricao': mov.descricao,
            'paciente': mov.paciente.nome if mov.paciente else '-',
            'tipo': mov.tipo,
            'valor': mov.valor,
            'metodo': mov.get_categoria_entrada_display() if mov.tipo == 'entrada' else mov.get_categoria_saida_display(),
        })
    
    # Ordenar por data
    movimentacoes.sort(key=lambda x: x['data'])
    
    # Calcular estatísticas por método de pagamento
    metodos_pagamento = {}
    for pag in pagamentos:
        metodo = pag.get_metodo_pagamento_display()
        if metodo not in metodos_pagamento:
            metodos_pagamento[metodo] = Decimal('0')
        metodos_pagamento[metodo] += pag.valor_pago
    
    context = {
        'caixa': caixa,
        'movimentacoes': movimentacoes,
        'metodos_pagamento': metodos_pagamento,
        'total_entradas': total_entradas,  # ADICIONADO
        'total_saidas': total_saidas,      # ADICIONADO
        'saldo_final': saldo_final,        # ADICIONADO
    }
    
    return render(request, 'caixa/relatorio_fechamento.html', context)