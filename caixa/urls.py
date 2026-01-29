from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_caixa, name='dashboard_caixa'),
    path('abrir/', views.abrir_caixa, name='abrir_caixa'),
    path('fechar/', views.fechar_caixa, name='fechar_caixa'),
    path('pagamento/', views.registrar_pagamento, name='registrar_pagamento'),
    path('sessao-avulsa/', views.registrar_sessao_avulsa, name='registrar_sessao_avulsa'),
    path('saida/', views.registrar_saida_caixa, name='registrar_saida_caixa'),
    path('relatorio/', views.relatorio_faturamento, name='relatorio_faturamento'),
    path('relatorio-fechamento/<int:caixa_id>/', views.relatorio_fechamento_caixa, name='relatorio_fechamento_caixa'),
]
