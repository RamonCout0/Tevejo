from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from comunidades.models import Comunidade, Post, Comentario

class Command(BaseCommand):
    help = 'Cria os grupos de permissões padrão do sistema'

    def handle(self, *args, **options):
        # Obter tipos de conteúdo
        comunidade_ct = ContentType.objects.get_for_model(Comunidade)
        post_ct = ContentType.objects.get_for_model(Post)
        comentario_ct = ContentType.objects.get_for_model(Comentario)
        
        # Importar modelos de conteúdos
        try:
            from conteudos.models import ConteudoEducacional, Curador
            conteudo_ct = ContentType.objects.get_for_model(ConteudoEducacional)
        except ImportError:
            conteudo_ct = None

        # ========== GRUPO: CONVIVENTE ==========
        grupo_convivente, criado = Group.objects.get_or_create(name='Convivente')
        
        if criado:
            # Permissões para Conviventes
            permissoes_convivente = Permission.objects.filter(
                content_type__in=[comunidade_ct, post_ct, comentario_ct],
                codename__in=[
                    'add_comunidade',
                    'view_comunidade',
                    'add_post',
                    'change_post',
                    'delete_post',
                    'add_comentario',
                    'change_comentario',
                    'delete_comentario',
                ]
            )
            grupo_convivente.permissions.set(permissoes_convivente)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Grupo "Convivente" criado com {permissoes_convivente.count()} permissões'
                )
            )
        else:
            # Verificar e corrigir permissões do Convivente
            permissoes_convivente = Permission.objects.filter(
                content_type__in=[comunidade_ct, post_ct, comentario_ct],
                codename__in=[
                    'add_comunidade',
                    'view_comunidade',
                    'add_post',
                    'change_post',
                    'delete_post',
                    'add_comentario',
                    'change_comentario',
                    'delete_comentario',
                ]
            )
            permissoes_atuais = set(grupo_convivente.permissions.values_list('id', flat=True))
            permissoes_esperadas = set(permissoes_convivente.values_list('id', flat=True))
            
            if permissoes_atuais != permissoes_esperadas:
                grupo_convivente.permissions.set(permissoes_convivente)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Grupo "Convivente" já existe. Permissões corrigidas ({permissoes_convivente.count()} permissões)'
                    )
                )
            else:
                self.stdout.write('Grupo "Convivente" já existe com permissões corretas')

        # ========== GRUPO: MODERADOR ==========
        grupo_moderador, criado = Group.objects.get_or_create(name='Moderador')
        
        if criado:
            # Permissões para Moderadores (todas as de Convivente + moderação)
            permissoes_moderador = Permission.objects.filter(
                content_type__in=[comunidade_ct, post_ct, comentario_ct],
                codename__in=[
                    'view_comunidade',
                    'change_comunidade',
                    'add_post',
                    'change_post',
                    'delete_post',
                    'add_comentario',
                    'change_comentario',
                    'delete_comentario',
                ]
            )
            grupo_moderador.permissions.set(permissoes_moderador)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Grupo "Moderador" criado com {permissoes_moderador.count()} permissões'
                )
            )
        else:
            # Verificar e corrigir permissões do Moderador
            permissoes_moderador = Permission.objects.filter(
                content_type__in=[comunidade_ct, post_ct, comentario_ct],
                codename__in=[
                    'view_comunidade',
                    'change_comunidade',
                    'add_post',
                    'change_post',
                    'delete_post',
                    'add_comentario',
                    'change_comentario',
                    'delete_comentario',
                ]
            )
            permissoes_atuais = set(grupo_moderador.permissions.values_list('id', flat=True))
            permissoes_esperadas = set(permissoes_moderador.values_list('id', flat=True))
            
            if permissoes_atuais != permissoes_esperadas:
                grupo_moderador.permissions.set(permissoes_moderador)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Grupo "Moderador" já existe. Permissões corrigidas ({permissoes_moderador.count()} permissões)'
                    )
                )
            else:
                self.stdout.write('Grupo "Moderador" já existe com permissões corretas')

        # ========== GRUPO: CURADOR ==========
        grupo_curador, criado = Group.objects.get_or_create(name='Curador')
        
        if criado and conteudo_ct:
            # Permissões para Curadores
            permissoes_curador = Permission.objects.filter(
                content_type__in=[conteudo_ct],
                codename__in=[
                    'add_conteudoeducacional',
                    'change_conteudoeducacional',
                    'delete_conteudoeducacional',
                    'view_conteudoeducacional',
                ]
            )
            grupo_curador.permissions.set(permissoes_curador)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Grupo "Curador" criado com {permissoes_curador.count()} permissões'
                )
            )
        elif conteudo_ct:
            # Verificar e corrigir permissões do Curador
            permissoes_curador = Permission.objects.filter(
                content_type__in=[conteudo_ct],
                codename__in=[
                    'add_conteudoeducacional',
                    'change_conteudoeducacional',
                    'delete_conteudoeducacional',
                    'view_conteudoeducacional',
                ]
            )
            permissoes_atuais = set(grupo_curador.permissions.values_list('id', flat=True))
            permissoes_esperadas = set(permissoes_curador.values_list('id', flat=True))
            
            if permissoes_atuais != permissoes_esperadas:
                grupo_curador.permissions.set(permissoes_curador)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Grupo "Curador" já existe. Permissões corrigidas ({permissoes_curador.count()} permissões)'
                    )
                )
            else:
                self.stdout.write('Grupo "Curador" já existe com permissões corretas')

        self.stdout.write(self.style.SUCCESS('Grupos e permissões configurados com sucesso!'))
