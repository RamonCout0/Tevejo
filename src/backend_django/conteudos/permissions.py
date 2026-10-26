from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerCurador(BasePermission):
    """Permite escrita apenas para o Curador dono do conteúdo.

    - Métodos seguros (GET/HEAD/OPTIONS) sempre passam (leitura é pública).
    - Para escrita, exige que `request.user` tenha relação `.curador` e que
      o `obj.curador_id` corresponda ao curador autenticado.

    Usar em conjunto com `IsCurador` no `permission_classes` da view: a
    primeira garante "é curador?", esta garante "é dono?".
    """

    message = 'Você só pode alterar conteúdos que você mesmo publicou.'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        curador = getattr(request.user, 'curador', None)
        return curador is not None and obj.curador_id == curador.pk
