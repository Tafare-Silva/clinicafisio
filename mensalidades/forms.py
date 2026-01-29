# mensalidades/forms.py
from django import forms
from .models import Mensalidade

class MensalidadeForm(forms.ModelForm):
    class Meta:
        model = Mensalidade
        fields = ['paciente', 'servico', 'valor', 'data_vencimento']
        widgets = {
            'paciente': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg'
            }),
            'servico': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg'
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg',
                'step': '0.01'
            }),
            'data_vencimento': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg',
                'type': 'date'
            }),
        }
