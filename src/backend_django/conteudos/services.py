from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import ConteudoEducacional, Denuncia


class ConteudoEducacionalService:
    """Operações de leitura sobre conteúdos educacionais.

    A criação/edição/remoção é feita diretamente pelo ModelSerializer do DRF
    — ele já trata M2M corretamente e não há regra de domínio adicional além
    do "curador = request.user.curador", que é injetado em `perform_create`.
    """

    @staticmethod
    def listar_conteudos():
        return ConteudoEducacional.objects.all().order_by('-id')

    @staticmethod
    def obter_detalhe_conteudo(conteudo_id):
        try:
            return ConteudoEducacional.objects.get(id=conteudo_id)
        except ConteudoEducacional.DoesNotExist:
            return None


class DenunciaService:
    """Registra denúncias de conteúdos educacionais (CDU022)."""

    @staticmethod
    def registrar(*, conteudo, convivente, motivo, descricao=''):
        if not convivente or not convivente.is_authenticated:
            raise PermissionDenied('É necessário estar autenticado para denunciar.')
        if motivo not in dict(Denuncia.MOTIVO_CHOICES):
            raise ValidationError('Motivo inválido.')
        ja_pendente = Denuncia.objects.filter(
            conteudo=conteudo,
            convivente=convivente,
            status=Denuncia.STATUS_EM_ANALISE,
        ).exists()
        if ja_pendente:
            raise ValidationError(
                'Você já denunciou esse conteúdo. Aguarde a análise do curador.'
            )
        return Denuncia.objects.create(
            conteudo=conteudo,
            convivente=convivente,
            motivo=motivo,
            descricao=(descricao or '').strip(),
        )

    @staticmethod
    def minha_denuncia_pendente(conteudo, convivente):
        """Hook para o serializer: retorna a denúncia em análise do usuário, se houver."""
        if not convivente or not getattr(convivente, 'is_authenticated', False):
            return None
        # Em caminhos como create/update do DRF, o serializer pode acabar
        # serializando o validated_data (um dict) se o instance não estiver
        # setado. Aqui evitamos uma query que quebraria.
        if not getattr(conteudo, 'pk', None):
            return None
        return (
            Denuncia.objects
            .filter(
                conteudo=conteudo,
                convivente=convivente,
                status=Denuncia.STATUS_EM_ANALISE,
            )
            .order_by('-criado_em')
            .first()
        )
