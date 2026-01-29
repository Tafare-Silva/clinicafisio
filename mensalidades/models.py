# mensalidades/models.py
from django.db import models

from django.utils import timezone
from datetime import timedelta
from pacientes.models import Paciente
from servicos.models import Servico

class Mensalidade(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('paga', 'Paga'),
        ('parcial', 'Parcialmente Paga'),
        ('vencida', 'Vencida'),
    ]
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='mensalidades')
    servico = models.ForeignKey(Servico, on_delete=models.PROTECT)
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    data_vencimento = models.DateField(db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    @property
    def dias_ate_vencimento(self):
        return (self.data_vencimento - timezone.now().date()).days
    
    @property
    def esta_vencida(self):
        return self.data_vencimento < timezone.now().date() and self.status == 'pendente'
    
    def __str__(self):
        return f"{self.paciente.nome} - {self.servico.nome} ({self.data_vencimento})"
    
    class Meta:
        ordering = ['data_vencimento']
        verbose_name_plural = 'Mensalidades'
        indexes = [
            models.Index(fields=['paciente', 'status']),
            models.Index(fields=['data_vencimento', 'status']),
        ]
