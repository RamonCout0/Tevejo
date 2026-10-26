from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from usuarios.models import Curador
from django.contrib.auth.models import Group


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin que verifica o tipo de usuário (role) antes de acessar uma CBV.
    
    Atributos:
        required_roles: Lista com tipos de usuário permitidos
                       Valores possíveis: ['curador', 'convivente', 'admin']
    
    Exemplo:
        class CriarConteudoView(RoleRequiredMixin, CreateView):
            required_roles = ['curador']
            ...
    """
    required_roles = []
    login_url = reverse_lazy('usuarios:login')
    
    def test_func(self):
        """Testa se o usuário tem o role necessário."""
        user_role = self._get_user_role(self.request.user)
        return user_role in self.required_roles
    
    def handle_no_permission(self):
        """Chamado quando o usuário não tem permissão."""
        messages.error(
            self.request,
            f'Acesso negado. Apenas {", ".join(self.required_roles)} podem acessar este recurso.'
        )
        return redirect('usuarios:acesso_negado')
    
    @staticmethod
    def _get_user_role(user):
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
        
        # Verifica se pertence ao grupo Convivente
        if user.groups.filter(name='Convivente').exists():
            return 'convivente'
        
        # Usuário padrão
        return 'usuario'


def is_curador(user):
    """
    Função helper para verificar se um usuário é curador.
    Útil em templates e contextos.
    
    Retorna:
        True se o usuário é um Curador, False caso contrário
    """
    if not user.is_authenticated:
        return False
    return Curador.objects.filter(pk=user.pk).exists()


def is_convivente(user):
    """
    Função helper para verificar se um usuário é convivente.
    Útil em templates e contextos.
    
    Retorna:
        True se o usuário pertence ao grupo Convivente, False caso contrário
    """
    if not user.is_authenticated:
        return False
    return user.groups.filter(name='Convivente').exists()
