from django import forms
from .models import Paciente
from servicos.models import Servico

class PacienteForm(forms.ModelForm):
    quantidade_meses = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=24,
        initial=1,
        label="Quantidade de Meses",
        help_text="Apenas para serviço de Fisioterapia",
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500',
            'id': 'id_quantidade_meses',
            'style': 'display: none;'  # Inicialmente escondido
        })
    )
    
    class Meta:
        model = Paciente
        fields = [
            'nome', 'data_nascimento', 'cpf', 'telefone', 'email', 
            'endereco', 'cidade', 'inicio_atividades',  # Ajustado: removido observacoes e ativo, adicionado cidade
            'servico', 'valor_mensalidade', 'dia_vencimento', 'status'  # Mudado ativo para status
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500',
                'placeholder': 'Nome completo do paciente'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500'
            }),
            'inicio_atividades': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500',
                'placeholder': '000.000.000-00'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500',
                'placeholder': '(00) 00000-0000'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500',
                'placeholder': 'email@exemplo.com'
            }),
            'endereco': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500',
                'placeholder': 'Endereço completo'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500',
                'placeholder': 'Cidade'
            }),
            'servico': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500',
                'id': 'id_servico'
            }),
            'valor_mensalidade': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'dia_vencimento': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500',
                'min': '1',
                'max': '31',
                'placeholder': 'Dia do mês (1-31)'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500'
            }),
        }