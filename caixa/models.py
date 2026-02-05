from django.db import models
from mensalidades.models import Mensalidade
import uuid


class AberturaCaixa(models.Model):
    data_abertura = models.DateTimeField(auto_now_add=True)
    data_fechamento = models.DateTimeField(null=True, blank=True)
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saldo_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_entradas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_saidas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    aberto = models.BooleanField(default=True)
    observacoes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Caixa {self.data_abertura.strftime('%d/%m/%Y')} - {'Aberto' if self.aberto else 'Fechado'}"
    
    class Meta:
        ordering = ['-data_abertura']
        verbose_name = 'Abertura de Caixa'
        verbose_name_plural = 'Aberturas de Caixa'

class Pagamento(models.Model):
    METODO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('credito', 'Cartão Crédito'),
        ('debito', 'Cartão Débito'),
        ('transferencia', 'Transferência'),
        ('cheque', 'Cheque'),
        ('pix', 'PIX'),
    ]
    
    mensalidade = models.ForeignKey(Mensalidade, on_delete=models.PROTECT, related_name='pagamentos')
    valor_pago = models.DecimalField(max_digits=8, decimal_places=2)
    metodo_pagamento = models.CharField(max_length=20, choices=METODO_CHOICES)
    data_pagamento = models.DateTimeField(auto_now_add=True, db_index=True)
    numero_recibo = models.CharField(max_length=50, unique=True, blank=True, null=True)
    observacoes = models.TextField(blank=True)
    caixa = models.ForeignKey(AberturaCaixa, on_delete=models.SET_NULL, null=True, blank=True, related_name='pagamentos')
    
    def save(self, *args, **kwargs):
        # Gerar número de recibo automaticamente se não tiver
        if not self.numero_recibo:
            self.numero_recibo = str(uuid.uuid4())[:12].upper()
        
        super().save(*args, **kwargs)
        
        # Atualizar status da mensalidade
        total_pago = self.mensalidade.pagamentos.aggregate(
            models.Sum('valor_pago')
        )['valor_pago__sum'] or 0
        
        if total_pago >= self.mensalidade.valor:
            self.mensalidade.status = 'paga'
        else:
            self.mensalidade.status = 'parcial'
        self.mensalidade.save()
    
    def __str__(self):
        return f"Pagamento {self.numero_recibo} - R$ {self.valor_pago:.2f}"
    
    class Meta:
        ordering = ['-data_pagamento']
        verbose_name_plural = 'Pagamentos'
        indexes = [
            models.Index(fields=['data_pagamento']),
            models.Index(fields=['metodo_pagamento']),
        ]


class MovimentacaoCaixa(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    ]
    
    CATEGORIA_ENTRADA_CHOICES = [
        ('mensalidade', 'Mensalidade'),
        ('sessao_avulsa', 'Sessão Avulsa'),
        ('outro', 'Outro'),
    ]
    
    CATEGORIA_SAIDA_CHOICES = [
        ('despesa', 'Despesa'),
        ('aluguel', 'Aluguel'),
        ('funcionario', 'Funcionário'),
        ('outro', 'Outro'),
    ]

    METODO_PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('pix', 'Pix'),
        ('credito', 'Cartão de Crédito'),
        ('debito', 'Cartão de Débito'),
        ('cheque', 'Cheque'),
        ('outro', 'Outro'),
    ]
    
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    categoria_entrada = models.CharField(max_length=20, choices=CATEGORIA_ENTRADA_CHOICES, blank=True, null=True)
    categoria_saida = models.CharField(max_length=20, choices=CATEGORIA_SAIDA_CHOICES, blank=True, null=True)
    
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    
    paciente = models.ForeignKey('pacientes.Paciente', on_delete=models.SET_NULL, null=True, blank=True, related_name='movimentacoes_caixa')
    
    data_movimentacao = models.DateTimeField(auto_now_add=True, db_index=True)
    observacoes = models.TextField(blank=True)
    caixa = models.ForeignKey(AberturaCaixa, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimentacoes')
    
    servico = models.ForeignKey(
        'servicos.Servico',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_caixa'
    )

    metodo_pagamento = models.CharField(
        max_length=20,
        choices=METODO_PAGAMENTO_CHOICES,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.descricao} - R$ {self.valor:.2f}"
    
    class Meta:
        ordering = ['-data_movimentacao']
        verbose_name_plural = 'Movimentações de Caixa'
        indexes = [
            models.Index(fields=['data_movimentacao', 'tipo']),
        ]

