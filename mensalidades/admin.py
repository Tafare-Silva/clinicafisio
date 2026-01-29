# mensalidades/admin.py
from django.contrib import admin
from .models import Mensalidade

@admin.register(Mensalidade)
class MensalidadeAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'servico', 'valor', 'data_vencimento', 'status')
    list_filter = ('status', 'data_vencimento', 'servico')
    search_fields = ('paciente__nome', 'servico__nome')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    date_hierarchy = 'data_vencimento'
    
    fieldsets = (
        ('Informações', {
            'fields': ('paciente', 'servico', 'valor', 'data_vencimento')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
