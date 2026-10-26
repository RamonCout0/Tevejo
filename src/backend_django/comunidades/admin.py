from django.contrib import admin

from .models import AcaoModeracao, ComentarioPostagem, Comunidade, Encontro, DenunciaPostagem, Postagem


@admin.register(Comunidade)
class ComunidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'moderador', 'criado_em')
    search_fields = ('nome', 'categoria')
    list_filter = ('categoria', 'criado_em')
    readonly_fields = ('criado_em',)
    fields = ('nome', 'descricao', 'categoria', 'regras', 'icone', 'banner', 'moderador', 'membros', 'banidos', 'criado_em')
    filter_horizontal = ('membros', 'banidos')


@admin.register(AcaoModeracao)
class AcaoModeracaoAdmin(admin.ModelAdmin):
    list_display = ('comunidade', 'convivente', 'tipo', 'moderador', 'criado_em', 'expira_em')
    list_filter = ('tipo', 'criado_em')
    search_fields = ('comunidade__nome', 'convivente__username', 'moderador__username')
    readonly_fields = ('criado_em',)


@admin.register(Postagem)
class PostagemAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'comunidade', 'autor', 'criado_em')
    search_fields = ('titulo', 'conteudo', 'comunidade__nome', 'autor__username')
    list_filter = ('comunidade', 'criado_em')
    readonly_fields = ('criado_em',)

@admin.register(ComentarioPostagem)
class ComentarioPostagemAdmin(admin.ModelAdmin):
    list_display = ('postagem', 'autor', 'criado_em')
    search_fields = ('conteudo', 'postagem__titulo', 'autor__username')
    list_filter = ('criado_em',)
    readonly_fields = ('criado_em',)    

@admin.register(DenunciaPostagem)
class DenunciaPostagemAdmin(admin.ModelAdmin):
    list_display = ('motivo', 'comunidade', 'postagem', 'denunciante', 'status', 'criado_em')
    search_fields = ('motivo', 'detalhe', 'postagem__titulo', 'denunciante__username')
    list_filter = ('status', 'comunidade', 'criado_em')
    readonly_fields = ('criado_em', 'analisado_em')    


@admin.register(Encontro)
class EncontroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'comunidade', 'data_hr_encontro', 'criado_por', 'criado_em')
    search_fields = ('titulo', 'endereco')
    list_filter = ('comunidade', 'data_hr_encontro')
    readonly_fields = ('criado_em',)
