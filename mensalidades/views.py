# mensalidades/views.py
from django.shortcuts import render
from django.db.models import Sum, Q
from .models import Mensalidade
from django.utils import timezone
from datetime import timedelta

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