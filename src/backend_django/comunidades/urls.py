from django.urls import path

from . import views

app_name = 'comunidades'

urlpatterns = [
    path('', views.ListarComunidadesView.as_view(), name='listar'),
    path('criar/', views.CriarComunidadeView.as_view(), name='criar'),
    path('minhas/', views.MinhasComunidadesView.as_view(), name='minhas'),
    path('encontros/', views.EncontrosPublicosView.as_view(), name='encontros-publicos'),
    path('<int:pk>/', views.ComunidadeDetailView.as_view(), name='detalhe'),
    path('<int:pk>/participar/', views.ParticiparComunidadeView.as_view(), name='participar'),
    path('<int:pk>/sair/', views.SairComunidadeView.as_view(), name='sair'),

    # Postagens & Encontros
    path('<int:pk>/postagens/', views.PostagensComunidadeView.as_view(), name='postagens'),
    path('<int:pk>/postagens/<int:postagem_id>/curtir/', views.CurtirPostagemView.as_view(), name='curtir-postagem'),
    path('<int:pk>/postagens/<int:postagem_id>/comentarios/', views.ComentariosPostagemView.as_view(), name='comentarios-postagem'),
    path('<int:pk>/postagens/<int:postagem_id>/comentarios/<int:comentario_id>/curtir/', views.CurtirComentarioView.as_view(), name='curtir-comentario'),
    path('<int:pk>/postagens/<int:postagem_id>/comentarios/<int:comentario_id>/denunciar/', views.DenunciarComentarioView.as_view(), name='denunciar-comentario'),
    path('<int:pk>/postagens/<int:postagem_id>/denunciar/', views.DenunciarPostagemView.as_view(), name='denunciar-postagem'),
    path('<int:pk>/moderacao/', views.ModeracaoComunidadeView.as_view(), name='moderacao'),
    path('<int:pk>/moderacao/<int:denuncia_id>/<str:acao>/', views.AnalisarDenunciaPostagemView.as_view(), name='analisar-denuncia'),
    path('<int:pk>/encontros/', views.ListarEncontrosView.as_view(), name='listar-encontros'),
    path('<int:pk>/encontros/criar/', views.CriarEncontroView.as_view(), name='criar-encontro'),

    # CDU024 — Moderar Conviventes
    path('<int:pk>/membros/', views.MembrosComunidadeView.as_view(), name='membros'),
    path('<int:pk>/moderar/', views.ModerarConviventeView.as_view(), name='moderar'),
    path(
        '<int:pk>/membros/<int:convivente_id>/historico/',
        views.HistoricoConviventeView.as_view(),
        name='historico-convivente',
    ),
]
