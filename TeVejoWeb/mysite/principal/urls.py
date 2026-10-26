from django.urls import path
from . import views

app_name = 'principal'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('principal/discussoes/', views.DiscussoesView.as_view(), name='discussoes'),
    
    path("conteudos/", views.ConteudosView.as_view(), name="conteudos"),
    path("encontros/", views.EncontrosView.as_view(), name="encontros"),

    # Comunidades
    path("comunidades/criar/", views.CriarComunidadeView.as_view(), name="criar_comunidade"),
    path("comunidades/gerenciar/", views.GerenciarComunidadesView.as_view(), name="gerenciar_comunidades"),
    path("comunidade/<int:pk>/", views.ComunidadeDetailView.as_view(), name="comunidade"),
]