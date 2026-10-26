from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .models import AcaoModeracao, Comunidade, DenunciaPostagem, Encontro, Postagem
from .serializers import (
    AcaoModeracaoSerializer,
    AplicarAcaoModeracaoSerializer,
    DenunciaPostagemSerializer,
    EncontroSerializer,
)


Usuario = get_user_model()


class ModelosModeracaoTestCase(TestCase):
    """Testes de modelos relacionados aos CDU024 e CDU025."""

    def setUp(self):
        self.moderador = Usuario.objects.create_user(
            username='moderador', email='moderador@example.com', password='senha-segura'
        )
        self.convivente = Usuario.objects.create_user(
            username='convivente', email='convivente@example.com', password='senha-segura'
        )
        self.denunciante = Usuario.objects.create_user(
            username='denunciante', email='denunciante@example.com', password='senha-segura'
        )
        self.comunidade = Comunidade.objects.create(
            nome='Comunidade de teste',
            descricao='Descrição',
            categoria='Apoio',
            moderador=self.moderador,
        )
        self.postagem = Postagem.objects.create(
            comunidade=self.comunidade,
            autor=self.convivente,
            titulo='Postagem de teste',
            conteudo='Conteúdo da postagem',
        )

    def test_acao_moderacao_restringir_registra_duracao_e_exibicao(self):
        acao = AcaoModeracao.objects.create(
            comunidade=self.comunidade,
            convivente=self.convivente,
            moderador=self.moderador,
            tipo=AcaoModeracao.TIPO_RESTRINGIR,
            justificativa='Descumprimento das regras',
            duracao_dias=1,
            expira_em=timezone.now() + timedelta(days=1),
        )

        self.assertEqual(acao.get_tipo_display(), 'Restringir')
        self.assertEqual(
            str(acao), f'Restringir de {self.convivente} em {self.comunidade}'
        )

    def test_acao_moderacao_banir_permite_moderador_removido(self):
        acao = AcaoModeracao.objects.create(
            comunidade=self.comunidade,
            convivente=self.convivente,
            moderador=self.moderador,
            tipo=AcaoModeracao.TIPO_BANIR,
            justificativa='a',
        )

        outro_moderador = Usuario.objects.create_user(
            username='outro_moderador',
            email='outro_moderador@example.com',
            password='senha-segura',
        )
        self.comunidade.moderador = outro_moderador
        self.comunidade.save(update_fields=['moderador'])
        self.moderador.delete()
        acao.refresh_from_db()

        self.assertIsNone(acao.moderador)
        self.assertEqual(acao.get_tipo_display(), 'Banir')
        self.assertIn('Banir de', str(acao))

    def test_denuncia_postagem_inicia_pendente_e_identifica_postagem(self):
        denuncia = DenunciaPostagem.objects.create(
            comunidade=self.comunidade,
            postagem=self.postagem,
            denunciante=self.denunciante,
            motivo='Conteúdo inadequado',
        )

        self.assertEqual(denuncia.status, DenunciaPostagem.STATUS_PENDENTE)
        self.assertEqual(
            str(denuncia), f'{self.denunciante} denunciou {self.postagem}'
        )

    def test_denuncia_postagem_representa_alvo_removido(self):
        denuncia = DenunciaPostagem.objects.create(
            comunidade=self.comunidade,
            postagem=self.postagem,
            denunciante=self.denunciante,
            motivo='Conteúdo inadequado',
        )

        self.postagem.delete()
        denuncia.refresh_from_db()

        self.assertIsNone(denuncia.postagem)
        self.assertIn('postagem removida', str(denuncia))


class SerializersModeracaoTestCase(TestCase):
    """Testes dos serializers usados pelos CDU024 e CDU025."""

    def test_aplicar_acao_moderacao_aceita_duracao_minima_e_justificativa_curta(self):
        serializer = AplicarAcaoModeracaoSerializer(data={
            'convivente_id': 1,
            'tipo': AcaoModeracao.TIPO_RESTRINGIR,
            'duracao_dias': 1,
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['duracao_dias'], 1)

        serializer_banimento = AplicarAcaoModeracaoSerializer(data={
            'convivente_id': 1,
            'tipo': AcaoModeracao.TIPO_BANIR,
            'justificativa': 'a',
        })
        self.assertTrue(serializer_banimento.is_valid(), serializer_banimento.errors)

    def test_aplicar_acao_moderacao_rejeita_duracao_zero_e_tipo_invalido(self):
        serializer = AplicarAcaoModeracaoSerializer(data={
            'convivente_id': 1,
            'tipo': AcaoModeracao.TIPO_RESTRINGIR,
            'duracao_dias': 0,
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('duracao_dias', serializer.errors)

        serializer_tipo_invalido = AplicarAcaoModeracaoSerializer(data={
            'convivente_id': 1,
            'tipo': 'advertir',
        })
        self.assertFalse(serializer_tipo_invalido.is_valid())
        self.assertIn('tipo', serializer_tipo_invalido.errors)

    def test_acao_moderacao_serializer_exibe_tipo_e_partes(self):
        moderador = Usuario.objects.create_user(
            username='moderador', email='moderador@example.com', password='senha-segura'
        )
        convivente = Usuario.objects.create_user(
            username='convivente', email='convivente@example.com', password='senha-segura'
        )
        comunidade = Comunidade.objects.create(
            nome='Comunidade', descricao='Descrição', categoria='Apoio', moderador=moderador
        )
        acao = AcaoModeracao.objects.create(
            comunidade=comunidade,
            convivente=convivente,
            moderador=moderador,
            tipo=AcaoModeracao.TIPO_RESTRINGIR,
            justificativa='Descumprimento das regras',
            duracao_dias=1,
            expira_em=timezone.now() + timedelta(days=1),
        )

        dados = AcaoModeracaoSerializer(acao).data

        self.assertEqual(dados['tipo'], AcaoModeracao.TIPO_RESTRINGIR)
        self.assertEqual(dados['tipo_display'], 'Restringir')
        self.assertEqual(dados['moderador'], str(moderador))
        self.assertEqual(dados['convivente'], str(convivente))

    def test_denuncia_postagem_serializer_exibe_alvo_e_dados_relacionados(self):
        moderador = Usuario.objects.create_user(
            username='moderador', email='moderador@example.com', password='senha-segura'
        )
        convivente = Usuario.objects.create_user(
            username='convivente', email='convivente@example.com', password='senha-segura'
        )
        denunciante = Usuario.objects.create_user(
            username='denunciante', email='denunciante@example.com', password='senha-segura'
        )
        comunidade = Comunidade.objects.create(
            nome='Comunidade', descricao='Descrição', categoria='Apoio', moderador=moderador
        )
        postagem = Postagem.objects.create(
            comunidade=comunidade, autor=convivente,
            titulo='Postagem', conteudo='Texto denunciado',
        )
        denuncia = DenunciaPostagem.objects.create(
            comunidade=comunidade,
            postagem=postagem,
            denunciante=denunciante,
            motivo='Conteúdo inadequado',
        )

        dados = DenunciaPostagemSerializer(denuncia).data

        self.assertEqual(dados['alvo_tipo'], 'postagem')
        self.assertEqual(dados['postagem_titulo'], 'Postagem')
        self.assertEqual(dados['postagem_conteudo'], 'Texto denunciado')
        self.assertEqual(dados['denunciante'], str(denunciante))

    def test_denuncia_postagem_serializer_representa_conteudo_removido(self):
        moderador = Usuario.objects.create_user(
            username='moderador', email='moderador@example.com', password='senha-segura'
        )
        convivente = Usuario.objects.create_user(
            username='convivente', email='convivente@example.com', password='senha-segura'
        )
        denunciante = Usuario.objects.create_user(
            username='denunciante', email='denunciante@example.com', password='senha-segura'
        )
        comunidade = Comunidade.objects.create(
            nome='Comunidade', descricao='Descrição', categoria='Apoio', moderador=moderador
        )
        postagem = Postagem.objects.create(
            comunidade=comunidade, autor=convivente,
            titulo='Postagem', conteudo='Texto denunciado',
        )
        denuncia = DenunciaPostagem.objects.create(
            comunidade=comunidade,
            postagem=postagem,
            denunciante=denunciante,
            motivo='Conteúdo inadequado',
        )
        postagem.delete()
        denuncia.refresh_from_db()

        dados = DenunciaPostagemSerializer(denuncia).data

        self.assertEqual(dados['alvo_tipo'], 'postagem')
        self.assertEqual(dados['postagem_titulo'], 'Postagem removida')
        self.assertEqual(dados['postagem_conteudo'], '')
        self.assertEqual(dados['postagem_autor'], 'Autor indisponível')


class EncontroModelTest(TestCase):
    """Testes unitários para o modelo Encontro (CDU010)."""

    def setUp(self):
        self.moderador = Usuario.objects.create_user(
            username="mod",
            email="mod@email.com",
            nome="Moderador Teste"
        )
        self.comunidade = Comunidade.objects.create(
            nome="Comunidade Teste",
            descricao="Descrição da comunidade",
            categoria="Apoio",
            moderador=self.moderador
        )

    def test_criar_encontro_valido(self):
        data_encontro = timezone.now() + timedelta(days=2)
        encontro = Encontro.objects.create(
            comunidade=self.comunidade,
            titulo="Encontro Presencial",
            descricao="Discussão sobre rotinas e apoio.",
            data_hr_encontro=data_encontro,
            endereco="Auditório IFRN",
            tags="apoio,rotina",
            criado_por=self.moderador
        )
        self.assertEqual(str(encontro), "Encontro Presencial")
        self.assertEqual(encontro.comunidade, self.comunidade)
        self.assertEqual(encontro.criado_por, self.moderador)
        self.assertEqual(encontro.endereco, "Auditório IFRN")

    def test_ordenacao_por_data_decrescente(self):
        data1 = timezone.now() + timedelta(days=1)
        data2 = timezone.now() + timedelta(days=5)
        e1 = Encontro.objects.create(
            comunidade=self.comunidade,
            titulo="Encontro 1",
            descricao="Desc 1",
            data_hr_encontro=data1,
            endereco="Local 1"
        )
        e2 = Encontro.objects.create(
            comunidade=self.comunidade,
            titulo="Encontro 2",
            descricao="Desc 2",
            data_hr_encontro=data2,
            endereco="Local 2"
        )
        encontros = list(Encontro.objects.filter(comunidade=self.comunidade))
        self.assertEqual(encontros, [e2, e1])

    def test_exclusao_em_cascata_pela_comunidade(self):
        Encontro.objects.create(
            comunidade=self.comunidade,
            titulo="Encontro a Deletar",
            descricao="Desc",
            data_hr_encontro=timezone.now(),
            endereco="Local"
        )
        self.comunidade.delete()
        self.assertEqual(Encontro.objects.count(), 0)

    def test_exclusao_do_criador_set_null(self):
        # O moderador é protegido contra exclusão, então o criador é outro usuário.
        criador = Usuario.objects.create_user(
            username="criador",
            email="criador@email.com",
            nome="Criador Teste"
        )
        encontro = Encontro.objects.create(
            comunidade=self.comunidade,
            titulo="Encontro com Criador",
            descricao="Desc",
            data_hr_encontro=timezone.now(),
            endereco="Local",
            criado_por=criador
        )
        criador.delete()
        encontro.refresh_from_db()
        self.assertIsNone(encontro.criado_por)

    def test_campos_opcionais_tags_e_img(self):
        encontro = Encontro.objects.create(
            comunidade=self.comunidade,
            titulo="Encontro Sem Tags",
            descricao="Desc",
            data_hr_encontro=timezone.now(),
            endereco="Online"
        )
        self.assertEqual(encontro.tags, "")
        self.assertFalse(bool(encontro.img))


class EncontroSerializerTest(TestCase):
    """Testes unitários para o serializer EncontroSerializer (CDU010)."""

    def test_dados_validos(self):
        data = {
            "titulo": "Café com Pais",
            "descricao": "Roda de conversa aberta.",
            "data_hr_encontro": (timezone.now() + timedelta(days=3)).isoformat(),
            "endereco": "Sala 10",
            "tags": "pais,conversa"
        }
        serializer = EncontroSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["titulo"], "Café com Pais")
        self.assertEqual(serializer.validated_data["endereco"], "Sala 10")

    def test_titulo_obrigatorio_e_sem_espacos(self):
        data = {
            "titulo": "   ",
            "descricao": "Descrição",
            "data_hr_encontro": timezone.now().isoformat(),
            "endereco": "Local"
        }
        serializer = EncontroSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        # O CharField apara os espaços e recusa o valor em branco antes do validate_titulo.
        self.assertIn("titulo", serializer.errors)

    def test_endereco_obrigatorio_e_sem_espacos(self):
        data = {
            "titulo": "Título Válido",
            "descricao": "Descrição",
            "data_hr_encontro": timezone.now().isoformat(),
            "endereco": ""
        }
        serializer = EncontroSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("endereco", serializer.errors)

    def test_campos_obrigatorios_ausentes(self):
        serializer = EncontroSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn("titulo", serializer.errors)
        self.assertIn("descricao", serializer.errors)
        self.assertIn("data_hr_encontro", serializer.errors)
        self.assertIn("endereco", serializer.errors)

    def test_campos_readonly_protegidos(self):
        data = {
            "id": 9999,
            "comunidade": "Tentativa de injetar",
            "criado_por": "Tentativa de injetar",
            "titulo": "Encontro Teste",
            "descricao": "Desc",
            "data_hr_encontro": timezone.now().isoformat(),
            "endereco": "Local"
        }
        serializer = EncontroSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn("id", serializer.validated_data)
        self.assertNotIn("comunidade", serializer.validated_data)
        self.assertNotIn("criado_por", serializer.validated_data)
