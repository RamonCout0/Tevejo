from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class Usuario(AbstractUser):
    """Custom user model usado como AUTH_USER_MODEL.

    Mantemos a compatibilidade com os campos de autenticação do Django e
    adicionamos campos de domínio: `nome` e `biografia`.
    """

    email = models.EmailField('email address', unique=True)
    nome = models.CharField(max_length=100, blank=True)
    biografia = models.TextField(blank=True, null=True)
    foto = models.ImageField(upload_to='usuarios/fotos/', blank=True, null=True)
    # CDU019 - versão do Termo de Consentimento aceita (0 = nunca aceitou).
    termo_versao_aceita = models.PositiveIntegerField(default=0)
    termo_aceito_em = models.DateTimeField(blank=True, null=True)
    # CDU026 - Guia Condutor: o convite do guia aparece só até a pessoa responder.
    guia_respondido_em = models.DateTimeField(blank=True, null=True)

    def clean(self):
        erros = {}
        nome_limpo = self.nome.strip() if self.nome else (self.username.strip() if self.username else "")

        if len(nome_limpo) < 3:
            erros['nome'] = 'O nome deve ter pelo menos 3 caracteres.'

        if erros:
            raise ValidationError(erros)

    def save(self, *args, **kwargs):
        if self.nome:
            self.nome = self.nome.strip()
        else:
            self.nome = self.username

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome or self.username


class Curador(Usuario):
    """Usuário especializado em curação de conteúdo educacional."""
    especialidade = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Curador'
        verbose_name_plural = 'Curadores'

    def __str__(self):
        return f"{self.nome} - {self.especialidade}"

    def clean(self):
        super().clean()
        erros = {}
        if len(self.especialidade) < 3:
            erros['especialidade'] = 'A especialidade deve ter pelo menos 3 caracteres.'
        if erros:
            raise ValidationError(erros)


class Convivente(Usuario):
    """Usuário que convive com o TEA e pode criar/participar de comunidades."""
    data_cadastro = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Convivente'
        verbose_name_plural = 'Conviventes'

    def __str__(self):
        return self.nome or self.username