from django.apps import AppConfig
from django.core.management import call_command
from django.db.models.signals import post_migrate


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios'

    def ready(self):
        """
        Executado quando a aplicação está pronta.
        Cria os grupos de permissões após as migrações.
        """

        def criar_grupos_ao_iniciar(sender, **kwargs):
            try:
                call_command('criar_grupos_permissoes', verbosity=0)
            except Exception as e:
                print(f"⚠️ Erro ao criar grupos: {e}")

        post_migrate.connect(criar_grupos_ao_iniciar, sender=self)
