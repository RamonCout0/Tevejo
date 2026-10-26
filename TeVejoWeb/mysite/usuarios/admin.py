from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario, Curador


class CuradorCreationForm(UserCreationForm):
    """Formulário customizado para criar Curadores"""
    class Meta:
        model = Curador
        fields = ('username', 'email', 'nome', 'foto', 'especialidade', 'password1', 'password2')


class CuradorChangeForm(UserChangeForm):
    """Formulário customizado para editar Curadores"""
    class Meta:
        model = Curador
        fields = ('username', 'email', 'nome', 'foto', 'biografia', 'especialidade', 'is_staff', 'is_active', 'groups', 'user_permissions')


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """
    Admin do usuário customizado.

    O administrador pode visualizar os dados de perfil,
    mas não pode alterá-los (nome, foto e biografia).
    """

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Perfil', {
            'fields': ('nome', 'foto', 'biografia'),
        }),
    )

    # Campos de perfil apenas para leitura no admin
    readonly_fields = ('nome', 'foto', 'biografia')

    list_display = ('username', 'email', 'nome', 'is_staff', 'is_active', 'tipo_usuario')
    search_fields = ('username', 'email', 'nome')
    list_filter = ('is_staff', 'is_active', 'is_superuser')

    def tipo_usuario(self, obj):
        """Mostra se o usuário é um Curador na listagem"""
        if isinstance(obj, Curador):
            return f"🎓 Curador: {obj.especialidade}"
        return "👤 Usuário"
    
    tipo_usuario.short_description = "Tipo"


@admin.register(Curador)
class CuradorAdmin(BaseUserAdmin):
    """
    Admin customizado para Curadores.
    
    Permite criar, editar e listar Curadores com seus campos específicos.
    """
    
    form = CuradorChangeForm
    add_form = CuradorCreationForm

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Perfil', {
            'fields': ('nome', 'foto', 'biografia'),
        }),
        ('Especialidade', {
            'fields': ('especialidade',),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'nome', 'foto', 'especialidade', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('nome', 'biografia')

    list_display = ('username', 'email', 'especialidade', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'nome', 'especialidade')
    list_filter = ('is_staff', 'is_active', 'is_superuser')


# ============================================================
# IMPORTANTE: Registros de Admin para Herança Multi-Tabela
# ============================================================
#
# ✅ Correto:
#    - Registrar Usuario em usuarios/admin.py
#    - Registrar Curador em usuarios/admin.py (mesmo app)
#
# ❌ Errado:
#    - Registrar Curador em conteudos/admin.py (app diferente)
#    - Isso causa conflito de herança e loops de login
#
# Por que funciona quando ambos estão em usuarios/admin.py?
# Django consegue resolver as permissões e a herança corretamente
# quando os modelos relacionados estão registrados no mesmo app.


