# mensalidades/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_mensalidades, name='lista_mensalidades'),
]
