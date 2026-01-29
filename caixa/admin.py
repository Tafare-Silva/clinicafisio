# caixa/admin.py
from django.contrib import admin
from .models import Pagamento

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('numero_recibo', 'mensalidade', 'valor_pago', 'metodo_pagamento', 'data_pagamento')
    list_filter = ('metodo_pagamento', 'data_pagamento')
    search_fields = ('numero_recibo', 'mensalidade__paciente__nome')
    readonly_fields = ('data_pagamento',)
    date_hierarchy = 'data_pagamento'
    
    fieldsets = (
        ('Pagamento', {
            'fields': ('mensalidade', 'valor_pago', 'numero_recibo')
        }),
        ('Método', {
            'fields': ('metodo_pagamento',)
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Data', {
            'fields': ('data_pagamento',),
            'classes': ('collapse',)
        }),
    )
