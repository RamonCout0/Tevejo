from rest_framework.permissions import IsAuthenticated


class IsConvivente(IsAuthenticated):
    """Permite acesso apenas a usuários autenticados que são Conviventes."""

    message = 'Apenas Conviventes podem realizar esta ação.'

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return hasattr(request.user, 'convivente')


class IsCurador(IsAuthenticated):
    """Permite acesso apenas a usuários autenticados que são Curadores."""

    message = 'Apenas Curadores podem realizar esta ação.'

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return hasattr(request.user, 'curador')
