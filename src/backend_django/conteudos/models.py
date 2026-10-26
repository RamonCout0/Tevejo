from django.conf import settings
from django.db import models
from usuarios.models import Usuario, Curador
from django.core.exceptions import ValidationError


class Tags(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

    def clean(self):
        erros = {}
        if len(self.nome) < 3:
            erros['nome'] = 'O nome do tipo de conteúdo deve ter pelo menos 3 caracteres.'
        if erros:
            raise ValidationError(erros)


class ConteudoEducacional(models.Model):
    fonte = models.CharField(max_length=200)
    descricao = models.TextField()
    titulo = models.CharField(max_length=200)
    tipos = models.ManyToManyField(Tags, related_name='conteudos')
    curador = models.ForeignKey(Curador, on_delete=models.PROTECT, related_name='conteudos')
    criado_em = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return self.titulo

    def clean(self):
        erros = {}
        if len(self.titulo) < 5:
            erros['titulo'] = 'O título deve ter pelo menos 5 caracteres.'
        if len(self.fonte) < 5:
            erros['fonte'] = 'A fonte deve ter pelo menos 5 caracteres.'
        if erros:
            raise ValidationError(erros)


class Denuncia(models.Model):
    """Denúncia de um conteúdo educacional feita por um convivente (CDU022)."""

    MOTIVO_DESATUALIZADO = 'desatualizado'
    MOTIVO_INCORRETO = 'incorreto'
    MOTIVO_LINK_QUEBRADO = 'link_quebrado'
    MOTIVO_OUTRO = 'outro'
    MOTIVO_CHOICES = [
        (MOTIVO_DESATUALIZADO, 'Conteúdo desatualizado'),
        (MOTIVO_INCORRETO, 'Incorreto segundo novos estudos'),
        (MOTIVO_LINK_QUEBRADO, 'Link quebrado'),
        (MOTIVO_OUTRO, 'Outro'),
    ]

    STATUS_EM_ANALISE = 'em_analise'
    STATUS_RESOLVIDA = 'resolvida'
    STATUS_CHOICES = [
        (STATUS_EM_ANALISE, 'Em análise'),
        (STATUS_RESOLVIDA, 'Resolvida'),
    ]

    conteudo = models.ForeignKey(
        ConteudoEducacional, on_delete=models.CASCADE, related_name='denuncias'
    )
    convivente = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='denuncias_feitas'
    )
    motivo = models.CharField(max_length=20, choices=MOTIVO_CHOICES)
    descricao = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_EM_ANALISE)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Denúncia'
        verbose_name_plural = 'Denúncias'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.get_motivo_display()} em {self.conteudo} por {self.convivente}'