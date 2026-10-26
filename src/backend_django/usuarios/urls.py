from django.urls import path

from . import views

app_name = 'usuarios'

urlpatterns = [
    path('me/', views.UsuarioMeView.as_view(), name='me'),
    path('me/aceitar-termo/', views.AceitarTermoView.as_view(), name='aceitar-termo'),
    path('me/guia/', views.ResponderConviteGuiaView.as_view(), name='responder-guia'),
    path('cadastro/', views.CadastroConviventeView.as_view(), name='cadastro'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('login/google/', views.GoogleLoginView.as_view(), name='login-google'),
]
