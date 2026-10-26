from django.urls import path
from . import views

app_name = 'comunidades'

urlpatterns = [
    path('', views.DiscussaoView.as_view(), name='index'),
    path('criar/', views.CriarComunidadeView.as_view(), name='criar'),
    path('post/', views.CriarPostView.as_view(), name='criarpost'),
    path('moderar/', views.ModerancaoView.as_view(), name='moderacao'),
    path('participar/<int:comunidade_id>/', views.ParticiparComunidadeView.as_view(), name='participar'),
    path('comunidade/<int:comunidade_id>/criar-post/', views.CriarPostView.as_view(), name='criarpost'),
    path('sair/<int:comunidade_id>/', views.SairComunidadeView.as_view(), name='sair'),
    path('explorar/', views.ExplorarComunidadesView.as_view(), name='explorar_comunidades'),
    path('api/buscar/', views.BuscarComunidadesAPIView.as_view(), name='buscar_api'),
]