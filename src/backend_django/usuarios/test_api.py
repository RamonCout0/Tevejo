import io
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Convivente, Curador


def _imagem(formato, nome, content_type):
    buffer = io.BytesIO()
    Image.new('RGB', (10, 10)).save(buffer, formato)
    return SimpleUploadedFile(nome, buffer.getvalue(), content_type=content_type)


class CadastroConviventeTests(APITestCase):
    """CDU002 - Auto Cadastro."""

    def test_cadastro_cria_convivente_e_devolve_tokens(self):
        resposta = self.client.post(reverse('usuarios:cadastro'), {
            'username': 'maria',
            'email': 'maria@tevejo.com',
            'nome': 'Maria Silva',
            'password': 'SenhaForte@123',
            'password_confirmacao': 'SenhaForte@123',
        }, format='json')

        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', resposta.data)
        self.assertNotIn('password', resposta.data['usuario'])
        self.assertTrue(Convivente.objects.filter(email='maria@tevejo.com').exists())

    def test_cadastro_devolve_papeis_do_usuario(self):
        resposta = self.client.post(reverse('usuarios:cadastro'), {
            'username': 'maria',
            'email': 'maria@tevejo.com',
            'nome': 'Maria Silva',
            'password': 'SenhaForte@123',
            'password_confirmacao': 'SenhaForte@123',
        }, format='json')

        usuario = resposta.data['usuario']
        self.assertTrue(usuario['is_convivente'])
        self.assertFalse(usuario['is_curador'])
        self.assertTrue(usuario['precisa_aceitar_termo'])

    def test_cadastro_rejeita_senha_fraca(self):
        resposta = self.client.post(reverse('usuarios:cadastro'), {
            'username': 'joao',
            'email': 'joao@tevejo.com',
            'nome': 'João Souza',
            'password': '123',
            'password_confirmacao': '123',
        }, format='json')

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', resposta.data)

    def test_cadastro_rejeita_email_repetido_com_outra_caixa(self):
        Convivente.objects.create_user(username='ana', email='ana@tevejo.com', password='SenhaForte@123')

        resposta = self.client.post(reverse('usuarios:cadastro'), {
            'username': 'ana2',
            'email': 'ANA@tevejo.com',
            'nome': 'Ana Dois',
            'password': 'SenhaForte@123',
            'password_confirmacao': 'SenhaForte@123',
        }, format='json')

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', resposta.data)

    def test_cadastro_rejeita_confirmacao_de_senha_diferente(self):
        resposta = self.client.post(reverse('usuarios:cadastro'), {
            'username': 'maria',
            'email': 'maria@tevejo.com',
            'nome': 'Maria Silva',
            'password': 'SenhaForte@123',
            'password_confirmacao': 'SenhaForte@124',
        }, format='json')

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resposta.data['password_confirmacao'], ['As senhas não coincidem.'])
        self.assertFalse(Convivente.objects.filter(email='maria@tevejo.com').exists())

    def test_cadastro_rejeita_nome_curto(self):
        resposta = self.client.post(reverse('usuarios:cadastro'), {
            'username': 'al',
            'email': 'al@tevejo.com',
            'nome': 'Al',
            'password': 'SenhaForte@123',
            'password_confirmacao': 'SenhaForte@123',
        }, format='json')

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resposta.data['nome'], ['O nome deve ter pelo menos 3 caracteres.'])
        self.assertFalse(Convivente.objects.filter(email='al@tevejo.com').exists())

    def test_cadastro_exige_confirmacao_de_senha(self):
        resposta = self.client.post(reverse('usuarios:cadastro'), {
            'username': 'maria',
            'email': 'maria@tevejo.com',
            'nome': 'Maria Silva',
            'password': 'SenhaForte@123',
        }, format='json')

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirmacao', resposta.data)


class LoginTests(APITestCase):
    """CDU001 - Fazer Login."""

    def setUp(self):
        usuario = Convivente(username='ana', email='ana@tevejo.com', nome='Ana Lima')
        usuario.set_password('SenhaForte@123')
        usuario.save()

    def test_login_com_email_e_senha_corretos(self):
        resposta = self.client.post(reverse('usuarios:login'), {
            'email': 'ana@tevejo.com',
            'password': 'SenhaForte@123',
        }, format='json')

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertIn('access', resposta.data)
        self.assertIn('refresh', resposta.data)

    def test_login_com_senha_incorreta(self):
        resposta = self.client.post(reverse('usuarios:login'), {
            'email': 'ana@tevejo.com',
            'password': 'errada',
        }, format='json')

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rota_me_exige_autenticacao(self):
        resposta = self.client.get(reverse('usuarios:me'))

        self.assertEqual(resposta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_renova_access(self):
        login = self.client.post(reverse('usuarios:login'), {
            'email': 'ana@tevejo.com',
            'password': 'SenhaForte@123',
        }, format='json')

        resposta = self.client.post(reverse('api_token_refresh'), {
            'refresh': login.data['refresh'],
        }, format='json')

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertIn('access', resposta.data)


class EditarPerfilTests(APITestCase):
    """CDU018 - Editar dados pessoais."""

    def setUp(self):
        self.usuario = Convivente.objects.create_user(
            username='ana', email='ana@tevejo.com', password='SenhaForte@123', nome='Ana Lima',
        )
        Convivente.objects.create_user(
            username='bia', email='bia@tevejo.com', password='SenhaForte@123', nome='Bia Souza',
        )
        self.client.force_authenticate(self.usuario)

    def test_rejeita_foto_em_formato_nao_permitido(self):
        resposta = self.client.patch(
            reverse('usuarios:me'), {'foto': _imagem('GIF', 'a.gif', 'image/gif')}, format='multipart',
        )

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('foto', resposta.data)

    def test_aceita_foto_png_e_devolve_url_relativa(self):
        media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media, ignore_errors=True)
        with override_settings(MEDIA_ROOT=media):
            resposta = self.client.patch(
                reverse('usuarios:me'), {'foto': _imagem('PNG', 'a.png', 'image/png')}, format='multipart',
            )

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertTrue(resposta.data['foto'].startswith('/media/'))

    def test_rejeita_email_de_outro_usuario_com_outra_caixa(self):
        resposta = self.client.patch(reverse('usuarios:me'), {'email': 'BIA@tevejo.com'}, format='json')

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', resposta.data)

    def test_rejeita_nome_curto(self):
        resposta = self.client.patch(reverse('usuarios:me'), {'nome': 'Al'}, format='json')

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('nome', resposta.data)


class TermoConsentimentoTests(APITestCase):
    """CDU019 - Termo de Consentimento e Responsabilidade."""

    def test_convivente_precisa_aceitar_e_aceite_e_registrado(self):
        convivente = Convivente.objects.create_user(
            username='ana', email='ana@tevejo.com', password='SenhaForte@123', nome='Ana Lima',
        )
        self.client.force_authenticate(convivente)
        self.assertTrue(self.client.get(reverse('usuarios:me')).data['precisa_aceitar_termo'])

        resposta = self.client.post(reverse('usuarios:aceitar-termo'))

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertFalse(resposta.data['precisa_aceitar_termo'])
        convivente.refresh_from_db()
        self.assertIsNotNone(convivente.termo_aceito_em)

    def test_nova_versao_do_termo_exige_novo_aceite(self):
        convivente = Convivente.objects.create_user(
            username='ana', email='ana@tevejo.com', password='SenhaForte@123', nome='Ana Lima',
        )
        self.client.force_authenticate(convivente)
        self.client.post(reverse('usuarios:aceitar-termo'))

        with override_settings(TERMO_CONSENTIMENTO_VERSAO=2):
            self.assertTrue(self.client.get(reverse('usuarios:me')).data['precisa_aceitar_termo'])

    def test_curador_nao_precisa_aceitar(self):
        curador = Curador.objects.create_user(
            username='cur', email='cur@tevejo.com', password='SenhaForte@123',
            nome='Curador', especialidade='Psicologia',
        )
        self.client.force_authenticate(curador)

        self.assertFalse(self.client.get(reverse('usuarios:me')).data['precisa_aceitar_termo'])


class GuiaCondutorTests(APITestCase):
    """CDU026 - o convite do guia aparece só no primeiro acesso."""

    def setUp(self):
        self.usuario = Convivente.objects.create_user(
            username='ana', email='ana@tevejo.com', password='SenhaForte@123', nome='Ana Lima',
        )
        self.client.force_authenticate(self.usuario)

    def test_usuario_novo_recebe_convite(self):
        resposta = self.client.get(reverse('usuarios:me'))

        self.assertTrue(resposta.data['mostrar_convite_guia'])

    def test_responder_convite_esconde_o_convite(self):
        resposta = self.client.post(reverse('usuarios:responder-guia'))

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertFalse(resposta.data['mostrar_convite_guia'])
        self.assertFalse(self.client.get(reverse('usuarios:me')).data['mostrar_convite_guia'])

    def test_responder_de_novo_mantem_a_primeira_data(self):
        self.client.post(reverse('usuarios:responder-guia'))
        self.usuario.refresh_from_db()
        primeira = self.usuario.guia_respondido_em

        self.client.post(reverse('usuarios:responder-guia'))
        self.usuario.refresh_from_db()

        self.assertEqual(self.usuario.guia_respondido_em, primeira)

    def test_visitante_nao_responde(self):
        self.client.force_authenticate(None)

        resposta = self.client.post(reverse('usuarios:responder-guia'))

        self.assertEqual(resposta.status_code, status.HTTP_401_UNAUTHORIZED)
