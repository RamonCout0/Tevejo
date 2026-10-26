from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.conf import settings
from principal.utils import get_image_field

class Usuario(AbstractUser):
    """Custom user model usado como AUTH_USER_MODEL.

    Mantemos a compatibilidade com os campos de autenticação do Django e
    adicionamos campos de domínio: `nome`, `foto` e `biografia`.
    """

    # Sobrescreve email para garantir unicidade (útil no registro/login por e-mail)
    email = models.EmailField('email address', unique=True)

    # Campos de perfil
    nome = models.CharField(max_length=100, blank=True)
    foto = get_image_field(upload_to='fotos/', blank=True, null=True)
    biografia = models.TextField(blank=True, null=True)

    def clean(self):
        erros = {}

        # preferir o campo `nome`, cair para `username` se necessário
        nome_limpo = self.nome.strip() if self.nome else (self.username.strip() if self.username else "")

        if len(nome_limpo) < 3:
            erros['nome'] = 'O nome deve ter pelo menos 3 caracteres.'

        if erros:
            raise ValidationError(erros)

    def save(self, *args, **kwargs):
        # garante que o nome esteja limpo antes de salvar
        if self.nome:
            self.nome = self.nome.strip()
        else:
            # sincroniza nome com username quando não fornecido
            self.nome = self.username

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome or self.username

class Curador(Usuario):
    """Usuário especializado em curação de conteúdo educacional.
    
    Herda de Usuario e adiciona um campo de especialidade.
    """
    especialidade = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Curador'
        verbose_name_plural = 'Curadores'

    def __str__(self):
        return f"{self.nome} - {self.especialidade}"
    
    def clean(self):
        erros = {}
        if len(self.especialidade) < 3:
            erros['especialidade'] = 'A especialidade deve ter pelo menos 3 caracteres.'
        if erros:
            raise ValidationError(erros)

