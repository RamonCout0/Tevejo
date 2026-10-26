from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from usuarios.models import Curador

from .models import ConteudoEducacional, Denuncia, Tags
from .serializers import (
	ConteudoEducacionalSerializer,
	CuradorSerializer,
	DenunciaSerializer,
	RegistrarDenunciaSerializer,
	TagsSerializer,
)


class ConteudosTestCase(TestCase):
	def setUp(self):
		self.curador = Curador.objects.create_user(
			username='curador',
			email='curador@example.com',
			password='senha-segura',
			nome='Curador Teste',
			especialidade='Psicologia',
		)
		self.convivente = get_user_model().objects.create_user(
			username='convivente',
			email='convivente@example.com',
			password='senha-segura',
			nome='Convivente Teste',
		)
		self.tag = Tags.objects.create(nome='Saúde mental')
		self.conteudo = ConteudoEducacional.objects.create(
			fonte='Fonte confiável',
			descricao='Descrição do conteúdo educacional.',
			titulo='Título de teste',
			curador=self.curador,
		)
		self.conteudo.tipos.add(self.tag)

	def test_tags_model_exibe_nome_e_valida_tamanho_minimo(self):
		self.assertEqual(str(self.tag), 'Saúde mental')
		self.tag.full_clean()

		tag_invalida = Tags(nome='ab')
		with self.assertRaises(ValidationError) as erro:
			tag_invalida.full_clean()

		self.assertIn('nome', erro.exception.message_dict)

	def test_conteudo_model_exibe_titulo_e_valida_titulo_e_fonte(self):
		self.assertEqual(str(self.conteudo), 'Título de teste')
		self.conteudo.full_clean()

		conteudo_invalido = ConteudoEducacional(
			fonte='abc', descricao='Descrição', titulo='abc', curador=self.curador
		)
		with self.assertRaises(ValidationError) as erro:
			conteudo_invalido.full_clean()

		self.assertEqual(set(erro.exception.message_dict), {'titulo', 'fonte'})

	def test_denuncia_model_define_status_padrao_e_representacao(self):
		denuncia = Denuncia.objects.create(
			conteudo=self.conteudo,
			convivente=self.convivente,
			motivo=Denuncia.MOTIVO_LINK_QUEBRADO,
		)

		self.assertEqual(denuncia.status, Denuncia.STATUS_EM_ANALISE)
		self.assertEqual(
			str(denuncia),
			f'Link quebrado em {self.conteudo} por {self.convivente}',
		)

	def test_tags_serializer_representa_id_e_nome(self):
		dados = TagsSerializer(self.tag).data

		self.assertEqual(dados, {'id': self.tag.id, 'nome': 'Saúde mental'})

	def test_curador_serializer_representa_nome_e_especialidade(self):
		dados = CuradorSerializer(self.curador).data

		self.assertEqual(dados['id'], self.curador.id)
		self.assertEqual(dados['nome'], 'Curador Teste')
		self.assertEqual(dados['especialidade'], 'Psicologia')

	def test_registrar_denuncia_serializer_valida_motivo_e_descricao_opcional(self):
		serializer = RegistrarDenunciaSerializer(data={
			'motivo': Denuncia.MOTIVO_OUTRO,
		})

		self.assertTrue(serializer.is_valid(), serializer.errors)
		self.assertEqual(serializer.validated_data['descricao'], '')

		serializer_invalido = RegistrarDenunciaSerializer(data={'motivo': 'invalido'})
		self.assertFalse(serializer_invalido.is_valid())
		self.assertIn('motivo', serializer_invalido.errors)

	def test_denuncia_serializer_representa_valores_e_rotulos(self):
		denuncia = Denuncia.objects.create(
			conteudo=self.conteudo,
			convivente=self.convivente,
			motivo=Denuncia.MOTIVO_INCORRETO,
			descricao='Há informação desatualizada.',
		)

		dados = DenunciaSerializer(denuncia).data

		self.assertEqual(dados['conteudo'], self.conteudo.id)
		self.assertEqual(dados['convivente'], str(self.convivente))
		self.assertEqual(dados['motivo_display'], 'Incorreto segundo novos estudos')
		self.assertEqual(dados['status_display'], 'Em análise')
		self.assertTrue(DenunciaSerializer().fields['motivo'].read_only)

	def test_conteudo_serializer_cria_com_ids_e_representa_relacoes_aninhadas(self):
		serializer = ConteudoEducacionalSerializer(data={
			'titulo': 'Novo conteúdo',
			'fonte': 'Fonte de teste',
			'descricao': 'Descrição do novo conteúdo.',
			'tipos_ids': [self.tag.id],
		})

		self.assertTrue(serializer.is_valid(), serializer.errors)
		conteudo = serializer.save(curador=self.curador)
		dados = serializer.data

		self.assertEqual(list(conteudo.tipos.all()), [self.tag])
		self.assertEqual(dados['tipos'], [{'id': self.tag.id, 'nome': 'Saúde mental'}])
		self.assertEqual(dados['curador']['id'], self.curador.id)
		self.assertIsNone(dados['minha_denuncia'])
		self.assertNotIn('tipos_ids', dados)

	def test_conteudo_serializer_retorna_denuncia_pendente_do_usuario(self):
		denuncia = Denuncia.objects.create(
			conteudo=self.conteudo,
			convivente=self.convivente,
			motivo=Denuncia.MOTIVO_DESATUALIZADO,
		)
		serializer = ConteudoEducacionalSerializer(
			self.conteudo,
			context={'request': SimpleNamespace(user=self.convivente)},
		)

		minha_denuncia = serializer.data['minha_denuncia']

		self.assertEqual(minha_denuncia['id'], denuncia.id)
		self.assertEqual(minha_denuncia['motivo'], Denuncia.MOTIVO_DESATUALIZADO)
		self.assertEqual(minha_denuncia['status'], Denuncia.STATUS_EM_ANALISE)
