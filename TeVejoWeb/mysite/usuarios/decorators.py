from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from usuarios.models import Curador


def role_required(required_roles):
    """
    Decorador que verifica o tipo de usuário (role) antes de executar uma view.
    
    Args:
        required_roles: Lista com tipos de usuário permitidos
                       Valores possíveis: ['curador', 'convivente', 'admin']
    
    Exemplo:
        @role_required(['curador'])
        def criar_conteudo(request):
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required(login_url='usuarios:login')
        def wrapper(request, *args, **kwargs):
            user_role = get_user_role(request.user)
            
            # Verifica se o role do usuário está na lista de roles permitidos
            if user_role not in required_roles:
                messages.error(
                    request, 
                    f'Acesso negado. Apenas {", ".join(required_roles)} podem acessar este recurso.'
                )
                return redirect('usuarios:acesso_negado')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def get_user_role(user):
    """
    Determina o role/tipo do usuário.
    
    Retorna:
        'curador' se o usuário é instância de Curador
        'convivente' se é usuário comum (Usuario)
        'admin' se é staff/superuser
    """
    if user.is_superuser or user.is_staff:
        return 'admin'
    
    # Verifica se é um Curador
    if Curador.objects.filter(pk=user.pk).exists():
        return 'curador'
    
    # Se não é Curador e não é admin, é um Convivente
    return 'convivente'


def is_curador(user):
    """Verifica se um usuário é curador."""
    return Curador.objects.filter(pk=user.pk).exists()


def is_convivente(user):
    """Verifica se um usuário é convivente (não é curador)."""
    return not is_curador(user) and not (user.is_staff or user.is_superuser)
