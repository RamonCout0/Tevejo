import io
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase
from PIL import Image

from .models import Convivente, Curador
from .serializers import (
	CadastroConviventeSerializer,
	GoogleLoginSerializer,
	LoginSerializer,
	UsuarioMeSerializer,
	UsuarioSerializer,
)


Usuario = get_user_model()


class ModelosUsuarioTestCase(TestCase):
	def test_usuario_limpa_nome_usa_username_como_padrao_e_representa_usuario(self):
		usuario = Usuario.objects.create_user(
			username='usuario_teste',
			email='usuario@example.com',
			password='senha-segura',
			nome='  Nome Limpo  ',
		)

		self.assertEqual(usuario.nome, 'Nome Limpo')
		self.assertEqual(str(usuario), 'Nome Limpo')

		usuario_sem_nome = Usuario.objects.create_user(
			username='usuario_sem_nome',
			email='sem_nome@example.com',
			password='senha-segura',
		)
		self.assertEqual(usuario_sem_nome.nome, 'usuario_sem_nome')
		self.assertEqual(str(usuario_sem_nome), 'usuario_sem_nome')

	def test_usuario_valida_nome_minimo_considerando_username_como_fallback(self):
		usuario = Usuario(username='ab', email='usuario@example.com')

		with self.assertRaises(ValidationError) as erro:
			usuario.full_clean()

		self.assertIn('nome', erro.exception.message_dict)

	def test_curador_representa_nome_e_especialidade_e_valida_especialidade(self):
		curador = Curador.objects.create_user(
			username='curador',
			email='curador@example.com',
			password='senha-segura',
			nome='Curador Teste',
			especialidade='Psicologia',
		)

		self.assertEqual(str(curador), 'Curador Teste - Psicologia')
		curador.full_clean()

		curador.especialidade = 'ab'
		with self.assertRaises(ValidationError) as erro:
			curador.full_clean()

		self.assertIn('especialidade', erro.exception.message_dict)

	def test_convivente_representa_nome(self):
		convivente = Convivente.objects.create_user(
			username='convivente',
			email='convivente@example.com',
			password='senha-segura',
			nome='Convivente Teste',
		)

		self.assertEqual(str(convivente), 'Convivente Teste')
		self.assertIsNotNone(convivente.data_cadastro)


class SerializersUsuarioTestCase(TestCase):
	def setUp(self):
		self.convivente = Convivente.objects.create_user(
			username='convivente',
			email='convivente@example.com',
			password='senha-segura',
			nome='Convivente Teste',
		)
		self.senha_forte = 'R4ndom!Passphrase-2026-Z'

	def test_cadastro_convivente_cria_usuario_com_senha_hash_e_sem_expor_senha(self):
		serializer = CadastroConviventeSerializer(data={
			'username': 'nova_convivente',
			'email': 'nova@example.com',
			'nome': 'Nova Convivente',
			'password': self.senha_forte,
			'password_confirmacao': self.senha_forte,
		})

		self.assertTrue(serializer.is_valid(), serializer.errors)
		novo_usuario = serializer.save()

		self.assertIsInstance(novo_usuario, Convivente)
		self.assertTrue(novo_usuario.check_password(self.senha_forte))
		self.assertNotIn('password', serializer.data)

	def test_cadastro_convivente_rejeita_senha_fraca_e_email_duplicado(self):
		senha_fraca = CadastroConviventeSerializer(data={
			'username': 'novo_usuario',
			'email': 'novo@example.com',
			'nome': 'Novo Usuario',
			'password': '123',
			'password_confirmacao': '123',
		})
		self.assertFalse(senha_fraca.is_valid())
		self.assertIn('password', senha_fraca.errors)

		email_duplicado = CadastroConviventeSerializer(data={
			'username': 'outro_usuario',
			'email': self.convivente.email,
			'nome': 'Outro Usuario',
			'password': self.senha_forte,
			'password_confirmacao': self.senha_forte,
		})
		self.assertFalse(email_duplicado.is_valid())
		self.assertIn('email', email_duplicado.errors)

	def test_usuario_serializer_exibe_dados_e_papeis(self):
		dados = UsuarioSerializer(self.convivente).data

		self.assertEqual(dados['id'], self.convivente.id)
		self.assertEqual(dados['username'], 'convivente')
		self.assertEqual(dados['email'], 'convivente@example.com')
		self.assertEqual(dados['nome'], 'Convivente Teste')
		self.assertTrue(dados['is_convivente'])
		self.assertFalse(dados['is_curador'])
		self.assertIsNone(dados['foto'])

	def test_usuario_me_serializer_edita_perfil_sem_alterar_campos_somente_leitura(self):
		serializer = UsuarioMeSerializer(
			self.convivente,
			data={
				'username': 'nao_deve_alterar',
				'nome': '  Nome Atualizado  ',
				'email': 'atualizado@example.com',
				'biografia': 'Minha biografia',
			},
			partial=True,
		)

		self.assertTrue(serializer.is_valid(), serializer.errors)
		usuario_atualizado = serializer.save()

		self.assertEqual(usuario_atualizado.username, 'convivente')
		self.assertEqual(usuario_atualizado.nome, 'Nome Atualizado')
		self.assertEqual(usuario_atualizado.email, 'atualizado@example.com')
		self.assertEqual(serializer.data['biografia'], 'Minha biografia')

	def test_usuario_me_serializer_rejeita_email_duplicado(self):
		Usuario.objects.create_user(
			username='outro', email='outro@example.com', password='senha-segura'
		)
		email_duplicado = UsuarioMeSerializer(
			self.convivente, data={'email': 'outro@example.com'}, partial=True
		)
		self.assertFalse(email_duplicado.is_valid())
		self.assertIn('email', email_duplicado.errors)

	def test_login_serializer_autentica_por_email_ou_username(self):
		for identificador in ('email', 'username'):
			serializer = LoginSerializer(data={
				identificador: getattr(self.convivente, identificador),
				'password': 'senha-segura',
			})

			self.assertTrue(serializer.is_valid(), serializer.errors)
			self.assertEqual(serializer.validated_data['usuario'].pk, self.convivente.pk)

	def test_login_serializer_rejeita_credenciais_invalidas_e_identificador_ausente(self):
		credenciais_invalidas = LoginSerializer(data={
			'email': self.convivente.email,
			'password': 'senha-incorreta',
		})
		self.assertFalse(credenciais_invalidas.is_valid())

		sem_identificador = LoginSerializer(data={'password': 'senha-segura'})
		self.assertFalse(sem_identificador.is_valid())

	@patch('usuarios.serializers.google_id_token.verify_oauth2_token')
	def test_google_login_cria_convivente_para_email_verificado(self, verificar_token):
		verificar_token.return_value = {
			'email': 'google@example.com',
			'email_verified': True,
			'name': 'Pessoa Google',
		}
		serializer = GoogleLoginSerializer(data={'id_token': 'token-valido'})

		self.assertTrue(serializer.is_valid(), serializer.errors)
		usuario = serializer.validated_data['usuario']

		self.assertIsInstance(usuario, Convivente)
		self.assertEqual(usuario.email, 'google@example.com')
		self.assertEqual(usuario.nome, 'Pessoa Google')
		self.assertFalse(usuario.has_usable_password())

	@patch('usuarios.serializers.google_id_token.verify_oauth2_token')
	def test_google_login_rejeita_token_invalido_ou_email_nao_verificado(self, verificar_token):
		verificar_token.side_effect = ValueError('inválido')
		token_invalido = GoogleLoginSerializer(data={'id_token': 'token-invalido'})
		self.assertFalse(token_invalido.is_valid())
		self.assertIn('id_token', token_invalido.errors)

		verificar_token.side_effect = None
		verificar_token.return_value = {
			'email': 'google@example.com',
			'email_verified': False,
			'name': 'Pessoa Google',
		}
		email_nao_verificado = GoogleLoginSerializer(data={'id_token': 'token-nao-verificado'})
		self.assertFalse(email_nao_verificado.is_valid())


class UsuarioModelTest(TestCase):
	"""Testes unitários para o modelo Usuario (CDU018)."""

	def test_criar_usuario_valido(self):
		usuario = Usuario.objects.create_user(
			username="joaosilva",
			email="joao@email.com",
			nome="João Silva",
			password="senhaSegura123"
		)
		self.assertEqual(usuario.nome, "João Silva")
		self.assertEqual(str(usuario), "João Silva")

	def test_validacao_nome_minimo_clean(self):
		usuario = Usuario(username="al", email="al@email.com", nome="Al")
		with self.assertRaises(ValidationError) as ctx:
			usuario.clean()
		self.assertIn("nome", ctx.exception.message_dict)

	def test_strip_nome_no_save(self):
		usuario = Usuario.objects.create_user(
			username="maria",
			email="maria@email.com",
			nome="  Maria Souza  "
		)
		self.assertEqual(usuario.nome, "Maria Souza")

	def test_nome_vazio_assume_username(self):
		usuario = Usuario.objects.create_user(
			username="carlos123",
			email="carlos@email.com",
			nome=""
		)
		self.assertEqual(usuario.nome, "carlos123")

	def test_email_unico(self):
		Usuario.objects.create_user(username="u1", email="repetido@email.com")
		with self.assertRaises(IntegrityError):
			Usuario.objects.create_user(username="u2", email="repetido@email.com")

	def test_str_retorna_nome_ou_username(self):
		u1 = Usuario(username="user1", nome="Nome Completo")
		u2 = Usuario(username="user2", nome="")
		self.assertEqual(str(u1), "Nome Completo")
		self.assertEqual(str(u2), "user2")


class UsuarioMeSerializerTest(TestCase):
	"""Testes unitários para o serializer UsuarioMeSerializer (CDU018)."""

	def setUp(self):
		self.user = Usuario.objects.create_user(
			username="teste",
			email="teste@email.com",
			nome="Usuário Teste"
		)
		self.outro_user = Usuario.objects.create_user(
			username="outro",
			email="outro@email.com",
			nome="Outro Usuário"
		)

	def test_serializacao_campos_publicos(self):
		serializer = UsuarioMeSerializer(instance=self.user)
		data = serializer.data
		self.assertEqual(data["id"], self.user.id)
		self.assertEqual(data["username"], "teste")
		self.assertEqual(data["email"], "teste@email.com")
		self.assertEqual(data["nome"], "Usuário Teste")
		self.assertIn("biografia", data)
		self.assertIn("foto", data)
		self.assertIn("is_convivente", data)
		self.assertIn("is_curador", data)

	def test_atualizacao_parcial_valida(self):
		serializer = UsuarioMeSerializer(
			instance=self.user,
			data={"nome": "Novo Nome", "biografia": "Biografia atualizada."},
			partial=True
		)
		self.assertTrue(serializer.is_valid(), serializer.errors)
		atualizado = serializer.save()
		self.assertEqual(atualizado.nome, "Novo Nome")
		self.assertEqual(atualizado.biografia, "Biografia atualizada.")

	def test_campos_readonly_nao_alterados(self):
		serializer = UsuarioMeSerializer(
			instance=self.user,
			data={"username": "hacked_username", "id": 9999},
			partial=True
		)
		self.assertTrue(serializer.is_valid())
		atualizado = serializer.save()
		self.assertEqual(atualizado.username, "teste")
		self.assertEqual(atualizado.id, self.user.id)

	def test_validacao_nome_curto_falha(self):
		serializer = UsuarioMeSerializer(
			instance=self.user,
			data={"nome": "Ab"},
			partial=True
		)
		self.assertFalse(serializer.is_valid())
		self.assertIn("nome", serializer.errors)
		self.assertIn("O nome deve ter pelo menos 3 caracteres.", str(serializer.errors["nome"]))

	def test_validacao_email_em_uso_falha(self):
		serializer = UsuarioMeSerializer(
			instance=self.user,
			data={"email": "outro@email.com"},
			partial=True
		)
		self.assertFalse(serializer.is_valid())
		# O validador de unicidade do modelo responde antes do validate_email.
		self.assertIn("email", serializer.errors)

	def _imagem(self, formato):
		buffer = io.BytesIO()
		Image.new("RGB", (1, 1)).save(buffer, format=formato)
		return buffer.getvalue()

	def test_validacao_foto_formato_invalido(self):
		# Imagem real, mas em GIF: passa no ImageField e cai na regra de JPG/PNG.
		foto_invalida = SimpleUploadedFile(
			name="foto.gif",
			content=self._imagem("GIF"),
			content_type="image/gif"
		)
		serializer = UsuarioMeSerializer(
			instance=self.user,
			data={"foto": foto_invalida},
			partial=True
		)
		self.assertFalse(serializer.is_valid())
		self.assertIn("foto", serializer.errors)
		self.assertIn("Arquivo de imagem inválido. Use JPG ou PNG.", str(serializer.errors["foto"]))

	def test_validacao_foto_tamanho_maximo(self):
		# PNG válido completado até passar de 5 MB
		conteudo_grande = self._imagem("PNG") + b"\0" * (5 * 1024 * 1024 + 1024)
		foto_pesada = SimpleUploadedFile(
			name="pesada.png",
			content=conteudo_grande,
			content_type="image/png"
		)
		serializer = UsuarioMeSerializer(
			instance=self.user,
			data={"foto": foto_pesada},
			partial=True
		)
		self.assertFalse(serializer.is_valid())
		self.assertIn("foto", serializer.errors)
		self.assertIn("A imagem deve ter no máximo 5 MB.", str(serializer.errors["foto"]))
