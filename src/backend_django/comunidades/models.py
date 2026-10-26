from django.db import models
from django.conf import settings


class Comunidade(models.Model):
    nome = models.CharField(max_length=150, unique=True)
    descricao = models.TextField()
    categoria = models.CharField(max_length=100)
    regras = models.TextField(blank=True)
    icone = models.ImageField(upload_to='comunidades/icones/', blank=True, null=True)
    banner = models.ImageField(upload_to='comunidades/banners/', blank=True, null=True) 
    moderador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    membros = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='comunidades_participadas',
        blank=True,
    )
    banidos = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='banimentos_em_comunidades',
        blank=True,
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Comunidade'
        verbose_name_plural = 'Comunidades'

    def __str__(self):
        return self.nome


class AcaoModeracao(models.Model):
    """Histórico de ações de moderação aplicadas em conviventes (CDU024)."""

    TIPO_RESTRINGIR = 'restringir'
    TIPO_BANIR = 'banir'
    TIPO_CHOICES = [
        (TIPO_RESTRINGIR, 'Restringir'),
        (TIPO_BANIR, 'Banir'),
    ]

    comunidade = models.ForeignKey(
        Comunidade, on_delete=models.CASCADE, related_name='acoes_moderacao'
    )
    convivente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='acoes_recebidas',
    )
    moderador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='acoes_aplicadas',
    )
    tipo = models.CharField(max_length=12, choices=TIPO_CHOICES)
    justificativa = models.TextField(blank=True)
    duracao_dias = models.PositiveIntegerField(null=True, blank=True)
    expira_em = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ação de Moderação'
        verbose_name_plural = 'Ações de Moderação'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.get_tipo_display()} de {self.convivente} em {self.comunidade}'


class Postagem(models.Model):
    comunidade = models.ForeignKey(
        Comunidade,
        on_delete=models.CASCADE,
        related_name='postagens',
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='postagens_comunidade',
    )
    titulo = models.CharField(max_length=50)
    conteudo = models.TextField()
    curtidas = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='postagens_curtidas',
        blank=True,
    )    
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Postagem'
        verbose_name_plural = 'Postagens'
        ordering = ['-criado_em']

    def __str__(self):
        return self.titulo


class Encontro(models.Model):
    """Encontro criado por um moderador dentro de uma comunidade (CDU010)."""

    comunidade = models.ForeignKey(
        Comunidade,
        on_delete=models.CASCADE,
        related_name='encontros',
    )
    titulo = models.CharField(max_length=150)
    descricao = models.TextField()
    data_hr_encontro = models.DateTimeField()
    endereco = models.CharField(max_length=255)
    tags = models.CharField(max_length=255, blank=True)
    img = models.ImageField(upload_to='encontros/imagens/', blank=True, null=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='encontros_criados',
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Encontro'
        verbose_name_plural = 'Encontros'
        ordering = ['-data_hr_encontro']

    def __str__(self):
        return self.titulo


class ComentarioPostagem(models.Model):
    postagem = models.ForeignKey(
        Postagem,
        on_delete=models.CASCADE,
        related_name='comentarios',
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='respostas',
        blank=True,
        null=True,
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comentarios_postagens',
    )
    conteudo = models.TextField()
    curtidas = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='comentarios_curtidos',
        blank=True,
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Comentário de Postagem'
        verbose_name_plural = 'Comentários de Postagens'
        ordering = ['criado_em']

    def __str__(self):
        return f'{self.autor}: {self.conteudo[:40]}'        

class DenunciaPostagem(models.Model):
    STATUS_PENDENTE = 'pendente'
    STATUS_APROVADA = 'aprovada'
    STATUS_REPROVADA = 'reprovada'

    STATUS_CHOICES = [
        (STATUS_PENDENTE, 'Pendente'),
        (STATUS_APROVADA, 'Aprovada'),
        (STATUS_REPROVADA, 'Reprovada'),
    ]

    comunidade = models.ForeignKey(
        Comunidade,
        on_delete=models.CASCADE,
        related_name='denuncias_postagens',
    )
    postagem = models.ForeignKey(
        Postagem,
        on_delete=models.SET_NULL,
        related_name='denuncias',
        blank=True,
        null=True,
    )
    comentario = models.ForeignKey(
        ComentarioPostagem,
        on_delete=models.SET_NULL,
        related_name='denuncias',
        blank=True,
        null=True,
    )
    denunciante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='denuncias_postagens',
    )
    motivo = models.CharField(max_length=120)
    detalhe = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDENTE)
    analisado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='denuncias_analisadas',
        blank=True,
        null=True,
    )
    analisado_em = models.DateTimeField(blank=True, null=True)
    acao_registrada = models.CharField(max_length=160, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Denúncia de Postagem'
        verbose_name_plural = 'Denúncias de Postagens'
        ordering = ['criado_em']

    def __str__(self):
        return f'{self.denunciante} denunciou {self.postagem or "postagem removida"}'        