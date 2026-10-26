from rest_framework.permissions import IsAuthenticated

from usuarios.permissions import IsConvivente  # noqa: F401  re-export

from .models import Comunidade


class IsModeradorDaComunidade(IsAuthenticated):
    """Permite acesso apenas ao moderador da comunidade identificada por `pk`."""

    message = 'Apenas o moderador desta comunidade pode realizar esta ação.'

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        pk = view.kwargs.get('pk')
        if pk is None:
            return False
        return Comunidade.objects.filter(pk=pk, moderador=request.user).exists()
