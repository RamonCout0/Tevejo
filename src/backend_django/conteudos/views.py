from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied, ValidationError as DRFValidationError

from usuarios.permissions import IsConvivente, IsCurador

from .models import ConteudoEducacional, Tags
from .permissions import IsOwnerCurador
from .serializers import (
    ConteudoEducacionalSerializer,
    DenunciaSerializer,
    RegistrarDenunciaSerializer,
    TagsSerializer,
)
from .services import DenunciaService


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all().order_by('nome')
    serializer_class = TagsSerializer

    def get_permissions(self):
        # Leitura pública (filtro da tela de conteúdos); só Curador cria/edita/remove.
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsCurador()]


class ConteudoEducacionalViewSet(viewsets.ModelViewSet):
    queryset = ConteudoEducacional.objects.all()
    serializer_class = ConteudoEducacionalSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def get_permissions(self):
        """
        - Leitura (list, retrieve): qualquer um (público).
        - Criação: precisa ser Curador.
        - Edição/exclusão: precisa ser Curador *e* dono do conteúdo.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsCurador(), IsOwnerCurador()]
        if self.action == 'create':
            return [IsCurador()]
        return [AllowAny()]

    def perform_create(self, serializer):
        # `curador` não vem no payload; injetamos a partir do request autenticado.
        # ModelSerializer.create() do DRF cuida do M2M (tipos) automaticamente.
        serializer.save(curador=self.request.user.curador)


# ---------------------------------------------------------------------------
# CDU022 - Denunciar Conteúdo Educacional
# ---------------------------------------------------------------------------


class DenunciarConteudoView(APIView):
    """Registra uma denúncia sobre um conteúdo educacional. Apenas Conviventes."""

    permission_classes = [IsConvivente]
    serializer_class = RegistrarDenunciaSerializer

    @extend_schema(responses={201: DenunciaSerializer})
    def post(self, request, pk, *args, **kwargs):
        try:
            conteudo = ConteudoEducacional.objects.get(pk=pk)
        except ConteudoEducacional.DoesNotExist:
            return Response(
                {"erro": "Conteúdo educacional não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = RegistrarDenunciaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            denuncia = DenunciaService.registrar(
                conteudo=conteudo,
                convivente=request.user.convivente,
                motivo=serializer.validated_data['motivo'],
                descricao=serializer.validated_data.get('descricao', ''),
            )
        except DRFValidationError as exc:
            return Response({"erro": exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as exc:
            return Response({"erro": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except Exception:
            return Response(
                {"erro": "Não foi possível registrar a denúncia. Tente novamente."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(DenunciaSerializer(denuncia).data, status=status.HTTP_201_CREATED)
