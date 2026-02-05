# caixa/forms.py
from django import forms
from .models import Pagamento
from mensalidades.models import Mensalidade
from caixa.models import MovimentacaoCaixa
from servicos.models import Servico
from pacientes.models import Paciente
from decimal import Decimal

class PagamentoForm(forms.ModelForm):
    ajustar_proxima = forms.BooleanField(
        required=False,
        initial=False,
        label="Ajustar diferença na próxima mensalidade",
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-purple-600 focus:ring-purple-500',
            'id': 'id_ajustar_proxima'
        })
    )
    
    class Meta:
        model = Pagamento
        fields = ['mensalidade', 'valor_pago', 'metodo_pagamento', 'observacoes']
        widgets = {
            'mensalidade': forms.Select(attrs={
                'class': 'hidden',  # Vamos esconder o select padrão e usar busca
                'id': 'id_mensalidade',
                'required': True
            }),
            'valor_pago': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500',
                'step': '0.01',
                'placeholder': '0.00',
                'id': 'id_valor_pago'
            }),
            'metodo_pagamento': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg',
                'rows': 3,
                'placeholder': 'Observações opcionais'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar apenas mensalidades pendentes/parciais
        self.fields['mensalidade'].queryset = Mensalidade.objects.filter(
            status__in=['pendente', 'parcial', 'vencida']
        ).select_related('paciente', 'servico').order_by('paciente__nome', '-data_vencimento')


class SessaoAvulsaForm(forms.ModelForm):
    class Meta:
        model = MovimentacaoCaixa
        fields = ['paciente', 'servico', 'valor', 'metodo_pagamento', 'descricao', 'observacoes']
        widgets = {
            'paciente': forms.HiddenInput(),
            'servico': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-lg',
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-lg',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'descricao': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-lg',
                'placeholder': 'Ex: Sessão avulsa'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-slate-300 rounded-lg',
                'rows': 3,
                'placeholder': 'Observações opcionais'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['paciente'].queryset = Paciente.objects.filter(status='ativo').only('id', 'nome')
        self.fields['servico'].queryset = Servico.objects.filter(ativo=True).only('id', 'nome', 'valor_padrao').order_by('tipo', 'nome')

        # tornar obrigatório no formulário
        self.fields['servico'].required = True
        self.fields['metodo_pagamento'].required = True
        self.fields['valor'].required = True

    def clean(self):
        cleaned = super().clean()

        paciente = cleaned.get('paciente')
        servico = cleaned.get('servico')
        metodo = cleaned.get('metodo_pagamento')
        valor = cleaned.get('valor')

        if not paciente:
            self.add_error('paciente', 'Selecione um paciente.')
        if not servico:
            self.add_error('servico', 'Selecione um serviço.')
        if not metodo:
            self.add_error('metodo_pagamento', 'Selecione o método de pagamento.')
        if valor is None:
            self.add_error('valor', 'Informe o valor.')

        return cleaned


class SaidaCaixaForm(forms.ModelForm):
    class Meta:
        model = MovimentacaoCaixa
        fields = ['categoria_saida', 'valor', 'descricao', 'observacoes']
        widgets = {
            'categoria_saida': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent'
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'descricao': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Descrição da saída'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg',
                'rows': 3,
                'placeholder': 'Observações opcionais'
            }),
        }