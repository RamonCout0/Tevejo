from django.urls import path
from . import views

app_name = "usuarios"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("cadastro/", views.CadastroView.as_view(), name="cadastro"),
    path("perfil/", views.PerfilView.as_view(), name="perfil"),
    path("acesso-negado/", views.AcessoNegadoView.as_view(), name="acesso_negado"),
    path("perfil/editar-foto/", views.editar_foto_perfil, name="editar_foto"),
    path("perfil/editar-biografia/", views.editar_biografia_perfil, name="editar_biografia"),
]
