# mensalidades/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_mensalidades, name='lista_mensalidades'),
    path('api/mensalidades-por-paciente/', views.api_mensalidades_por_paciente, name='api_mensalidades_por_paciente'),
    path('api/mensalidade-detalhe/', views.api_detalhe_mensalidade, name='api_detalhe_mensalidade'),
]
