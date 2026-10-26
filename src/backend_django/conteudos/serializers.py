from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from config import limites

from usuarios.models import Curador

from .models import ConteudoEducacional, Denuncia, Tags
from .services import DenunciaService


# 1. Serializer das Tags (ok)
class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ['id', 'nome']
        extra_kwargs = {'nome': {'max_length': limites.TAG_NOME}}


# 2. Serializer do Curador
class CuradorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curador
        fields = ['id', 'nome', 'especialidade']


# 3. Serializer da Denúncia (saída — usado no POST e em listagens futuras)
class DenunciaSerializer(serializers.ModelSerializer):
    convivente = serializers.StringRelatedField(read_only=True)
    motivo_display = serializers.CharField(source='get_motivo_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Denuncia
        fields = [
            'id', 'conteudo', 'convivente', 'motivo', 'motivo_display',
            'descricao', 'status', 'status_display', 'criado_em',
        ]
        read_only_fields = fields


# 4. Serializer de entrada (registrar denúncia)
class RegistrarDenunciaSerializer(serializers.Serializer):
    motivo = serializers.ChoiceField(choices=Denuncia.MOTIVO_CHOICES)
    descricao = serializers.CharField(
        required=False, allow_blank=True, default='', max_length=limites.DENUNCIA_DETALHE,
    )


class MinhaDenunciaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    motivo = serializers.CharField()
    motivo_display = serializers.CharField()
    status = serializers.CharField()
    criado_em = serializers.DateTimeField()


# 5. Serializer do Conteúdo
class ConteudoEducacionalSerializer(serializers.ModelSerializer):
    tipos = TagsSerializer(many=True, read_only=True)
    curador = CuradorSerializer(read_only=True)
    minha_denuncia = serializers.SerializerMethodField()

    tipos_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True,
        write_only=True,
        source='tipos',
    )

    class Meta:
        model = ConteudoEducacional
        fields = [
            'id', 'titulo', 'fonte', 'descricao',
            'tipos', 'tipos_ids', 'curador', 'minha_denuncia',
            'criado_em',
        ]
        read_only_fields = ('criado_em',)
        extra_kwargs = {
            'titulo': {'max_length': limites.CONTEUDO_TITULO},
            'fonte': {'max_length': limites.CONTEUDO_FONTE},
            'descricao': {'max_length': limites.CONTEUDO_DESCRICAO},
        }

    @extend_schema_field(MinhaDenunciaSerializer(allow_null=True))
    def get_minha_denuncia(self, obj):
        """Devolve a denúncia em análise do usuário autenticado, se existir."""
        request = self.context.get('request') if hasattr(self, 'context') else None
        user = getattr(request, 'user', None) if request else None
        if not user or not user.is_authenticated:
            return None
        denuncia = DenunciaService.minha_denuncia_pendente(obj, user)
        if not denuncia:
            return None
        return {
            'id': denuncia.id,
            'motivo': denuncia.motivo,
            'motivo_display': denuncia.get_motivo_display(),
            'status': denuncia.status,
            'criado_em': denuncia.criado_em,
        }
