# pacientes/models.py
from django.db import models
from django.core.validators import RegexValidator

class Paciente(models.Model):
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('suspenso', 'Suspenso'),
    ]
    
    nome = models.CharField(max_length=200, db_index=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    telefone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        blank=True
    )
    cpf = models.CharField(max_length=14, unique=True, db_index=True)
    data_nascimento = models.DateField(blank=True, null=True)
    endereco = models.CharField(max_length=300, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    
    # NOVO CAMPO
    inicio_atividades = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Início das Atividades",
        help_text="Data em que o paciente começou a utilizar a clínica"
    )
    
    servico = models.ForeignKey('servicos.Servico', on_delete=models.SET_NULL, null=True, blank=True, related_name='pacientes')
    valor_mensalidade = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # NOVO CAMPO para controlar dia de vencimento
    dia_vencimento = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name="Dia de Vencimento",
        help_text="Dia do mês para vencimento da mensalidade (1-31)"
    )
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ativo')
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        ordering = ['-data_cadastro']
        verbose_name_plural = 'Pacientes'
        indexes = [
            models.Index(fields=['nome', 'status']),
        ]