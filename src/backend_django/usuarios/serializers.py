from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from rest_framework import serializers

from config import limites

from .models import Convivente

Usuario = get_user_model()

MAX_FOTO_BYTES = 5 * 1024 * 1024
FORMATOS_FOTO_PERMITIDOS = ('image/jpeg', 'image/png')


def _email_em_uso(email, excluir_pk=None):
    qs = Usuario.objects.filter(email__iexact=email)
    if excluir_pk is not None:
        qs = qs.exclude(pk=excluir_pk)
    return qs.exists()


def precisa_aceitar_termo(usuario):
    """CDU019: só Conviventes precisam aceitar (a versão vigente) do termo."""
    return (
        hasattr(usuario, 'convivente')
        and usuario.termo_versao_aceita < settings.TERMO_CONSENTIMENTO_VERSAO
    )


# ---------------------------------------------------------------------------
# CDU002 - Auto Cadastro
# ---------------------------------------------------------------------------


class CadastroConviventeSerializer(serializers.ModelSerializer):
    """Cria um Convivente a partir do formulário de auto cadastro.

    `username` e `email` já são validados como únicos pelo ModelSerializer
    (os campos são `unique=True` no model). A senha nunca é devolvida na
    resposta, e precisa ser digitada duas vezes (`password_confirmacao`).
    """

    password = serializers.CharField(write_only=True)
    password_confirmacao = serializers.CharField(write_only=True)

    class Meta:
        model = Convivente
        fields = ['id', 'username', 'email', 'nome', 'password', 'password_confirmacao']
        extra_kwargs = {'nome': {'max_length': limites.USUARIO_NOME}}

    def validate_nome(self, value):
        # Mesma regra da edição de perfil (UsuarioMeSerializer).
        if value and len(value.strip()) < 3:
            raise serializers.ValidationError('O nome deve ter pelo menos 3 caracteres.')
        return value

    def validate_email(self, value):
        # O unique do banco diferencia maiúsculas; o login por e-mail não.
        if _email_em_uso(value):
            raise serializers.ValidationError('Este e-mail já está em uso.')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirmacao'):
            raise serializers.ValidationError({'password_confirmacao': ['As senhas não coincidem.']})

        convivente_temp = Convivente(
            username=attrs.get('username', ''),
            email=attrs.get('email', ''),
            nome=attrs.get('nome', ''),
        )
        try:
            validate_password(attrs['password'], user=convivente_temp)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': list(exc.messages)})
        return attrs

    def create(self, validated_data):
        senha = validated_data.pop('password')
        convivente = Convivente(**validated_data)
        convivente.set_password(senha)
        convivente.save()
        return convivente


class UsuarioSerializer(serializers.Serializer):
    """Representação pública de um Usuario autenticado, com seus papéis."""

    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    nome = serializers.CharField()
    biografia = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    foto = serializers.SerializerMethodField()
    is_convivente = serializers.SerializerMethodField()
    is_curador = serializers.SerializerMethodField()
    precisa_aceitar_termo = serializers.SerializerMethodField()
    mostrar_convite_guia = serializers.SerializerMethodField()

    def get_foto(self, obj) -> str | None:
        # URL relativa (/media/...): funciona igual atrás do proxy do Angular,
        # do nginx ou de qualquer domínio de deploy.
        foto = getattr(obj, 'foto', None)
        return foto.url if foto else None

    def get_is_convivente(self, obj) -> bool:
        return hasattr(obj, 'convivente')

    def get_is_curador(self, obj) -> bool:
        return hasattr(obj, 'curador')

    def get_precisa_aceitar_termo(self, obj) -> bool:
        return precisa_aceitar_termo(obj)

    def get_mostrar_convite_guia(self, obj) -> bool:
        return getattr(obj, 'guia_respondido_em', None) is None


class UsuarioMeSerializer(serializers.ModelSerializer):
    """Serializer para leitura e edição dos dados pessoais do usuário autenticado (CDU018)."""

    is_convivente = serializers.SerializerMethodField()
    is_curador = serializers.SerializerMethodField()
    precisa_aceitar_termo = serializers.SerializerMethodField()
    mostrar_convite_guia = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = (
            'id',
            'username',
            'email',
            'nome',
            'biografia',
            'foto',
            'is_convivente',
            'is_curador',
            'precisa_aceitar_termo',
            'mostrar_convite_guia',
        )
        read_only_fields = (
            'id', 'username', 'is_convivente', 'is_curador', 'precisa_aceitar_termo', 'mostrar_convite_guia',
        )
        extra_kwargs = {
            'nome': {'max_length': limites.USUARIO_NOME},
            'biografia': {'max_length': limites.USUARIO_BIOGRAFIA},
        }

    def get_is_convivente(self, obj) -> bool:
        return hasattr(obj, 'convivente')

    def get_is_curador(self, obj) -> bool:
        return hasattr(obj, 'curador')

    def get_precisa_aceitar_termo(self, obj) -> bool:
        return precisa_aceitar_termo(obj)

    def get_mostrar_convite_guia(self, obj) -> bool:
        return obj.guia_respondido_em is None

    def validate_nome(self, value):
        if value and len(value.strip()) < 3:
            raise serializers.ValidationError('O nome deve ter pelo menos 3 caracteres.')
        return value

    def validate_email(self, value):
        if _email_em_uso(value, excluir_pk=self.instance.pk if self.instance else None):
            raise serializers.ValidationError('Este e-mail já está em uso.')
        return value

    def validate_foto(self, value):
        if value in (None, ''):
            return value
        if value.size > MAX_FOTO_BYTES:
            raise serializers.ValidationError('A imagem deve ter no máximo 5 MB.')
        content_type = getattr(value, 'content_type', None)
        if content_type and content_type not in FORMATOS_FOTO_PERMITIDOS:
            raise serializers.ValidationError('Arquivo de imagem inválido. Use JPG ou PNG.')
        return value

    def to_representation(self, instance):
        dados = super().to_representation(instance)
        dados['foto'] = instance.foto.url if instance.foto else None
        return dados


# ---------------------------------------------------------------------------
# CDU001 - Fazer Login
# ---------------------------------------------------------------------------


class LoginSerializer(serializers.Serializer):
    """Autentica por e-mail (CDU001) ou, alternativamente, por username.

    O username não está no detalhamento do CDU001, mas o frontend já tinha
    um formulário de login por username antes deste JWT entrar — aceitamos
    os dois para não forçar reescrita da tela existente.

    A mensagem de erro é sempre a mesma genérica, esteja o identificador
    incorreto, a senha incorreta ou a conta inativa — evita revelar qual
    deles falhou.
    """

    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get('email')
        username = attrs.get('username')
        if not email and not username:
            raise serializers.ValidationError('Informe e-mail ou username.')

        if email:
            usuario = Usuario.objects.filter(email__iexact=email).first()
        else:
            usuario = Usuario.objects.filter(username__iexact=username).first()

        if usuario is None or not usuario.is_active or not usuario.check_password(attrs['password']):
            raise serializers.ValidationError('Usuário ou senha inválidos.')
        attrs['usuario'] = usuario
        return attrs


class GoogleLoginSerializer(serializers.Serializer):
    """Autentica com o id_token emitido pelo Google Identity Services.

    Cria automaticamente um Convivente na primeira vez que o e-mail do Google
    aparece, já que não há senha para o usuário definir nesse fluxo.
    """

    id_token = serializers.CharField(write_only=True)

    def validate_id_token(self, value):
        try:
            payload = google_id_token.verify_oauth2_token(
                value, google_requests.Request(), settings.GOOGLE_OAUTH_CLIENT_ID,
                # Tolera dessincronia de relógio entre esta máquina e o Google.
                # O ideal é manter o relógio do sistema sincronizado (NTP).
                clock_skew_in_seconds=300,
            )
        except ValueError as exc:
            raise serializers.ValidationError(f'Token do Google inválido ou expirado: {exc}')
        return payload

    def validate(self, attrs):
        payload = attrs['id_token']
        email = payload.get('email')
        if not email or not payload.get('email_verified'):
            raise serializers.ValidationError('Conta Google sem e-mail verificado.')

        usuario = Usuario.objects.filter(email__iexact=email).first()
        if usuario is None:
            usuario = self._criar_convivente(email, payload.get('name', ''))
        elif not usuario.is_active:
            raise serializers.ValidationError('Usuário ou senha inválidos.')

        attrs['usuario'] = usuario
        return attrs

    def _criar_convivente(self, email, nome):
        username = email.split('@')[0]
        sufixo = 1
        username_base = username
        while Usuario.objects.filter(username__iexact=username).exists():
            sufixo += 1
            username = f'{username_base}{sufixo}'

        convivente = Convivente(username=username, email=email, nome=nome or username)
        convivente.set_unusable_password()
        convivente.save()
        return convivente


class SessaoSerializer(serializers.Serializer):
    """Formato da resposta de login/cadastro (documentação do Swagger)."""

    refresh = serializers.CharField()
    access = serializers.CharField()
    usuario = UsuarioSerializer()
