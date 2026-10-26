from datetime import timedelta

from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from config import limites

from .models import AcaoModeracao, DenunciaPostagem


MAX_IMAGEM_BYTES = 5 * 1024 * 1024
FORMATOS_IMAGEM_PERMITIDOS = ('image/jpeg', 'image/png', 'image/webp')


class ComunidadeService:
    @staticmethod
    def validar_imagem(arquivo, campo):
        if arquivo is None:
            return
        if arquivo.size > MAX_IMAGEM_BYTES:
            raise ValidationError({campo: 'A imagem deve ter no máximo 5 MB.'})
        content_type = getattr(arquivo, 'content_type', None)
        if content_type and content_type not in FORMATOS_IMAGEM_PERMITIDOS:
            raise ValidationError({campo: 'Arquivo de imagem inválido. Use JPG, PNG ou WEBP.'})

    @staticmethod
    def criar_comunidade(serializer, moderador, icone=None, banner=None):
        ComunidadeService.validar_imagem(icone, 'icone')
        ComunidadeService.validar_imagem(banner, 'banner')
        extras = {}
        if icone:
            extras['icone'] = icone
        if banner:
            extras['banner'] = banner
        comunidade = serializer.save(moderador=moderador, **extras)
        comunidade.membros.add(moderador)
        return comunidade

    @staticmethod
    def validar_moderador(comunidade, usuario):
        if not usuario or not usuario.is_authenticated:
            raise PermissionDenied('É necessário estar autenticado.')
        if comunidade.moderador_id != usuario.pk:
            raise PermissionDenied('Apenas o moderador da comunidade pode gerenciá-la.')

    @staticmethod
    def atualizar_comunidade(comunidade, usuario, serializer, *, icone=None, banner=None,
                             remover_icone=False, remover_banner=False):
        """CDU012 - Fluxo Principal: o moderador altera as informações da comunidade.

        Uma imagem nova substitui a anterior (o arquivo antigo é apagado do
        disco); `remover_*` volta ao visual padrão sem imagem.
        """
        ComunidadeService.validar_moderador(comunidade, usuario)
        ComunidadeService.validar_imagem(icone, 'icone')
        ComunidadeService.validar_imagem(banner, 'banner')

        antigos = []
        extras = {}
        for campo, novo, remover in (
            ('icone', icone, remover_icone),
            ('banner', banner, remover_banner),
        ):
            atual = getattr(comunidade, campo)
            if novo or remover:
                if atual:
                    antigos.append(atual.name)
                extras[campo] = novo or None

        comunidade = serializer.save(**extras)

        storage = comunidade.icone.storage
        for nome in antigos:
            if nome and storage.exists(nome):
                storage.delete(nome)
        return comunidade

    @staticmethod
    def excluir_comunidade(comunidade, usuario):
        """CDU012 - Fluxo Alternativo I: o moderador remove a comunidade.

        Postagens, comentários, encontros, denúncias e histórico de moderação
        são removidos em cascata; os arquivos de imagem também saem do disco.
        """
        ComunidadeService.validar_moderador(comunidade, usuario)
        arquivos = [comunidade.icone, comunidade.banner]
        arquivos += [encontro.img for encontro in comunidade.encontros.all()]
        nomes = [(arquivo.storage, arquivo.name) for arquivo in arquivos if arquivo]

        comunidade.delete()

        for storage, nome in nomes:
            if storage.exists(nome):
                storage.delete(nome)

    @staticmethod
    def participar(comunidade, usuario):
        if not usuario or not usuario.is_authenticated:
            raise PermissionDenied("É necessário estar autenticado para participar.")
        if comunidade.banidos.filter(pk=usuario.pk).exists():
            raise PermissionDenied("Você foi banido desta comunidade.")
        if comunidade.moderador_id == usuario.pk:
            raise ValidationError("O moderador já é membro da comunidade.")
        if comunidade.membros.filter(pk=usuario.pk).exists():
            raise ValidationError("Você já é membro desta comunidade.")
        comunidade.membros.add(usuario)
        return comunidade

    @staticmethod
    def sair(comunidade, usuario):
        if not usuario or not usuario.is_authenticated:
            raise PermissionDenied("É necessário estar autenticado.")
        if comunidade.moderador_id == usuario.pk:
            raise ValidationError("O moderador não pode sair da própria comunidade.")
        if not comunidade.membros.filter(pk=usuario.pk).exists():
            raise ValidationError("Você não é membro desta comunidade.")
        comunidade.membros.remove(usuario)
        return comunidade


class ModeracaoService:
    """Aplica ações de moderação (CDU024) sobre conviventes de uma comunidade."""

    @staticmethod
    def aplicar_acao(*, comunidade, moderador, convivente, tipo, justificativa='', duracao_dias=None):
        if convivente.pk == comunidade.moderador_id:
            raise ValidationError("O moderador não pode moderar a si mesmo.")
        if not comunidade.membros.filter(pk=convivente.pk).exists():
            raise ValidationError("O convivente não é membro desta comunidade.")

        justificativa = (justificativa or '').strip()
        expira_em = None

        if tipo == AcaoModeracao.TIPO_RESTRINGIR:
            if not duracao_dias or duracao_dias <= 0:
                raise ValidationError("Duração obrigatória (em dias) para restrição.")
            expira_em = timezone.now() + timedelta(days=duracao_dias)
        elif tipo == AcaoModeracao.TIPO_BANIR:
            if not justificativa:
                raise ValidationError("Justificativa é obrigatória para banimento.")
            duracao_dias = None
        else:
            raise ValidationError("Tipo de ação inválido.")

        acao = AcaoModeracao.objects.create(
            comunidade=comunidade,
            moderador=moderador,
            convivente=convivente,
            tipo=tipo,
            justificativa=justificativa,
            duracao_dias=duracao_dias,
            expira_em=expira_em,
        )

        if tipo == AcaoModeracao.TIPO_BANIR:
            comunidade.membros.remove(convivente)
            comunidade.banidos.add(convivente)

        return acao

    @staticmethod
    def restricao_ativa(comunidade, convivente):
        """Hook para o CDU de Postar Conteúdo: retorna a restrição ativa, se houver."""
        agora = timezone.now()
        return (
            AcaoModeracao.objects
            .filter(
                comunidade=comunidade,
                convivente=convivente,
                tipo=AcaoModeracao.TIPO_RESTRINGIR,
                expira_em__gt=agora,
            )
            .order_by('-expira_em')
            .first()
        )

    @staticmethod
    def validar_moderador(comunidade, usuario):
        if not usuario or not usuario.is_authenticated:
            raise PermissionDenied('É necessário estar autenticado para moderar.')
        if comunidade.moderador_id != usuario.pk:
            raise PermissionDenied('Apenas o moderador da comunidade pode analisar denúncias.')

    @staticmethod
    def aprovar_denuncia(denuncia, moderador):
        ModeracaoService.validar_moderador(denuncia.comunidade, moderador)
        if denuncia.status != DenunciaPostagem.STATUS_PENDENTE:
            raise ValidationError('Esta denúncia já foi analisada.')

        postagem = denuncia.postagem
        comentario = denuncia.comentario
        eh_comentario = denuncia.comentario_id is not None

        denuncia.status = DenunciaPostagem.STATUS_APROVADA
        denuncia.analisado_por = moderador
        denuncia.analisado_em = timezone.now()
        denuncia.acao_registrada = (
            'Denúncia aprovada e comentário removido.'
            if eh_comentario
            else 'Denúncia aprovada e postagem removida.'
        )
        denuncia.save(update_fields=['status', 'analisado_por', 'analisado_em', 'acao_registrada'])

        # Outras denúncias pendentes sobre o mesmo item (ou, no caso de uma
        # postagem, sobre seus comentários) perderiam o alvo com a remoção e
        # ficariam "órfãs" na fila: resolvemos todas junto.
        pendentes = DenunciaPostagem.objects.filter(
            status=DenunciaPostagem.STATUS_PENDENTE,
        ).exclude(pk=denuncia.pk)
        if eh_comentario:
            pendentes = pendentes.filter(comentario=comentario) if comentario else pendentes.none()
        else:
            pendentes = pendentes.filter(postagem=postagem) if postagem else pendentes.none()
        pendentes.update(
            status=DenunciaPostagem.STATUS_APROVADA,
            analisado_por=moderador,
            analisado_em=denuncia.analisado_em,
            acao_registrada=denuncia.acao_registrada,
        )

        if eh_comentario:
            if comentario:
                comentario.delete()
        elif postagem:
            postagem.delete()
        return denuncia

    @staticmethod
    def reprovar_denuncia(denuncia, moderador):
        ModeracaoService.validar_moderador(denuncia.comunidade, moderador)
        if denuncia.status != DenunciaPostagem.STATUS_PENDENTE:
            raise ValidationError('Esta denúncia já foi analisada.')

        denuncia.status = DenunciaPostagem.STATUS_REPROVADA
        denuncia.analisado_por = moderador
        denuncia.analisado_em = timezone.now()
        denuncia.acao_registrada = (
            'Denúncia reprovada e comentário mantido na comunidade.'
            if denuncia.comentario_id is not None
            else 'Denúncia reprovada e postagem mantida na comunidade.'
        )
        denuncia.save(update_fields=['status', 'analisado_por', 'analisado_em', 'acao_registrada'])
        return denuncia


class PostagemService:
    @staticmethod
    def validar_sem_restricao(comunidade, usuario):
        """CDU024: convivente restringido não publica (postagem nem comentário)."""
        restricao = ModeracaoService.restricao_ativa(comunidade, usuario)
        if restricao is not None:
            data = timezone.localtime(restricao.expira_em).strftime('%d/%m/%Y')
            raise PermissionDenied(
                f'Você está restrito de postar nesta comunidade até {data}.'
            )

    @staticmethod
    def criar_postagem(comunidade, usuario, serializer):
        if not usuario or not usuario.is_authenticated:
            raise PermissionDenied('É necessário estar autenticado para publicar.')
        if not comunidade.membros.filter(pk=usuario.pk).exists():
            raise PermissionDenied('Você precisa participar da comunidade para publicar conteúdos')
        PostagemService.validar_sem_restricao(comunidade, usuario)
        return serializer.save(comunidade=comunidade, autor=usuario)


class EncontroService:
    @staticmethod
    def criar_encontro(serializer, comunidade, usuario):
        """Cria um encontro dentro de uma comunidade (CDU010).

        Pré-condição: o usuário precisa ser o moderador da comunidade.
        """
        if not usuario or not usuario.is_authenticated:
            raise PermissionDenied("É necessário estar autenticado.")
        if comunidade.moderador_id != usuario.pk:
            raise PermissionDenied("Apenas o moderador da comunidade pode criar encontros.")
        return serializer.save(comunidade=comunidade, criado_por=usuario)


class InteracaoPostagemService:
    @staticmethod
    def validar_denuncia(motivo, detalhe, alvo):
        motivo_limpo = motivo.strip() if motivo else ''
        if not motivo_limpo:
            raise ValidationError(f'Selecione um motivo para denunciar {alvo}.')
        if len(motivo_limpo) > 120:
            raise ValidationError('O motivo deve ter no máximo 120 caracteres.')
        detalhe_limpo = (detalhe or '').strip()
        if len(detalhe_limpo) > limites.DENUNCIA_DETALHE:
            raise ValidationError(f'O detalhe deve ter no máximo {limites.DENUNCIA_DETALHE} caracteres.')
        return motivo_limpo, detalhe_limpo

    @staticmethod
    def validar_membro(comunidade, usuario):
        if not usuario or not usuario.is_authenticated:
            raise PermissionDenied('É necessário estar autenticado para interagir com a postagem.')
        if not comunidade.membros.filter(pk=usuario.pk).exists():
            raise PermissionDenied('Você precisa participar da comunidade para interagir com a postagem.')

    @staticmethod
    def alternar_curtida(postagem, usuario):
        InteracaoPostagemService.validar_membro(postagem.comunidade, usuario)
        if postagem.curtidas.filter(pk=usuario.pk).exists():
            postagem.curtidas.remove(usuario)
            curtido = False
        else:
            postagem.curtidas.add(usuario)
            curtido = True
        return curtido

    @staticmethod
    def comentar(postagem, usuario, serializer, parent=None):
        InteracaoPostagemService.validar_membro(postagem.comunidade, usuario)
        PostagemService.validar_sem_restricao(postagem.comunidade, usuario)
        # 1 nível de aninhamento: responder a uma resposta re-ancora no comentário-raiz.
        if parent is not None and parent.parent_id is not None:
            parent = parent.parent
        return serializer.save(postagem=postagem, autor=usuario, parent=parent)

    @staticmethod
    def alternar_curtida_comentario(comentario, usuario):
        InteracaoPostagemService.validar_membro(comentario.postagem.comunidade, usuario)
        if comentario.curtidas.filter(pk=usuario.pk).exists():
            comentario.curtidas.remove(usuario)
            curtido = False
        else:
            comentario.curtidas.add(usuario)
            curtido = True
        return curtido

    @staticmethod
    def denunciar_comentario(comentario, usuario, motivo, detalhe=''):
        InteracaoPostagemService.validar_membro(comentario.postagem.comunidade, usuario)
        motivo_limpo, detalhe_limpo = InteracaoPostagemService.validar_denuncia(motivo, detalhe, 'o comentário')
        return DenunciaPostagem.objects.create(
            comunidade=comentario.postagem.comunidade,
            # Guarda também a postagem: se ela for removida por outra denúncia,
            # esta é resolvida junto em vez de ficar órfã.
            postagem=comentario.postagem,
            comentario=comentario,
            denunciante=usuario,
            motivo=motivo_limpo,
            detalhe=detalhe_limpo,
        )

    @staticmethod
    def denunciar(postagem, usuario, motivo, detalhe=''):
        InteracaoPostagemService.validar_membro(postagem.comunidade, usuario)
        motivo_limpo, detalhe_limpo = InteracaoPostagemService.validar_denuncia(motivo, detalhe, 'a postagem')
        return DenunciaPostagem.objects.create(
            comunidade=postagem.comunidade,
            postagem=postagem,
            denunciante=usuario,
            motivo=motivo_limpo,
            detalhe=detalhe_limpo,
        )        

