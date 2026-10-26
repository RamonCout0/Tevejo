import io
import os
import shutil
import tempfile
from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from usuarios.models import Convivente

from .models import ComentarioPostagem, Comunidade, DenunciaPostagem, Encontro, Postagem
from .services import InteracaoPostagemService, ModeracaoService


class ComunidadeApiBase(APITestCase):
    def setUp(self):
        self.moderador = Convivente.objects.create_user(
            username='mod', email='mod@tevejo.com', password='SenhaForte@123', nome='Moderador',
        )
        self.membro = Convivente.objects.create_user(
            username='ana', email='ana@tevejo.com', password='SenhaForte@123', nome='Ana Lima',
        )
        self.outro = Convivente.objects.create_user(
            username='bia', email='bia@tevejo.com', password='SenhaForte@123', nome='Bia Souza',
        )
        self.comunidade = Comunidade.objects.create(
            nome='Apoio TEA', descricao='Descrição', categoria='Apoio', moderador=self.moderador,
        )
        self.comunidade.membros.add(self.moderador, self.membro, self.outro)
        self.postagem = Postagem.objects.create(
            comunidade=self.comunidade, autor=self.membro, titulo='Olá', conteudo='Primeira postagem',
        )


class RestricaoTests(ComunidadeApiBase):
    """CDU024 - convivente restringido não publica nem comenta."""

    def setUp(self):
        super().setUp()
        ModeracaoService.aplicar_acao(
            comunidade=self.comunidade, moderador=self.moderador,
            convivente=self.membro, tipo='restringir', duracao_dias=3,
        )
        self.client.force_authenticate(self.membro)

    def test_restringido_nao_comenta(self):
        url = reverse('comunidades:comentarios-postagem', args=[self.comunidade.pk, self.postagem.pk])

        resposta = self.client.post(url, {'conteudo': 'oi'}, format='json')

        self.assertEqual(resposta.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('restrito', resposta.data['erro'])

    def test_restringido_ainda_curte(self):
        url = reverse('comunidades:curtir-postagem', args=[self.comunidade.pk, self.postagem.pk])

        resposta = self.client.post(url)

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)


class PostagemAutorTests(ComunidadeApiBase):
    def test_postagem_expoe_username_do_autor(self):
        self.client.force_authenticate(self.membro)

        resposta = self.client.get(reverse('comunidades:postagens', args=[self.comunidade.pk]))

        self.assertEqual(resposta.data[0]['autor'], 'Ana Lima')
        self.assertEqual(resposta.data[0]['autor_username'], 'ana')


class DenunciasOrfasTests(ComunidadeApiBase):
    """CDU025 - aprovar uma denúncia resolve as demais sobre o mesmo item."""

    def test_aprovar_postagem_resolve_denuncias_da_postagem_e_dos_comentarios(self):
        comentario = ComentarioPostagem.objects.create(
            postagem=self.postagem, autor=self.outro, conteudo='comentário',
        )
        d1 = InteracaoPostagemService.denunciar(self.postagem, self.outro, 'Ofensivo')
        d2 = InteracaoPostagemService.denunciar(self.postagem, self.moderador, 'Spam')
        d3 = InteracaoPostagemService.denunciar_comentario(comentario, self.membro, 'Ofensivo')

        ModeracaoService.aprovar_denuncia(d1, self.moderador)

        self.assertFalse(Postagem.objects.filter(pk=self.postagem.pk).exists())
        self.assertFalse(
            DenunciaPostagem.objects.filter(
                pk__in=[d2.pk, d3.pk], status=DenunciaPostagem.STATUS_PENDENTE,
            ).exists()
        )

    def test_aprovar_comentario_resolve_outras_denuncias_do_comentario(self):
        comentario = ComentarioPostagem.objects.create(
            postagem=self.postagem, autor=self.outro, conteudo='comentário',
        )
        d1 = InteracaoPostagemService.denunciar_comentario(comentario, self.membro, 'Ofensivo')
        d2 = InteracaoPostagemService.denunciar_comentario(comentario, self.moderador, 'Spam')
        d_post = InteracaoPostagemService.denunciar(self.postagem, self.outro, 'Spam')

        ModeracaoService.aprovar_denuncia(d1, self.moderador)

        d2.refresh_from_db()
        d_post.refresh_from_db()
        self.assertEqual(d2.status, DenunciaPostagem.STATUS_APROVADA)
        # A denúncia da postagem não é afetada pela remoção do comentário.
        self.assertEqual(d_post.status, DenunciaPostagem.STATUS_PENDENTE)


class EncontrosPublicosTests(ComunidadeApiBase):
    """CDU005 - Visualizar Encontros Públicos."""

    def setUp(self):
        super().setUp()
        outra = Comunidade.objects.create(
            nome='Outra', descricao='d', categoria='Lazer', moderador=self.outro,
        )
        agora = timezone.now()
        Encontro.objects.create(
            comunidade=self.comunidade, titulo='Próximo', descricao='d',
            data_hr_encontro=agora + timedelta(days=2), endereco='Natal',
        )
        Encontro.objects.create(
            comunidade=outra, titulo='De outra comunidade', descricao='d',
            data_hr_encontro=agora + timedelta(days=1), endereco='Natal',
        )
        Encontro.objects.create(
            comunidade=self.comunidade, titulo='Passado', descricao='d',
            data_hr_encontro=agora - timedelta(days=1), endereco='Natal',
        )
        self.client.force_authenticate(self.membro)

    def test_lista_proximos_encontros_de_todas_as_comunidades(self):
        resposta = self.client.get(reverse('comunidades:encontros-publicos'))

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual([e['titulo'] for e in resposta.data], ['De outra comunidade', 'Próximo'])
        self.assertEqual(resposta.data[1]['comunidade_id'], self.comunidade.pk)

    def test_filtra_pelas_minhas_comunidades(self):
        resposta = self.client.get(reverse('comunidades:encontros-publicos'), {'minhas': '1'})

        self.assertEqual([e['titulo'] for e in resposta.data], ['Próximo'])


def _imagem(nome='img.png', formato='PNG', content_type='image/png'):
    buffer = io.BytesIO()
    Image.new('RGB', (40, 10)).save(buffer, formato)
    return SimpleUploadedFile(nome, buffer.getvalue(), content_type=content_type)


class GerenciarComunidadeTests(ComunidadeApiBase):
    """CDU012 - Gerenciar comunidades (editar e excluir)."""

    def setUp(self):
        super().setUp()
        self.media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.media, ignore_errors=True)
        configuracao = override_settings(MEDIA_ROOT=self.media)
        configuracao.enable()
        self.addCleanup(configuracao.disable)
        self.url = reverse('comunidades:detalhe', args=[self.comunidade.pk])

    def test_moderador_edita_informacoes(self):
        self.client.force_authenticate(self.moderador)

        resposta = self.client.patch(self.url, {'descricao': 'Nova descrição', 'categoria': 'Saúde e terapias'})

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.comunidade.refresh_from_db()
        self.assertEqual(self.comunidade.descricao, 'Nova descrição')
        self.assertEqual(self.comunidade.categoria, 'Saúde e terapias')

    def test_moderador_troca_imagens_e_arquivo_antigo_e_apagado(self):
        self.client.force_authenticate(self.moderador)
        self.client.patch(self.url, {'icone': _imagem('a.png'), 'banner': _imagem('b.png')}, format='multipart')
        self.comunidade.refresh_from_db()
        icone_antigo = self.comunidade.icone.path

        resposta = self.client.patch(self.url, {'icone': _imagem('c.png')}, format='multipart')

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertTrue(resposta.data['icone'].startswith('/media/comunidades/icones/'))
        self.assertFalse(os.path.exists(icone_antigo))
        self.assertIsNotNone(resposta.data['banner'])

    def test_moderador_remove_banner(self):
        self.client.force_authenticate(self.moderador)
        self.client.patch(self.url, {'banner': _imagem('b.png')}, format='multipart')
        self.comunidade.refresh_from_db()
        caminho = self.comunidade.banner.path

        resposta = self.client.patch(self.url, {'remover_banner': 'true'}, format='multipart')

        self.assertIsNone(resposta.data['banner'])
        self.assertFalse(os.path.exists(caminho))

    def test_rejeita_imagem_em_formato_invalido(self):
        self.client.force_authenticate(self.moderador)

        resposta = self.client.patch(
            self.url, {'icone': _imagem('a.gif', 'GIF', 'image/gif')}, format='multipart',
        )

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('icone', resposta.data)

    def test_rejeita_nome_de_outra_comunidade(self):
        Comunidade.objects.create(nome='Outra', descricao='d', categoria='c', moderador=self.outro)
        self.client.force_authenticate(self.moderador)

        resposta = self.client.patch(self.url, {'nome': 'outra'})

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('nome', resposta.data)

    def test_membro_nao_edita_nem_exclui(self):
        self.client.force_authenticate(self.membro)

        self.assertEqual(self.client.patch(self.url, {'nome': 'X'}).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.delete(self.url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Comunidade.objects.filter(pk=self.comunidade.pk).exists())

    def test_visitante_nao_edita(self):
        self.assertEqual(self.client.patch(self.url, {'nome': 'X'}).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_moderador_exclui_comunidade_com_postagens_e_imagens(self):
        self.client.force_authenticate(self.moderador)
        self.client.patch(self.url, {'icone': _imagem('a.png')}, format='multipart')
        self.comunidade.refresh_from_db()
        caminho = self.comunidade.icone.path

        resposta = self.client.delete(self.url)

        self.assertEqual(resposta.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comunidade.objects.filter(pk=self.comunidade.pk).exists())
        self.assertFalse(Postagem.objects.filter(pk=self.postagem.pk).exists())
        self.assertFalse(os.path.exists(caminho))


class LimitesDeTextoTests(ComunidadeApiBase):
    """Textos longos são recusados com mensagem clara (não quebram o layout)."""

    def test_categoria_gigante_e_recusada(self):
        self.client.force_authenticate(self.moderador)

        resposta = self.client.patch(
            reverse('comunidades:detalhe', args=[self.comunidade.pk]),
            {'categoria': 'ajKSDAJKSDJak' * 10},
        )

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('categoria', resposta.data)

    def test_comentario_acima_do_limite_e_recusado(self):
        self.client.force_authenticate(self.membro)
        url = reverse('comunidades:comentarios-postagem', args=[self.comunidade.pk, self.postagem.pk])

        resposta = self.client.post(url, {'conteudo': 'x' * 1001}, format='json')

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_detalhe_de_denuncia_acima_do_limite_e_recusado(self):
        self.client.force_authenticate(self.outro)
        url = reverse('comunidades:denunciar-postagem', args=[self.comunidade.pk, self.postagem.pk])

        resposta = self.client.post(url, {'motivo': 'Spam', 'detalhe': 'x' * 501}, format='json')

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)


class CategoriasFixasTests(ComunidadeApiBase):
    """A categoria vem de uma lista fixa (filtro limpo na tela de Comunidades)."""

    def test_aceita_categoria_da_lista(self):
        self.client.force_authenticate(self.moderador)

        resposta = self.client.post(reverse('comunidades:criar'), {
            'nome': 'Escola inclusiva', 'descricao': 'Troca sobre inclusão escolar.',
            'categoria': 'Educação e escola',
        })

        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resposta.data['categoria'], 'Educação e escola')

    def test_recusa_categoria_fora_da_lista(self):
        self.client.force_authenticate(self.moderador)

        resposta = self.client.post(reverse('comunidades:criar'), {
            'nome': 'Qualquer', 'descricao': 'Descrição.', 'categoria': 'ajKSDAJKSDJak',
        })

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('categoria', resposta.data)

    def test_editar_sem_mexer_na_categoria_antiga_continua_funcionando(self):
        # Comunidades criadas antes da lista fixa podem ter categoria livre.
        self.comunidade.categoria = 'Categoria antiga livre'
        self.comunidade.save()
        self.client.force_authenticate(self.moderador)

        resposta = self.client.patch(
            reverse('comunidades:detalhe', args=[self.comunidade.pk]), {'descricao': 'Atualizada'},
        )

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
