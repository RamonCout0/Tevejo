from django.urls import path
from . import views

app_name = 'conteudos'

urlpatterns = [
    path('', views.ListaConteudosView.as_view(), name='conteudos'), 
    path('criar/', views.CriarConteudoView.as_view(), name='criar'),
    path('editar/<int:id>/', views.EditarConteudoView.as_view(), name='editar'), 
    path('deletar/<int:id>/', views.DeletarConteudoView.as_view(), name='deletar'),
    path('ver/<int:id>/', views.VerConteudoView.as_view(), name='ver_conteudo'),
]