from django.db import models
from usuarios.models import Usuario
from conteudos.models import Tags
from django.core.exceptions import ValidationError
from principal.utils import get_image_field

# Create your models here.

class Convivente(Usuario):
    dataCadastro = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nome
    
    def clean(self):
        super().clean()



class Comunidade(models.Model):
    nome = models.CharField(max_length=25)
    descricao = models.TextField()
    conviventes = models.ManyToManyField(Usuario, related_name='comunidades')
    regras = models.TextField(blank=True, null=True)
    tipoVisibilidade = models.CharField(max_length=7, choices=[('publico', 'Público'), ('privado', 'Privado')], default='privado')
    tags = models.ManyToManyField(Tags, related_name='comunidades')
    dataCriacao = models.DateField(auto_now_add=True)
    banner = get_image_field(upload_to='banners/', blank=True, null=True)
    icone = get_image_field(upload_to='icones/', blank=True, null=True)
    moderadores = models.ManyToManyField(Usuario, related_name='comunidades_moderadas')

    def __str__(self):
        return self.nome
    
    def getConviventes(self):
        return self.conviventes.all()

    def clean(self):
        """
        Validação de negócio para a comunidade.
        NOTA: Esta validação é usada apenas quando necessário verificar
        consistência de comunidades já estabelecidas. Durante a criação,
        estas validações são relaxadas no ComunidadeService.
        """
        erros = {}
        if len(self.nome) < 3:
            erros['nome'] = 'O nome da comunidade deve ter pelo menos 3 caracteres.'
        if len(self.descricao) < 10:
            erros['descricao'] = 'A descrição deve ter pelo menos 10 caracteres.'
        # Validações opcionais (comentadas durante criação)
        # if self.tags.count() == 0:
        #     erros['tags'] = 'A comunidade deve ter pelo menos uma tag associada.'
        # if self.moderadores.count() == 0:
        #     erros['moderadores'] = 'A comunidade deve ter pelo menos um moderador.'
        if erros:
            raise ValidationError(erros)

class Post(models.Model):
    comunidade = models.ForeignKey(Comunidade, on_delete=models.CASCADE, related_name='posts')
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='posts')
    titulo = models.CharField(max_length=100, null=True, blank=False)
    conteudo = models.TextField()
    dataPostagem = models.DateTimeField(auto_now_add=True)
    reacoes=models.ManyToManyField(Usuario, through='ReacaoPost', related_name='posts_reagidos')
    denuncias=models.ManyToManyField(Usuario, through='DenunciaPost', related_name='posts_denunciados')
    def __str__(self):
        return f"Post de {self.autor.nome} na comunidade {self.comunidade.nome}"
    
    def clean(self):
        erros = {}
        if len(self.conteudo) < 5:
            erros['conteudo'] = 'O conteúdo do post deve ter pelo menos 5 caracteres.'
        if len(self.conteudo) > 300:
            erros['conteudo'] = 'O conteúdo do post deve ter no máximo 300 caracteres.'
        if len(self.titulo) > 50:
            erros['titulo'] = 'O título do post deve ter no máximo 50 caracteres.'
        if len(self.titulo) < 5:
            erros['titulo'] = 'O título do post deve ter pelo menos 5 caracteres.'
        if erros:
            raise ValidationError(erros)
class ReacaoPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reacoes_post')
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reacoes_post')
    curtir= models.BooleanField(default=True)

    def __str__(self):
        return f"{self.curtir} de {self.autor.nome} no post {self.post.id}"
class DenunciaPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='denuncias_post')
    denunciante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='denuncias_feitas')
    descricao = models.TextField()
    status=models.CharField(max_length=10, choices=[('em_analise', 'Em Análise'), ('aprovado', 'Aprovado'), ('reprovado', 'Reprovado')], default='em_analise')

    def __str__(self):
        return f"Denúncia de {self.denunciante.nome} no post {self.post.id}"
    
    def clean(self):
        erros = {}
        if len(self.descricao) < 10:
            erros['descricao'] = 'A descrição da denúncia deve ter pelo menos 10 caracteres.'
        if erros:
            raise ValidationError(erros)
    
class Comentario(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='comentarios')
    texto = models.TextField()
    dataComentario = models.DateTimeField(auto_now_add=True)
    reacoes=models.ManyToManyField(Usuario, through='ReacaoComentario', related_name='comentarios_reagidos')
    denuncias=models.ManyToManyField(Usuario, through='DenunciaComentario', related_name='comentarios_denunciados')
    

    def __str__(self):
        return f"Comentário de {self.autor.nome} no post {self.post.id}"
    
    def clean(self):
        erros = {}
        if len(self.texto) < 2:
            erros['texto'] = 'O conteúdo do comentário deve ter pelo menos 2 caracteres.'
        if erros:
            raise ValidationError(erros)
        
class ReacaoComentario(models.Model):
    comentario = models.ForeignKey(Comentario, on_delete=models.CASCADE, related_name='reacoes_comentario')
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reacoes_comentario')
    curtir= models.BooleanField(default=True)

    def __str__(self):
        return f"{self.curtir} de {self.autor.nome} no comentário {self.comentario.id}"
    
class DenunciaComentario(models.Model):
    comentario = models.ForeignKey(Comentario, on_delete=models.CASCADE, related_name='denuncias_comentario')
    denunciante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='denuncias_comentario_feitas')
    descricao = models.TextField()
    status=models.CharField(max_length=10, choices=[('em_analise', 'Em Análise'), ('aprovado', 'Aprovado'), ('reprovado', 'Reprovado')], default='em_analise')

    def __str__(self):
        return f"Denúncia de {self.denunciante.nome} no comentário {self.comentario.id}"
    
    def clean(self):
        erros = {}
        if len(self.descricao) < 10:
            erros['descricao'] = 'A descrição da denúncia deve ter pelo menos 10 caracteres.'
        if erros:
            raise ValidationError(erros)

class Encontro(models.Model):
    comunidade = models.ForeignKey(Comunidade, on_delete=models.CASCADE, related_name='encontros')
    tags = models.ManyToManyField(Tags, related_name='encontros')
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    dataHora = models.DateTimeField()
    endereco = models.CharField(max_length=200)
    imagem = get_image_field(upload_to='encontros/', blank=True, null=True)

    def __str__(self):
        return f"Encontro: {self.titulo} na comunidade {self.comunidade.nome}"
    
    def clean(self):
        erros = {}
        if len(self.titulo) < 3:
            erros['titulo'] = 'O título do encontro deve ter pelo menos 3 caracteres.'
        if len(self.descricao) < 10:
            erros['descricao'] = 'A descrição do encontro deve ter pelo menos 10 caracteres.'
        if len(self.endereco) < 5:
            erros['endereco'] = 'O local do encontro deve ter pelo menos 5 caracteres.'
        if self.tags.count() == 0:
            erros['tags'] = 'O encontro deve ter pelo menos uma tag associada.'
        if erros:
            raise ValidationError(erros)