from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
import calendar
from dateutil.relativedelta import relativedelta

from .models import Paciente
from .forms import PacienteForm
from mensalidades.models import Mensalidade


def cadastrar_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                paciente = form.save()

                # Verificar se tem serviço selecionado
                if paciente.servico and paciente.valor_mensalidade and paciente.dia_vencimento:
                    # Pegar quantidade de meses (se for fisioterapia)
                    quantidade_meses = int(request.POST.get('quantidade_meses', 12))

                    # Verificar se é fisioterapia
                    if 'fisioterapia' in paciente.servico.nome.lower():
                        total_meses = quantidade_meses
                    else:
                        total_meses = 12  # Outros serviços sempre 12 meses

                    # Criar mensalidades
                    data_base = timezone.localdate()  # date (não datetime)
                    for i in range(total_meses):
                        data_vencimento = data_base + relativedelta(months=i)

                        # Ajustar para o dia de vencimento escolhido (sem quebrar em meses menores)
                        ano = data_vencimento.year
                        mes = data_vencimento.month
                        ultimo_dia = calendar.monthrange(ano, mes)[1]
                        dia = min(paciente.dia_vencimento, ultimo_dia)

                        data_vencimento = data_vencimento.replace(day=dia)

                        Mensalidade.objects.create(
                            paciente=paciente,
                            servico=paciente.servico,
                            valor=paciente.valor_mensalidade,
                            data_vencimento=data_vencimento,
                            status='pendente'
                        )

                    messages.success(request, f'Paciente cadastrado com sucesso! {total_meses} mensalidades criadas.')
                else:
                    messages.success(request, 'Paciente cadastrado com sucesso!')

            return redirect('lista_pacientes')
    else:
        form = PacienteForm()

    return render(request, 'pacientes/formulario.html', {'form': form, 'titulo': 'Cadastrar Paciente'})


def editar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)

    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente atualizado com sucesso!')
            return redirect('lista_pacientes')
    else:
        form = PacienteForm(instance=paciente)

    return render(request, 'pacientes/formulario.html', {'form': form, 'titulo': 'Editar Paciente', 'paciente': paciente})


def listar_pacientes(request):
    pacientes = Paciente.objects.all().select_related('servico')
    return render(request, 'pacientes/lista.html', {'pacientes': pacientes})


def detalhes_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    mensalidades = Mensalidade.objects.filter(paciente=paciente).order_by('-data_vencimento')

    context = {
        'paciente': paciente,
        'mensalidades': mensalidades,
    }
    return render(request, 'pacientes/detalhes.html', context)