from django.utils import timezone
from rest_framework import serializers

from config import limites

from .categorias import CATEGORIAS

from .models import AcaoModeracao, ComentarioPostagem, Comunidade, Encontro, DenunciaPostagem, Postagem


class ComunidadeSerializer(serializers.ModelSerializer):
    icone = serializers.SerializerMethodField()
    banner = serializers.SerializerMethodField()    
    moderador = serializers.StringRelatedField(read_only=True)
    membros_count = serializers.SerializerMethodField()
    is_membro = serializers.SerializerMethodField()
    is_moderador = serializers.SerializerMethodField()
    minha_restricao = serializers.SerializerMethodField()
    fui_banido = serializers.SerializerMethodField()

    class Meta:
        model = Comunidade
        fields = [
            'id', 'nome', 'descricao', 'categoria', 'regras', 'icone', 'banner',
            'moderador', 'criado_em', 'membros_count',
            'is_membro', 'is_moderador', 'minha_restricao', 'fui_banido',
        ]
        read_only_fields = [
            'id', 'icone', 'banner', 'moderador', 'criado_em',
            'membros_count', 'is_membro', 'is_moderador',
            'minha_restricao', 'fui_banido',
        ]
        extra_kwargs = {
            'nome': {'max_length': limites.COMUNIDADE_NOME},
            'descricao': {'max_length': limites.COMUNIDADE_DESCRICAO},
            'categoria': {'max_length': limites.COMUNIDADE_CATEGORIA},
            'regras': {'max_length': limites.COMUNIDADE_REGRAS},
        }

    def _media_url(self, arquivo):
        if not arquivo:
            return None
        try:
            return arquivo.url
        except ValueError:
            return None

    def get_icone(self, obj):
        return self._media_url(obj.icone)

    def get_banner(self, obj):
        return self._media_url(obj.banner)

    def validate_categoria(self, value):
        if value not in CATEGORIAS:
            raise serializers.ValidationError('Escolha uma das categorias da lista.')
        return value

    def validate_nome(self, value):
        instance = getattr(self, 'instance', None)
        qs = Comunidade.objects.filter(nome__iexact=value)
        if instance is not None:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Já existe uma comunidade com esse nome.")
        return value

    def get_membros_count(self, obj):
        return obj.membros.count()

    def _request_user(self):
        request = self.context.get('request') if hasattr(self, 'context') else None
        if not request:
            return None
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            return user
        return None

    def get_is_membro(self, obj):
        user = self._request_user()
        if user is None:
            return False
        return obj.membros.filter(pk=user.pk).exists()

    def get_is_moderador(self, obj):
        user = self._request_user()
        if user is None:
            return False
        return obj.moderador_id == user.pk

    def get_fui_banido(self, obj):
        user = self._request_user()
        if user is None:
            return False
        return obj.banidos.filter(pk=user.pk).exists()

    def get_minha_restricao(self, obj):
        user = self._request_user()
        if user is None:
            return None
        ativa = (
            AcaoModeracao.objects
            .filter(
                comunidade=obj,
                convivente=user,
                tipo=AcaoModeracao.TIPO_RESTRINGIR,
                expira_em__gt=timezone.now(),
            )
            .order_by('-expira_em')
            .first()
        )
        if not ativa:
            return None
        return {
            'expira_em': ativa.expira_em,
            'duracao_dias': ativa.duracao_dias,
            'justificativa': ativa.justificativa,
        }


class EditarComunidadeSerializer(serializers.Serializer):
    """Documenta (Swagger) o PATCH de comunidade (CDU012). Todos os campos são opcionais."""

    nome = serializers.CharField(required=False, max_length=limites.COMUNIDADE_NOME)
    descricao = serializers.CharField(required=False, max_length=limites.COMUNIDADE_DESCRICAO)
    categoria = serializers.ChoiceField(required=False, choices=CATEGORIAS)
    regras = serializers.CharField(required=False, allow_blank=True, max_length=limites.COMUNIDADE_REGRAS)
    icone = serializers.ImageField(required=False)
    banner = serializers.ImageField(required=False)
    remover_icone = serializers.BooleanField(required=False)
    remover_banner = serializers.BooleanField(required=False)


class AcaoModeracaoSerializer(serializers.ModelSerializer):
    moderador = serializers.StringRelatedField(read_only=True)
    convivente = serializers.StringRelatedField(read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = AcaoModeracao
        fields = [
            'id', 'tipo', 'tipo_display', 'justificativa', 'duracao_dias',
            'expira_em', 'criado_em', 'moderador', 'convivente',
        ]


class MembroComunidadeSerializer(serializers.Serializer):
    """Representa um membro com seu status atual de moderação."""

    id = serializers.IntegerField()
    username = serializers.CharField()
    nome = serializers.CharField()
    is_moderador = serializers.SerializerMethodField()
    restricao_ativa = serializers.SerializerMethodField()
    acoes_count = serializers.SerializerMethodField()  # total de ações sofridas no histórico

    def get_is_moderador(self, obj):
        comunidade = self.context.get('comunidade')
        return bool(comunidade and comunidade.moderador_id == obj.pk)

    def get_restricao_ativa(self, obj):
        comunidade = self.context.get('comunidade')
        if not comunidade:
            return None
        ativa = (
            AcaoModeracao.objects
            .filter(
                comunidade=comunidade,
                convivente=obj,
                tipo=AcaoModeracao.TIPO_RESTRINGIR,
                expira_em__gt=timezone.now(),
            )
            .order_by('-expira_em')
            .first()
        )
        if not ativa:
            return None
        return {
            'expira_em': ativa.expira_em,
            'duracao_dias': ativa.duracao_dias,
            'justificativa': ativa.justificativa,
        }

    def get_acoes_count(self, obj):
        comunidade = self.context.get('comunidade')
        if not comunidade:
            return 0
        return AcaoModeracao.objects.filter(
            comunidade=comunidade, convivente=obj,
        ).count()


class AplicarAcaoModeracaoSerializer(serializers.Serializer):
    convivente_id = serializers.IntegerField()
    tipo = serializers.ChoiceField(choices=AcaoModeracao.TIPO_CHOICES)
    justificativa = serializers.CharField(
        required=False, allow_blank=True, default='', max_length=limites.JUSTIFICATIVA,
    )
    duracao_dias = serializers.IntegerField(required=False, allow_null=True, min_value=1)


class ComentarioPostagemSerializer(serializers.ModelSerializer):
    autor = serializers.StringRelatedField(read_only=True)
    autor_username = serializers.CharField(source='autor.username', read_only=True)
    curtidas_count = serializers.SerializerMethodField()
    curtido_por_mim = serializers.SerializerMethodField()
    respostas_count = serializers.SerializerMethodField()
    respostas = serializers.SerializerMethodField()

    class Meta:
        model = ComentarioPostagem
        fields = [
            'id', 'postagem', 'parent', 'autor', 'autor_username', 'conteudo', 'criado_em',
            'curtidas_count', 'curtido_por_mim', 'respostas_count', 'respostas',
        ]
        read_only_fields = [
            'id', 'postagem', 'parent', 'autor', 'autor_username', 'criado_em',
            'curtidas_count', 'curtido_por_mim', 'respostas_count', 'respostas',
        ]
        extra_kwargs = {
            'conteudo': {'max_length': limites.COMENTARIO},
        }

    def validate_conteudo(self, value):
        conteudo = value.strip() if value else ''
        if not conteudo:
            raise serializers.ValidationError('Não foi possível publicar seu comentário. Verifique o conteúdo e tente novamente.')
        return conteudo

    def _request_user(self):
        request = self.context.get('request') if hasattr(self, 'context') else None
        user = getattr(request, 'user', None) if request else None
        if user and user.is_authenticated:
            return user
        return None

    def get_curtidas_count(self, obj):
        return obj.curtidas.count()

    def get_curtido_por_mim(self, obj):
        user = self._request_user()
        if user is None:
            return False
        return obj.curtidas.filter(pk=user.pk).exists()

    def get_respostas_count(self, obj):
        # 1 nível de aninhamento: só comentários-raiz têm respostas.
        if obj.parent_id is not None:
            return 0
        return obj.respostas.count()

    def get_respostas(self, obj):
        if obj.parent_id is not None:
            return []
        filhos = obj.respostas.select_related('autor').prefetch_related('curtidas')
        return ComentarioPostagemSerializer(filhos, many=True, context=self.context).data

class PostagemSerializer(serializers.ModelSerializer):
    autor = serializers.StringRelatedField(read_only=True)
    # `autor` é o nome de exibição; o username identifica o autor sem ambiguidade.
    autor_username = serializers.CharField(source='autor.username', read_only=True)
    curtidas_count = serializers.SerializerMethodField()
    comentarios_count = serializers.SerializerMethodField()
    curtido_por_mim = serializers.SerializerMethodField()
    comentarios = serializers.SerializerMethodField()

    class Meta:
        model = Postagem
        fields = [
            'id', 'comunidade', 'autor', 'autor_username', 'titulo', 'conteudo', 'criado_em',
            'curtidas_count', 'comentarios_count', 'curtido_por_mim', 'comentarios',
        ]
        read_only_fields = [
            'id', 'comunidade', 'autor', 'autor_username', 'criado_em', 'curtidas_count',
            'comentarios_count', 'curtido_por_mim', 'comentarios',
        ]
        extra_kwargs = {
            'titulo': {'max_length': limites.POSTAGEM_TITULO},
            'conteudo': {'max_length': limites.POSTAGEM_CONTEUDO},
        }

    def validate_titulo(self, value):
        titulo = value.strip() if value else ''
        if not titulo:
            raise serializers.ValidationError('O título da postagem é obrigatório.')
        return titulo

    def validate_conteudo(self, value):
        conteudo = value.strip() if value else ''
        if not conteudo:
            raise serializers.ValidationError('O conteúdo da postagem não pode estar vazio')
        return conteudo

    def get_curtidas_count(self, obj):
        return obj.curtidas.count()

    def get_comentarios_count(self, obj):
        return obj.comentarios.count()

    def get_comentarios(self, obj):
        raiz = (
            obj.comentarios.filter(parent__isnull=True)
            .select_related('autor')
            .prefetch_related('curtidas', 'respostas__autor', 'respostas__curtidas')
        )
        return ComentarioPostagemSerializer(raiz, many=True, context=self.context).data

    def get_curtido_por_mim(self, obj):
        request = self.context.get('request') if hasattr(self, 'context') else None
        user = getattr(request, 'user', None) if request else None
        if not user or not user.is_authenticated:
            return False
        return obj.curtidas.filter(pk=user.pk).exists()     


class EncontroSerializer(serializers.ModelSerializer):
    comunidade = serializers.StringRelatedField(read_only=True)
    comunidade_id = serializers.IntegerField(read_only=True)
    criado_por = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Encontro
        fields = [
            'id', 'comunidade', 'comunidade_id', 'titulo', 'descricao', 'data_hr_encontro',
            'endereco', 'tags', 'img', 'criado_por', 'criado_em',
        ]
        read_only_fields = [
            'id', 'comunidade', 'comunidade_id', 'criado_por', 'criado_em',
        ]
        extra_kwargs = {
            'titulo': {'max_length': limites.ENCONTRO_TITULO},
            'descricao': {'max_length': limites.ENCONTRO_DESCRICAO},
            'endereco': {'max_length': limites.ENCONTRO_ENDERECO},
            'tags': {'max_length': limites.ENCONTRO_TAGS},
        }

    def to_representation(self, instance):
        dados = super().to_representation(instance)
        # URL relativa, igual às demais mídias (ícone, banner, foto).
        dados['img'] = instance.img.url if instance.img else None
        return dados

    def validate_titulo(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("O título é obrigatório.")
        return value.strip()

    def validate_endereco(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("O endereço é obrigatório.")
        return value.strip()    

class DenunciaPostagemSerializer(serializers.ModelSerializer):
    denunciante = serializers.StringRelatedField(read_only=True)
    alvo_tipo = serializers.SerializerMethodField()
    postagem_titulo = serializers.SerializerMethodField()
    postagem_conteudo = serializers.SerializerMethodField()
    postagem_autor = serializers.SerializerMethodField()
    postagem_criado_em = serializers.SerializerMethodField()
    comentario_conteudo = serializers.SerializerMethodField()
    comentario_autor = serializers.SerializerMethodField()

    class Meta:
        model = DenunciaPostagem
        fields = [
            'id', 'comunidade', 'alvo_tipo', 'postagem', 'postagem_titulo', 'postagem_conteudo',
            'postagem_autor', 'postagem_criado_em', 'comentario', 'comentario_conteudo',
            'comentario_autor', 'denunciante', 'motivo', 'detalhe',
            'status', 'criado_em', 'analisado_por', 'analisado_em', 'acao_registrada',
        ]
        read_only_fields = fields

    def get_alvo_tipo(self, obj):
        return 'comentario' if obj.comentario_id else 'postagem'

    def get_postagem_titulo(self, obj):
        return obj.postagem.titulo if obj.postagem else 'Postagem removida'

    def get_postagem_conteudo(self, obj):
        return obj.postagem.conteudo if obj.postagem else ''

    def get_postagem_autor(self, obj):
        return str(obj.postagem.autor) if obj.postagem else 'Autor indisponível'

    def get_postagem_criado_em(self, obj):
        return obj.postagem.criado_em if obj.postagem else None

    def get_comentario_conteudo(self, obj):
        return obj.comentario.conteudo if obj.comentario else 'Comentário removido'

    def get_comentario_autor(self, obj):
        return str(obj.comentario.autor) if obj.comentario else 'Autor indisponível'