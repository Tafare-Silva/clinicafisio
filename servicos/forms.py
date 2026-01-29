# servicos/forms.py
from django import forms
from .models import Servico

class ServicoForm(forms.ModelForm):
    class Meta:
        model = Servico
        fields = ['nome', 'tipo', 'descricao', 'valor_padrao', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg',
                'placeholder': 'Nome do serviço'
            }),
            'tipo': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg',
                'rows': 3
            }),
            'valor_padrao': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg',
                'step': '0.01'
            }),
        }
