from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ConteudoEducacionalViewSet,
    DenunciarConteudoView,
    TagsViewSet,
)

# 1. Criamos o roteador para as rotas automáticas (Listar, Editar, Deletar)
router = DefaultRouter()
router.register(r'conteudo-educacional', ConteudoEducacionalViewSet, basename='conteudo-educacional')
router.register(r'tags', TagsViewSet, basename='tags')

urlpatterns = [
    # Rotas automáticas do router
    path('', include(router.urls)),

   
    #path('criar-conteudo/', ConteudoEducacionalViewSet.as_view({'post': 'create'}), name='criar-conteudo'),

    # CDU022 - Denunciar Conteúdo Educacional
    path(
        'conteudo-educacional/<int:pk>/denunciar/',
        DenunciarConteudoView.as_view(),
        name='denunciar-conteudo',
    ),
]