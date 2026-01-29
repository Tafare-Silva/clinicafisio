# servicos/admin.py
from django.contrib import admin
from .models import Servico

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'valor_padrao', 'ativo')
    list_filter = ('tipo', 'ativo')
    search_fields = ('nome', 'descricao')
    
    fieldsets = (
        ('Informações', {
            'fields': ('nome', 'tipo', 'descricao')
        }),
        ('Valores', {
            'fields': ('valor_padrao', 'ativo')
        }),
    )