# servicos/models.py

from django.db import models

class Servico(models.Model):
    TIPO_CHOICES = [
        ('pilates', 'Pilates'),
        ('academia', 'Academia'),
        ('fisioterapia', 'Fisioterapia'),
        ('massagem', 'Massagem'),
        ('outro', 'Outro'),
    ]
    
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descricao = models.TextField(blank=True)
    valor_padrao = models.DecimalField(max_digits=8, decimal_places=2)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nome} - R$ {self.valor_padrao:.2f}"
    
    class Meta:
        ordering = ['tipo', 'nome']
        verbose_name_plural = 'Serviços'
