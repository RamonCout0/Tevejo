from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    CadastroConviventeSerializer,
    GoogleLoginSerializer,
    LoginSerializer,
    SessaoSerializer,
    UsuarioMeSerializer,
    UsuarioSerializer,
)


def _sessao(usuario, request):
    """Resposta padrão de login/cadastro: tokens JWT + usuário com seus papéis."""
    refresh = RefreshToken.for_user(usuario)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'usuario': UsuarioSerializer(usuario, context={'request': request}).data,
    }


class UsuarioMeView(APIView):
    """Retorna ou atualiza os dados pessoais do usuário autenticado."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = UsuarioMeSerializer

    @extend_schema(responses=UsuarioSerializer)
    def get(self, request, *args, **kwargs):
        return Response(UsuarioSerializer(request.user, context={'request': request}).data)

    def patch(self, request, *args, **kwargs):
        serializer = UsuarioMeSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# CDU019 - Termo de Consentimento e Responsabilidade
# ---------------------------------------------------------------------------


class AceitarTermoView(APIView):
    """Registra o aceite da versão vigente do termo pelo usuário autenticado."""

    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses=UsuarioSerializer)
    def post(self, request, *args, **kwargs):
        usuario = request.user
        usuario.termo_versao_aceita = settings.TERMO_CONSENTIMENTO_VERSAO
        usuario.termo_aceito_em = timezone.now()
        usuario.save(update_fields=['termo_versao_aceita', 'termo_aceito_em'])
        return Response(UsuarioSerializer(usuario, context={'request': request}).data)


# ---------------------------------------------------------------------------
# CDU026 - Guia Condutor
# ---------------------------------------------------------------------------


class ResponderConviteGuiaView(APIView):
    """Registra que o usuário respondeu ao convite do guia (aceitou ou recusou).

    Depois disso o convite não aparece mais; o guia continua disponível no
    botão de ajuda (CDU027).
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses=UsuarioSerializer)
    def post(self, request, *args, **kwargs):
        usuario = request.user
        if usuario.guia_respondido_em is None:
            usuario.guia_respondido_em = timezone.now()
            usuario.save(update_fields=['guia_respondido_em'])
        return Response(UsuarioSerializer(usuario, context={'request': request}).data)


# ---------------------------------------------------------------------------
# CDU001 - Fazer Login
# ---------------------------------------------------------------------------


class LoginView(APIView):
    """Autentica por e-mail ou username + senha. Devolve a sessão em JWT (access + refresh)."""

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(request=LoginSerializer, responses=SessaoSerializer)
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(_sessao(serializer.validated_data['usuario'], request))


class GoogleLoginView(APIView):
    """Autentica com o id_token do Google. Cria a conta na primeira vez."""

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(request=GoogleLoginSerializer, responses=SessaoSerializer)
    def post(self, request, *args, **kwargs):
        serializer = GoogleLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(_sessao(serializer.validated_data['usuario'], request))


# ---------------------------------------------------------------------------
# CDU002 - Auto Cadastro
# ---------------------------------------------------------------------------


class CadastroConviventeView(APIView):
    """Auto cadastro de Convivente. Devolve a sessão já autenticada (JWT)."""

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(request=CadastroConviventeSerializer, responses={201: SessaoSerializer})
    def post(self, request, *args, **kwargs):
        serializer = CadastroConviventeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        convivente = serializer.save()
        # Devolve o mesmo formato do login (com is_convivente etc.), para o
        # front já liberar as telas de Convivente logo após o cadastro.
        return Response(_sessao(convivente, request), status=status.HTTP_201_CREATED)
