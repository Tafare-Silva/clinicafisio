# pacientes/admin.py
from django.contrib import admin
from .models import Paciente

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'telefone', 'status', 'data_cadastro')
    list_filter = ('status', 'data_cadastro')
    search_fields = ('nome', 'cpf', 'email', 'telefone')
    readonly_fields = ('data_cadastro', 'data_atualizacao')
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('nome', 'email', 'telefone', 'cpf', 'data_nascimento')
        }),
        ('Endereço', {
            'fields': ('endereco', 'cidade')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Datas', {
            'fields': ('data_cadastro', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )