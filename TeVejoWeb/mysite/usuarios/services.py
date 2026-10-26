from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import MultipleObjectsReturned, ValidationError
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


# ============================================================
# LOGIN
# ============================================================

class AuthenticationService:
    """
    Serviço responsável pela autenticação de usuários.
    """

    @staticmethod
    def authenticate(login_value, password):
        login_value = login_value.strip()

        # 1) Tentativa como username
        user = authenticate(username=login_value, password=password)
        if user:
            return {"success": True, "user": user}

        # 2) Tentativa como email
        try:
            u = User.objects.get(email__iexact=login_value)
        except User.DoesNotExist:
            return {"success": False, "error": "invalid_credentials"}
        except MultipleObjectsReturned:
            u = User.objects.filter(email__iexact=login_value).first()
            if not u:
                return {"success": False, "error": "invalid_credentials"}

        # 3) Autenticar usando o username encontrado
        user = authenticate(username=u.username, password=password)
        if user:
            return {"success": True, "user": user}

        return {"success": False, "error": "invalid_credentials"}


# ============================================================
# CADASTRO
# ============================================================

class RegistrationService:
    """
    Serviço responsável pelo registro de novos usuários.
    """

    @staticmethod
    def register(*, username, nome, email, password, foto=None, biografia=None):
        """
        Uso de parâmetros nomeados (*) evita erros de ordem.
        """

        username = username.strip()
        email = email.strip().lower()
        nome = nome.strip()
        biografia = biografia.strip() if biografia else None

        # Validações de existência
        if User.objects.filter(username=username).exists():
            return {"success": False, "error": "username_exists"}

        if User.objects.filter(email__iexact=email).exists():
            return {"success": False, "error": "email_exists"}

        try:
            # Cria o usuário básico
            user = User(
                username=username,
                email=email,
            )
            user.set_password(password)

            # Campos extras
            user.nome = nome
            user.foto = foto
            user.biografia = biografia

            # Valida campos do model antes de salvar
            user.full_clean()
            user.save()

            # Grupo padrão
            grupo_convivente, _ = Group.objects.get_or_create(name="Convivente")
            user.groups.add(grupo_convivente)

            return {"success": True, "user": user}

        except ValidationError as e:
            # Retorna erro detalhado de validação
            logger.warning(f"Erro de validação ao registrar usuário: {e.message_dict}")
            return {"success": False, "error": e.message_dict}

        except Exception as e:
            # Qualquer outro erro inesperado
            logger.exception("Erro desconhecido ao registrar usuário")
            return {"success": False, "error": str(e)}
