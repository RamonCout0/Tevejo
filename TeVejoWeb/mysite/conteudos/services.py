from django.core.exceptions import ValidationError
from django.db import transaction
from .models import ConteudoEducacional, Curador, Tags

class ConteudoService:
    """
    Service para intermediar as ações de criação e gerenciamento de conteúdos educacionais.
    """

    @staticmethod
    def _verificar_permissao_gerenciar_conteudo(curador):
        """Verifica se o objeto é um Curador e se o User do Django tem as permissões."""
        
        # 1. Verifica se o objeto é da classe Curador (novo modelo com link)
        if not isinstance(curador, Curador):
            raise ValueError("Apenas curadores autorizados podem gerenciar conteúdos.")
        
        # 2. Acessa o User do Django (User -> Usuario -> Curador)
        # Como Curador tem OneToOne com Usuario, e Usuario tem OneToOne com User:
        user_auth = curador
        
        if not user_auth.is_active:
            raise ValueError(f"Usuário {user_auth.username} não está ativo.")
        
        # 3. Verifica o grupo (criado pelo comando criar_grupos_permissoes)
        if not user_auth.groups.filter(name='Curador').exists():
            raise ValueError("Seu usuário não pertence ao grupo 'Curador'.")
        
        # 4. Verifica a permissão de banco de dados
        if not user_auth.has_perm('conteudos.add_conteudoeducacional'):
            raise ValueError("Seu usuário não tem permissão técnica para publicar conteúdos.")
        
        return True

    @staticmethod
    def _validar_dados_conteudo(titulo, fonte, descricao, tipos):
        """Valida os dados de entrada para criação/edição."""
        erros = {}
        if not titulo or len(titulo.strip()) < 5:
            erros['titulo'] = 'O título deve ter pelo menos 5 caracteres.'
        if not fonte or len(fonte.strip()) < 5:
            erros['fonte'] = 'A fonte deve ter pelo menos 5 caracteres.'
        if not descricao or len(descricao.strip()) < 10:
            erros['descricao'] = 'A descrição deve ter pelo menos 10 caracteres.'
        if not tipos:
            erros['tipos'] = 'Selecione pelo menos uma categoria (Tag).'
        
        if erros:
            raise ValidationError(erros)

    @staticmethod
    @transaction.atomic
    def criar_conteudo(titulo, fonte, descricao, tipos, curador):
        ConteudoService._validar_dados_conteudo(titulo, fonte, descricao, tipos)
        ConteudoService._verificar_permissao_gerenciar_conteudo(curador)
        
        try:
            conteudo = ConteudoEducacional(
                titulo=titulo.strip(),
                fonte=fonte.strip(),
                descricao=descricao.strip(),
                curador=curador
            )
            conteudo.full_clean()
            conteudo.save()
            conteudo.tipos.set(tipos)
            return conteudo
        except ValidationError as e:
            raise ValidationError(e.message_dict if hasattr(e, 'message_dict') else str(e))
        except Exception as e:
            raise ValueError(f"Erro inesperado ao salvar: {str(e)}")

    @staticmethod
    @transaction.atomic
    def editar_conteudo(conteudo_id, titulo, fonte, descricao, tipos, curador):
        """Edita conteúdo verificando se o curador é o autor original."""
        ConteudoService._validar_dados_conteudo(titulo, fonte, descricao, tipos)
        ConteudoService._verificar_permissao_gerenciar_conteudo(curador)
        
        try:
            conteudo = ConteudoEducacional.objects.get(id=conteudo_id)
            
            # SEGURANÇA: Verifica se o objeto Curador é o mesmo que criou o post
            if conteudo.curador != curador:
                raise ValueError("Você só pode editar conteúdos que você mesmo publicou.")

            conteudo.titulo = titulo.strip()
            conteudo.fonte = fonte.strip()
            conteudo.descricao = descricao.strip()
            conteudo.full_clean()
            conteudo.save()
            conteudo.tipos.set(tipos)
            return conteudo
        except ConteudoEducacional.DoesNotExist:
            raise ValueError("Conteúdo não encontrado.")
        except Exception as e:
            raise ValueError(str(e))

    @staticmethod
    @transaction.atomic
    def deletar_conteudo(conteudo_id, curador):
        """Deleta conteúdo verificando a posse."""
        ConteudoService._verificar_permissao_gerenciar_conteudo(curador)
        
        try:
            conteudo = ConteudoEducacional.objects.get(id=conteudo_id)
            if conteudo.curador != curador:
                raise ValueError("Você não tem permissão para deletar este conteúdo.")
                
            conteudo.delete()
            return True
        except ConteudoEducacional.DoesNotExist:
            raise ValueError("Conteúdo não encontrado.")

    @staticmethod
    def obter_conteudos_publicados():
        return ConteudoEducacional.objects.all().order_by('-id')

    @staticmethod
    def obter_tags():
        return Tags.objects.all()