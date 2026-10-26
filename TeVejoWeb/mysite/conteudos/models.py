from django.db import models
from usuarios.models import Usuario, Curador
from django.core.exceptions import ValidationError

# Create your models here.

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
    tipos = models.ManyToManyField(Tags,related_name='conteudos')
    curador = models.ForeignKey(Curador, on_delete=models.PROTECT, related_name='conteudos')

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
    