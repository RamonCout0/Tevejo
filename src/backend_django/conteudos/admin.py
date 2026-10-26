from django.contrib import admin

from .models import ConteudoEducacional, Denuncia, Tags

admin.site.register(Tags)
admin.site.register(ConteudoEducacional)


@admin.register(Denuncia)
class DenunciaAdmin(admin.ModelAdmin):
    list_display = ('conteudo', 'convivente', 'motivo', 'status', 'criado_em')
    list_filter = ('motivo', 'status', 'criado_em')
    search_fields = ('conteudo__titulo', 'convivente__username', 'descricao')
    readonly_fields = ('criado_em',)
