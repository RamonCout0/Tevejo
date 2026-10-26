from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django import forms

from .models import Usuario, Curador, Convivente


class UsuarioCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('username', 'email', 'nome')


class UsuarioAdmin(UserAdmin):
    """Admin com formulários corretos de senha (faz hash via set_password)."""

    add_form = UsuarioCreationForm
    model = Usuario

    list_display = ('username', 'email', 'nome', 'is_staff')
    search_fields = ('username', 'email', 'nome')

    fieldsets = UserAdmin.fieldsets + (
        ('Dados TeVejo', {'fields': ('nome', 'biografia', 'foto')}),
        ('Termo de Consentimento', {'fields': ('termo_versao_aceita', 'termo_aceito_em')}),
        ('Guia condutor', {'fields': ('guia_respondido_em',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'nome', 'password1', 'password2'),
        }),
    )


class CuradorCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Curador
        fields = ('username', 'email', 'nome', 'especialidade')


class CuradorAdmin(UsuarioAdmin):
    add_form = CuradorCreationForm
    model = Curador

    fieldsets = UsuarioAdmin.fieldsets + (
        ('Curador', {'fields': ('especialidade',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'nome', 'especialidade', 'password1', 'password2'),
        }),
    )


class ConviventeCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Convivente
        fields = ('username', 'email', 'nome')


class ConviventeAdmin(UsuarioAdmin):
    add_form = ConviventeCreationForm
    model = Convivente

    list_display = ('username', 'email', 'nome', 'data_cadastro', 'is_staff')
    readonly_fields = ('data_cadastro',)

    fieldsets = UsuarioAdmin.fieldsets + (
        ('Convivente', {'fields': ('data_cadastro',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'nome', 'password1', 'password2'),
        }),
    )


admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Curador, CuradorAdmin)
admin.site.register(Convivente, ConviventeAdmin)
