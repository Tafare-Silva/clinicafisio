# mensalidades/views.py
from django.shortcuts import render
from django.db.models import Sum, Q
from .models import Mensalidade
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from decimal import Decimal


def lista_mensalidades(request):
    hoje = timezone.now().date()
    
    # Filtros
    query = request.GET.get('q', '')
    status_filtro = request.GET.get('status', 'pendente')
    
    mensalidades = Mensalidade.objects.filter(
        status__in=['pendente', 'parcial', 'vencida']
    ).select_related('paciente', 'servico').order_by('data_vencimento')
    
    # Buscar por nome do paciente
    if query:
        mensalidades = mensalidades.filter(
            Q(paciente__nome__icontains=query) |
            Q(paciente__cpf__icontains=query)
        )
    
    if status_filtro and status_filtro != 'todas':
        mensalidades = mensalidades.filter(status=status_filtro)
    
    # Estatísticas
    stats = {
        'total_pendente': Mensalidade.objects.filter(
            status__in=['pendente', 'parcial']
        ).count(),
        'total_vencido': Mensalidade.objects.filter(
            status='vencida',
            data_vencimento__lt=hoje
        ).count(),
        'valor_pendente': Mensalidade.objects.filter(
            status__in=['pendente', 'parcial']
        ).aggregate(sum=Sum('valor'))['sum'] or 0,
    }
    
    context = {
        'mensalidades': mensalidades,
        'stats': stats,
        'status_filtro': status_filtro,
        'query': query,
    }
    return render(request, 'mensalidades/lista.html', context)

@require_GET
def api_mensalidades_por_paciente(request):
    paciente_id = request.GET.get('paciente_id')
    if not paciente_id:
        return JsonResponse([], safe=False)

    hoje = timezone.localdate()

    qs = (
        Mensalidade.objects
        .select_related('paciente', 'servico')
        .filter(paciente_id=paciente_id, status__in=['pendente', 'parcial'])
        .order_by('data_vencimento')[:50]
    )

    data = []
    for m in qs:
        total_pago = m.pagamentos.aggregate(s=Sum('valor_pago'))['s'] or Decimal('0.00')
        restante = (m.valor or Decimal('0.00')) - total_pago
        if restante < 0:
            restante = Decimal('0.00')

        status_ui = 'vencida' if (m.status == 'pendente' and m.data_vencimento < hoje) else m.status

        data.append({
            'id': m.id,
            'paciente_nome': m.paciente.nome if m.paciente else '',
            'servico': m.servico.nome if m.servico else '',
            'valor': str(m.valor),
            'total_pago': str(total_pago),
            'restante': str(restante),
            'vencimento': m.data_vencimento.strftime('%d/%m/%Y') if m.data_vencimento else '',
            'status': status_ui,
        })

    return JsonResponse(data, safe=False)

@require_GET
#@login_required
def api_detalhe_mensalidade(request):
    mensalidade_id = request.GET.get('mensalidade_id')

    if not mensalidade_id:
        return JsonResponse({'error': 'mensalidade_id é obrigatório'}, status=400)

    try:
        m = (Mensalidade.objects
             .select_related('paciente', 'servico')
             .get(id=mensalidade_id))
    except Mensalidade.DoesNotExist:
        return JsonResponse({'error': 'mensalidade não encontrada'}, status=404)

    data = {
        'id': m.id,
        'paciente_id': m.paciente_id,
        'paciente_nome': m.paciente.nome if m.paciente else '',
        'servico': m.servico.nome if m.servico else '',
        'valor': str(m.valor),  # mantém precisão (Decimal)
        'vencimento': m.data_vencimento.strftime('%d/%m/%Y') if m.data_vencimento else '',
        'status': m.status,
    }
    return JsonResponse(data)