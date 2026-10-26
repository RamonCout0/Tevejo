from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.test import RequestFactory, TestCase
from django.utils import timezone

from .models import AcaoModeracao, Comunidade, Postagem
from .serializers import ComunidadeSerializer


Usuario = get_user_model()


class ComunidadeModelTestCase(TestCase):
    """Testes unitários do model Comunidade."""

    def setUp(self):
        self.moderador = Usuario.objects.create_user(
            username='moderador', email='moderador@example.com', password='senha-segura'
        )
        self.convivente = Usuario.objects.create_user(
            username='convivente', email='convivente@example.com', password='senha-segura'
        )
        self.comunidade = Comunidade.objects.create(
            nome='Apoio Visual',
            descricao='Comunidade de apoio a pessoas com deficiência visual.',
            categoria='Apoio',
            moderador=self.moderador,
        )

    def test_cria_comunidade_com_campos_obrigatorios(self):
        self.assertEqual(self.comunidade.nome, 'Apoio Visual')
        self.assertEqual(self.comunidade.categoria, 'Apoio')
        self.assertEqual(self.comunidade.moderador, self.moderador)
        self.assertEqual(self.comunidade.regras, '')
        self.assertFalse(self.comunidade.icone)
        self.assertFalse(self.comunidade.banner)
        self.assertIsNotNone(self.comunidade.criado_em)

    def test_str_retorna_nome(self):
        self.assertEqual(str(self.comunidade), 'Apoio Visual')

    def test_meta_verbose_names(self):
        self.assertEqual(Comunidade._meta.verbose_name, 'Comunidade')
        self.assertEqual(Comunidade._meta.verbose_name_plural, 'Comunidades')

    def test_nome_deve_ser_unico(self):
        with self.assertRaises(IntegrityError):
            Comunidade.objects.create(
                nome='Apoio Visual',
                descricao='Outra descrição',
                categoria='Lazer',
                moderador=self.convivente,
            )

    def test_nome_respeita_tamanho_maximo(self):
        comunidade = Comunidade(
            nome='a' * 151,
            descricao='Descrição',
            categoria='Apoio',
            moderador=self.moderador,
        )

        with self.assertRaises(ValidationError) as contexto:
            comunidade.full_clean()
        self.assertIn('nome', contexto.exception.message_dict)

    def test_campos_obrigatorios_nao_podem_ficar_vazios(self):
        comunidade = Comunidade(nome='', descricao='', categoria='', moderador=self.moderador)

        with self.assertRaises(ValidationError) as contexto:
            comunidade.full_clean()
        erros = contexto.exception.message_dict
        self.assertIn('nome', erros)
        self.assertIn('descricao', erros)
        self.assertIn('categoria', erros)
        self.assertNotIn('regras', erros)

    def test_membros_e_related_name(self):
        self.comunidade.membros.add(self.convivente)

        self.assertIn(self.convivente, self.comunidade.membros.all())
        self.assertIn(self.comunidade, self.convivente.comunidades_participadas.all())

    def test_banidos_e_related_name(self):
        self.comunidade.banidos.add(self.convivente)

        self.assertIn(self.convivente, self.comunidade.banidos.all())
        self.assertIn(self.comunidade, self.convivente.banimentos_em_comunidades.all())
        self.assertNotIn(self.convivente, self.comunidade.membros.all())

    def test_moderador_protegido_contra_exclusao(self):
        with self.assertRaises(ProtectedError):
            self.moderador.delete()

    def test_excluir_comunidade_remove_postagens(self):
        Postagem.objects.create(
            comunidade=self.comunidade,
            autor=self.convivente,
            titulo='Olá',
            conteudo='Primeira postagem',
        )

        self.comunidade.delete()

        self.assertFalse(Postagem.objects.exists())


class ComunidadeSerializerTestCase(TestCase):
    """Testes unitários do ComunidadeSerializer."""

    def setUp(self):
        self.factory = RequestFactory()
        self.moderador = Usuario.objects.create_user(
            username='moderador', email='moderador@example.com',
            password='senha-segura', nome='Moderador Teste',
        )
        self.convivente = Usuario.objects.create_user(
            username='convivente', email='convivente@example.com', password='senha-segura'
        )
        self.comunidade = Comunidade.objects.create(
            nome='Apoio Visual',
            descricao='Comunidade de apoio a pessoas com deficiência visual.',
            categoria='Apoio',
            regras='Respeite todos.',
            moderador=self.moderador,
        )

    def _contexto(self, usuario):
        request = self.factory.get('/')
        request.user = usuario
        return {'request': request}

    def _serializar(self, usuario=None):
        contexto = self._contexto(usuario) if usuario is not None else {}
        return ComunidadeSerializer(self.comunidade, context=contexto).data

    def test_serializa_campos_esperados(self):
        dados = self._serializar()

        self.assertEqual(set(dados.keys()), {
            'id', 'nome', 'descricao', 'categoria', 'regras', 'icone', 'banner',
            'moderador', 'criado_em', 'membros_count',
            'is_membro', 'is_moderador', 'minha_restricao', 'fui_banido',
        })
        self.assertEqual(dados['nome'], 'Apoio Visual')
        self.assertEqual(dados['regras'], 'Respeite todos.')
        self.assertEqual(dados['moderador'], 'Moderador Teste')

    def test_icone_e_banner_nulos_quando_vazios(self):
        dados = self._serializar()

        self.assertIsNone(dados['icone'])
        self.assertIsNone(dados['banner'])

    def test_icone_e_banner_retornam_url(self):
        self.comunidade.icone.name = 'comunidades/icones/icone.png'
        self.comunidade.banner.name = 'comunidades/banners/banner.png'

        dados = self._serializar()

        self.assertTrue(dados['icone'].endswith('comunidades/icones/icone.png'))
        self.assertTrue(dados['banner'].endswith('comunidades/banners/banner.png'))

    def test_membros_count(self):
        outro = Usuario.objects.create_user(
            username='outro', email='outro@example.com', password='senha-segura'
        )
        self.comunidade.membros.add(self.convivente, outro)

        self.assertEqual(self._serializar()['membros_count'], 2)

    def test_sem_request_retorna_valores_padrao(self):
        self.comunidade.membros.add(self.convivente)

        dados = self._serializar()

        self.assertFalse(dados['is_membro'])
        self.assertFalse(dados['is_moderador'])
        self.assertFalse(dados['fui_banido'])
        self.assertIsNone(dados['minha_restricao'])

    def test_usuario_anonimo_retorna_valores_padrao(self):
        dados = self._serializar(AnonymousUser())

        self.assertFalse(dados['is_membro'])
        self.assertFalse(dados['is_moderador'])
        self.assertFalse(dados['fui_banido'])
        self.assertIsNone(dados['minha_restricao'])

    def test_is_membro(self):
        self.assertFalse(self._serializar(self.convivente)['is_membro'])

        self.comunidade.membros.add(self.convivente)

        self.assertTrue(self._serializar(self.convivente)['is_membro'])

    def test_is_moderador(self):
        self.assertTrue(self._serializar(self.moderador)['is_moderador'])
        self.assertFalse(self._serializar(self.convivente)['is_moderador'])

    def test_fui_banido(self):
        self.comunidade.banidos.add(self.convivente)

        self.assertTrue(self._serializar(self.convivente)['fui_banido'])
        self.assertFalse(self._serializar(self.moderador)['fui_banido'])

    def test_minha_restricao_ativa(self):
        expira_em = timezone.now() + timedelta(days=3)
        AcaoModeracao.objects.create(
            comunidade=self.comunidade,
            convivente=self.convivente,
            moderador=self.moderador,
            tipo=AcaoModeracao.TIPO_RESTRINGIR,
            justificativa='Linguagem ofensiva',
            duracao_dias=3,
            expira_em=expira_em,
        )

        restricao = self._serializar(self.convivente)['minha_restricao']

        self.assertEqual(restricao['duracao_dias'], 3)
        self.assertEqual(restricao['justificativa'], 'Linguagem ofensiva')
        self.assertEqual(restricao['expira_em'], expira_em)

    def test_minha_restricao_retorna_a_que_expira_por_ultimo(self):
        for dias in (1, 7):
            AcaoModeracao.objects.create(
                comunidade=self.comunidade,
                convivente=self.convivente,
                moderador=self.moderador,
                tipo=AcaoModeracao.TIPO_RESTRINGIR,
                duracao_dias=dias,
                expira_em=timezone.now() + timedelta(days=dias),
            )

        restricao = self._serializar(self.convivente)['minha_restricao']

        self.assertEqual(restricao['duracao_dias'], 7)

    def test_minha_restricao_ignora_expiradas_e_banimentos(self):
        AcaoModeracao.objects.create(
            comunidade=self.comunidade,
            convivente=self.convivente,
            moderador=self.moderador,
            tipo=AcaoModeracao.TIPO_RESTRINGIR,
            duracao_dias=1,
            expira_em=timezone.now() - timedelta(days=1),
        )
        AcaoModeracao.objects.create(
            comunidade=self.comunidade,
            convivente=self.convivente,
            moderador=self.moderador,
            tipo=AcaoModeracao.TIPO_BANIR,
            expira_em=timezone.now() + timedelta(days=1),
        )

        self.assertIsNone(self._serializar(self.convivente)['minha_restricao'])

    def test_dados_validos_criam_comunidade(self):
        serializer = ComunidadeSerializer(data={
            'nome': 'Nova Comunidade',
            'descricao': 'Descrição da nova comunidade',
            'categoria': 'Lazer e convivência',
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        comunidade = serializer.save(moderador=self.convivente)
        self.assertEqual(comunidade.nome, 'Nova Comunidade')
        self.assertEqual(comunidade.moderador, self.convivente)
        self.assertEqual(comunidade.regras, '')

    def test_campos_obrigatorios_ausentes(self):
        serializer = ComunidadeSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn('nome', serializer.errors)
        self.assertIn('descricao', serializer.errors)
        self.assertIn('categoria', serializer.errors)
        self.assertNotIn('regras', serializer.errors)

    def test_nome_duplicado_ignorando_maiusculas(self):
        serializer = ComunidadeSerializer(data={
            'nome': 'APOIO visual',
            'descricao': 'Descrição',
            'categoria': 'Apoio familiar',
        })

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors['nome'][0], 'Já existe uma comunidade com esse nome.'
        )

    def test_atualizacao_permite_manter_o_proprio_nome(self):
        serializer = ComunidadeSerializer(
            self.comunidade,
            data={'nome': 'Apoio Visual', 'descricao': 'Nova descrição'},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        comunidade = serializer.save()
        self.assertEqual(comunidade.descricao, 'Nova descrição')

    def test_campos_somente_leitura_sao_ignorados(self):
        serializer = ComunidadeSerializer(data={
            'nome': 'Outra Comunidade',
            'descricao': 'Descrição',
            'categoria': 'Apoio familiar',
            'moderador': self.convivente.pk,
            'membros_count': 99,
            'is_moderador': True,
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn('moderador', serializer.validated_data)
        self.assertNotIn('membros_count', serializer.validated_data)
        self.assertNotIn('is_moderador', serializer.validated_data)
