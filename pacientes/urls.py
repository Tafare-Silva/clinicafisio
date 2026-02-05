from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_pacientes, name='lista_pacientes'),  # ← nome 'lista_pacientes'
    path('cadastrar/', views.cadastrar_paciente, name='cadastrar_paciente'),
    path('editar/<int:pk>/', views.editar_paciente, name='editar_paciente'),
    path('detalhes/<int:pk>/', views.detalhes_paciente, name='detalhes_paciente'),
    path('api/buscar/', views.api_buscar_pacientes, name='api_buscar_pacientes'),
]