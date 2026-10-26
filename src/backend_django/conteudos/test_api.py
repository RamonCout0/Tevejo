from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from usuarios.models import Convivente, Curador

from .models import Tags


class TagsPermissaoTests(APITestCase):
    def setUp(self):
        Tags.objects.create(nome='Saúde mental')
        self.convivente = Convivente.objects.create_user(
            username='ana', email='ana@tevejo.com', password='SenhaForte@123', nome='Ana Lima',
        )
        self.curador = Curador.objects.create_user(
            username='cur', email='cur@tevejo.com', password='SenhaForte@123',
            nome='Curador', especialidade='Psicologia',
        )

    def test_visitante_lista_tags(self):
        resposta = self.client.get(reverse('tags-list'))

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resposta.data), 1)

    def test_convivente_nao_cria_tag(self):
        self.client.force_authenticate(self.convivente)

        resposta = self.client.post(reverse('tags-list'), {'nome': 'Spam'}, format='json')

        self.assertEqual(resposta.status_code, status.HTTP_403_FORBIDDEN)

    def test_curador_cria_tag(self):
        self.client.force_authenticate(self.curador)

        resposta = self.client.post(reverse('tags-list'), {'nome': 'Escola'}, format='json')

        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
