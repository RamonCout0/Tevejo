from django.contrib.auth import get_user_model
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError as DRFValidationError
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import AcaoModeracao, ComentarioPostagem, Comunidade, DenunciaPostagem, Postagem, Encontro
from .permissions import IsConvivente, IsModeradorDaComunidade
from .serializers import (
    AcaoModeracaoSerializer,
    AplicarAcaoModeracaoSerializer,
    ComunidadeSerializer,
    EditarComunidadeSerializer,
    EncontroSerializer,
    MembroComunidadeSerializer,
    DenunciaPostagemSerializer, PostagemSerializer,
    ComentarioPostagemSerializer,
)
from .services import (
    ComunidadeService, InteracaoPostagemService,
    EncontroService,
    ModeracaoService,
    PostagemService,
)

User = get_user_model()


class ListarComunidadesView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ComunidadeSerializer

    def get(self, request, *args, **kwargs):
        comunidades = Comunidade.objects.all().order_by('-criado_em')
        serializer = ComunidadeSerializer(comunidades, many=True, context={'request': request})
        return Response(serializer.data)


class CriarComunidadeView(APIView):
    permission_classes = [IsConvivente]
    serializer_class = ComunidadeSerializer

    def post(self, request, *args, **kwargs):
        dados = request.data.copy()
        serializer = ComunidadeSerializer(data=dados, context={'request': request})
        if serializer.is_valid():
            try:
                comunidade = ComunidadeService.criar_comunidade(
                    serializer,
                    request.user.convivente,
                    icone=request.FILES.get('icone'),
                    banner=request.FILES.get('banner'),
                )
                return Response(
                    ComunidadeSerializer(comunidade, context={'request': request}).data,
                    status=status.HTTP_201_CREATED,
                )
            except DRFValidationError as exc:
                return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
            except Exception:
                return Response(
                    {"erro": "Não foi possível criar a comunidade no momento. Tente novamente."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MinhasComunidadesView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ComunidadeSerializer

    def get(self, request, *args, **kwargs):
        comunidades = request.user.comunidades_participadas.all().order_by('nome')
        serializer = ComunidadeSerializer(comunidades, many=True, context={'request': request})
        return Response(serializer.data)


def _verdadeiro(valor):
    """Interpreta booleanos vindos de multipart/form-data ("true", "1"...)."""
    return str(valor).strip().lower() in ('1', 'true', 'on', 'sim')


class ComunidadeDetailView(APIView):
    """Detalhe (público) e, para o moderador, edição e exclusão (CDU012)."""

    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ComunidadeSerializer

    def get(self, request, pk, *args, **kwargs):
        try:
            comunidade = Comunidade.objects.get(pk=pk)
        except Comunidade.DoesNotExist:
            return Response({"erro": "Comunidade não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ComunidadeSerializer(comunidade, context={'request': request}).data)

    @extend_schema(
        request={'multipart/form-data': EditarComunidadeSerializer},
        responses=ComunidadeSerializer,
    )
    def patch(self, request, pk, *args, **kwargs):
        try:
            comunidade = Comunidade.objects.get(pk=pk)
        except Comunidade.DoesNotExist:
            return Response({"erro": "Comunidade não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ComunidadeSerializer(
            comunidade, data=request.data, partial=True, context={'request': request},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            comunidade = ComunidadeService.atualizar_comunidade(
                comunidade,
                request.user,
                serializer,
                icone=request.FILES.get('icone'),
                banner=request.FILES.get('banner'),
                remover_icone=_verdadeiro(request.data.get('remover_icone')),
                remover_banner=_verdadeiro(request.data.get('remover_banner')),
            )
        except PermissionDenied as exc:
            return Response({"erro": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except DRFValidationError as exc:
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
        return Response(ComunidadeSerializer(comunidade, context={'request': request}).data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk, *args, **kwargs):
        try:
            comunidade = Comunidade.objects.get(pk=pk)
        except Comunidade.DoesNotExist:
            return Response({"erro": "Comunidade não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        try:
            ComunidadeService.excluir_comunidade(comunidade, request.user)
        except PermissionDenied as exc:
            return Response({"erro": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ParticiparComunidadeView(APIView):
    permission_classes = [IsConvivente]
    serializer_class = ComunidadeSerializer

    def post(self, request, pk, *args, **kwargs):
        try:
            comunidade = Comunidade.objects.get(pk=pk)
        except Comunidade.DoesNotExist:
            return Response({"erro": "Comunidade não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        try:
            ComunidadeService.participar(comunidade, request.user.convivente)
        except DRFValidationError as exc:
            return Response({"erro": exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as exc:
            return Response({"erro": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        return Response(
            ComunidadeSerializer(comunidade, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )


class SairComunidadeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ComunidadeSerializer

    def post(self, request, pk, *args, **kwargs):
        try:
            comunidade = Comunidade.objects.get(pk=pk)
        except Comunidade.DoesNotExist:
            return Response({"erro": "Comunidade não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        try:
            ComunidadeService.sair(comunidade, request.user)
        except DRFValidationError as exc:
            return Response({"erro": exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as exc:
            return Response({"erro": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        return Response(
            ComunidadeSerializer(comunidade, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )


class ListarEncontrosView(APIView):
    """Lista encontros agendados de uma comunidade (público — qualquer um pode ver)."""

    permission_classes = []
    serializer_class = EncontroSerializer

    def get(self, request, pk, *args, **kwargs):
        try:
            comunidade = Comunidade.objects.get(pk=pk)
        except Comunidade.DoesNotExist:
            return Response({"erro": "Comunidade não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        encontros = comunidade.encontros.order_by('data_hr_encontro')
        return Response(
            EncontroSerializer(encontros, many=True, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )


class EncontrosPublicosView(APIView):
    """CDU005 - Lista os próximos encontros de todas as comunidades.

    `?minhas=1` restringe às comunidades das quais o usuário participa.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = EncontroSerializer

    def get(self, request, *args, **kwargs):
        encontros = (
            Encontro.objects
            .filter(data_hr_encontro__gte=timezone.now())
            .select_related('comunidade', 'criado_por')
            .order_by('data_hr_encontro')
        )
        if request.query_params.get('minhas') in ('1', 'true'):
            encontros = encontros.filter(comunidade__membros=request.user)
        return Response(
            EncontroSerializer(encontros, many=True, context={'request': request}).data,
        )


class CriarEncontroView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EncontroSerializer

    def post(self, request, pk, *args, **kwargs):
        try:
            comunidade = Comunidade.objects.get(pk=pk)
        except Comunidade.DoesNotExist:
            return Response({"erro": "Comunidade não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        serializer = EncontroSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            encontro = EncontroService.criar_encontro(serializer, comunidade, request.user)
        except PermissionDenied as exc:
            return Response({"erro": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except DRFValidationError as exc:
            return Response({"erro": exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"erro": "Erro ao salvar o encontro. Tente novamente mais tarde."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            EncontroSerializer(encontro, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class PostagensComunidadeView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PostagemSerializer

    def get_comunidade(self, pk):
        try:
            return Comunidade.objects.get(pk=pk)
        except Comunidade.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        comunidade = self.get_comunidade(pk)
        if comunidade is None:
            return Response({"erro": "Comunidade não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        postagens = comunidade.postagens.select_related('autor').prefetch_related(
            'curtidas', 'comentarios__autor', 'comentarios__curtidas',
            'comentarios__respostas__autor', 'comentarios__respostas__curtidas',
        ).all()
        serializer = PostagemSerializer(postagens, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, pk, *args, **kwargs):
        comunidade = self.get_comunidade(pk)
        if comunidade is None:
            return Response({"erro": "Comunidade não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PostagemSerializer(data=request.data)
        if serializer.is_valid():
            try:
                postagem = PostagemService.criar_postagem(comunidade, request.user, serializer)
            except PermissionDenied as exc:
                return Response({"erro": str(exc)}, status=status.HTTP_403_FORBIDDEN)
            return Response(PostagemSerializer(postagem, context={'request': request}).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ModeracaoComunidadeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DenunciaPostagemSerializer

    def get_comunidade(self, pk):
        try:
            return Comunidade.objects.get(pk=pk)
        except Comunidade.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        comunidade = self.get_comunidade(pk)
        if comunidade is None:
            return Response({"erro": "Comunidade não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        try:
            ModeracaoService.validar_moderador(comunidade, request.user)
        except PermissionDenied as exc:
            return Response({"erro": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        denuncias = comunidade.denuncias_postagens.filter(
            status=DenunciaPostagem.STATUS_PENDENTE,
        ).select_related(
            'denunciante', 'postagem', 'postagem__autor',
            'comentario', 'comentario__autor',
        )
        serializer = DenunciaPostagemSerializer(denuncias, many=True)
        return Response({
            'pendentes': serializer.data,
            'pendentes_count': denuncias.count(),
            'analisadas_count': comunidade.denuncias_postagens.exclude(
                status=DenunciaPostagem.STATUS_PENDENTE,
            ).count(),
        })

class AnalisarDenunciaPostagemView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DenunciaPostagemSerializer

    def post(self, request, pk, denuncia_id, acao, *args, **kwargs):
        try:
            denuncia = DenunciaPostagem.objects.select_related(
                'comunidade', 'postagem', 'postagem__autor',
                'comentario', 'comentario__autor', 'denunciante',
            ).get(pk=denuncia_id, comunidade_id=pk)
        except DenunciaPostagem.DoesNotExist:
            return Response({"erro": "Denúncia não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        try:
            if acao == 'aprovar':
                denuncia = ModeracaoService.aprovar_denuncia(denuncia, request.user)
                mensagem = 'Denúncia aprovada e postagem removida com sucesso.'
            elif acao == 'reprovar':
                denuncia = ModeracaoService.reprovar_denuncia(denuncia, request.user)
                mensagem = 'Denúncia reprovada e postagem mantida na comunidade.'
            else:
                return Response({"erro": "Ação inválida."}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as exc:
            return Response({"erro": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except DRFValidationError as exc:
            return Response({"erro": exc.detail}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'mensagem': mensagem,
            'denuncia': DenunciaPostagemSerializer(denuncia).data,
        })        

class InteracaoPostagemView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostagemSerializer

    def get_postagem(self, pk, postagem_id):
        try:
            return Postagem.objects.select_related('comunidade', 'autor').prefetch_related(
                'curtidas', 'comentarios__autor', 'comentarios__curtidas',
                'comentarios__respostas__autor', 'comentarios__respostas__curtidas',
            ).get(pk=postagem_id, comunidade_id=pk)
        except Postagem.DoesNotExist:
            return None

class CurtirPostagemView(InteracaoPostagemView):
    def post(self, request, pk, postagem_id, *args, **kwargs):
        postagem = self.get_postagem(pk, postagem_id)
        if postagem is None:
            return Response({"erro": "Postagem não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        try:
            curtido = InteracaoPostagemService.alternar_curtida(postagem, request.user)
        except PermissionDenied as exc:
            return Response({"erro": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        postagem = self.get_postagem(pk, postagem_id)
        return Response({
            'curtido': curtido,
            'postagem': PostagemSerializer(postagem, context={'request': request}).data,
        })

class ComentariosPostagemView(InteracaoPostagemView):
    serializer_class = ComentarioPostagemSerializer

    def get(self, request, pk, postagem_id, *args, **kwargs):
        postagem = self.get_postagem(pk, postagem_id)
        if postagem is None:
            return Response({"erro": "Postagem não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        raiz = postagem.comentarios.filter(parent__isnull=True).select_related('autor').prefetch_related(
            'curtidas', 'respostas__autor', 'respostas__curtidas',
        )
        serializer = ComentarioPostagemSerializer(raiz, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, pk, postagem_id, *args, **kwargs):
        postagem = self.get_postagem(pk, postagem_id)
        if postagem is None:
            return Response({"erro": "Postagem não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        parent = None
        parent_id = request.data.get('parent')
        if parent_id not in (None, '', 0, '0'):
            try:
                parent = postagem.comentarios.get(pk=parent_id)
            except ComentarioPostagem.DoesNotExist:
                return Response(
                    {"erro": "Comentário respondido não encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        serializer = ComentarioPostagemSerializer(data=request.data)
        if serializer.is_valid():
            try:
                InteracaoPostagemService.comentar(postagem, request.user, serializer, parent=parent)
            except PermissionDenied as exc:
                return Response({"erro": str(exc)}, status=status.HTTP_403_FORBIDDEN)
            postagem = self.get_postagem(pk, postagem_id)
            return Response(PostagemSerializer(postagem, context={'request': request}).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InteracaoComentarioView(InteracaoPostagemView):
    def get_comentario(self, pk, postagem_id, comentario_id):
        try:
            return ComentarioPostagem.objects.select_related(
                'postagem', 'postagem__comunidade', 'autor',
            ).get(pk=comentario_id, postagem_id=postagem_id, postagem__comunidade_id=pk)
        except ComentarioPostagem.DoesNotExist:
            return None


class CurtirComentarioView(InteracaoComentarioView):
    def post(self, request, pk, postagem_id, comentario_id, *args, **kwargs):
        comentario = self.get_comentario(pk, postagem_id, comentario_id)
        if comentario is None:
            return Response({"erro": "Comentário não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        try:
            curtido = InteracaoPostagemService.alternar_curtida_comentario(comentario, request.user)
        except PermissionDenied as exc:
            return Response({"erro": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        postagem = self.get_postagem(pk, postagem_id)
        return Response({
            'curtido': curtido,
            'postagem': PostagemSerializer(postagem, context={'request': request}).data,
        })


class DenunciarComentarioView(InteracaoComentarioView):
    serializer_class = DenunciaPostagemSerializer

    def post(self, request, pk, postagem_id, comentario_id, *args, **kwargs):
        comentario = self.get_comentario(pk, postagem_id, comentario_id)
        if comentario is None:
            return Response({"erro": "Comentário não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        try:
            denuncia = InteracaoPostagemService.denunciar_comentario(
                comentario,
                request.user,
                request.data.get('motivo', ''),
                request.data.get('detalhe', ''),
            )
        except PermissionDenied as exc:
            return Response({"erro": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except DRFValidationError as exc:
            return Response({"erro": exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'mensagem': 'Denúncia enviada com sucesso.',
            'denuncia': DenunciaPostagemSerializer(denuncia).data,
        }, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# CDU024 - Moderar Conviventes
# ---------------------------------------------------------------------------


class MembrosComunidadeView(APIView):
    """Lista membros da comunidade com seu status de moderação. Apenas moderador."""

    permission_classes = [IsModeradorDaComunidade]
    serializer_class = MembroComunidadeSerializer

    def get(self, request, pk, *args, **kwargs):
        comunidade = Comunidade.objects.get(pk=pk)  # IsModeradorDaComunidade já garantiu existência
        membros = comunidade.membros.all().order_by('nome', 'username')
        serializer = MembroComunidadeSerializer(
            membros, many=True, context={'comunidade': comunidade},
        )
        return Response(serializer.data)


class ModerarConviventeView(APIView):
    """Aplica ação de moderação (CDU024). Apenas moderador."""

    permission_classes = [IsModeradorDaComunidade]
    serializer_class = AplicarAcaoModeracaoSerializer

    def post(self, request, pk, *args, **kwargs):
        comunidade = Comunidade.objects.get(pk=pk)
        serializer = AplicarAcaoModeracaoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        dados = serializer.validated_data
        try:
            convivente = User.objects.get(pk=dados['convivente_id'])
        except User.DoesNotExist:
            return Response({"erro": "Convivente não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        try:
            acao = ModeracaoService.aplicar_acao(
                comunidade=comunidade,
                moderador=request.user,
                convivente=convivente,
                tipo=dados['tipo'],
                justificativa=dados.get('justificativa', ''),
                duracao_dias=dados.get('duracao_dias'),
            )
        except DRFValidationError as exc:
            return Response({"erro": exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"erro": "Não foi possível concluir a moderação. Tente novamente."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(AcaoModeracaoSerializer(acao).data, status=status.HTTP_201_CREATED)


class HistoricoConviventeView(APIView):
    """Histórico completo de ações sofridas por um convivente. Apenas moderador."""

    permission_classes = [IsModeradorDaComunidade]
    serializer_class = AcaoModeracaoSerializer

    def get(self, request, pk, convivente_id, *args, **kwargs):
        comunidade = Comunidade.objects.get(pk=pk)
        acoes = AcaoModeracao.objects.filter(
            comunidade=comunidade, convivente_id=convivente_id,
        ).order_by('-criado_em')
        return Response(AcaoModeracaoSerializer(acoes, many=True).data)


class DenunciarPostagemView(InteracaoPostagemView):
    serializer_class = DenunciaPostagemSerializer

    def post(self, request, pk, postagem_id, *args, **kwargs):
        postagem = self.get_postagem(pk, postagem_id)
        if postagem is None:
            return Response({"erro": "Postagem não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        try:
            denuncia = InteracaoPostagemService.denunciar(
                postagem,
                request.user,
                request.data.get('motivo', ''),
                request.data.get('detalhe', ''),
            )
        except PermissionDenied as exc:
            return Response({"erro": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except DRFValidationError as exc:
            return Response({"erro": exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'mensagem': 'Denúncia enviada com sucesso.',
            'denuncia': DenunciaPostagemSerializer(denuncia).data,
        }, status=status.HTTP_201_CREATED)        