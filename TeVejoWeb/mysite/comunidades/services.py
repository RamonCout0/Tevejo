from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth.models import Group
from .models import Comunidade, Post
from usuarios.models import Usuario


class ComunidadeService:
    """
    Service para intermediar as ações de criação e gerenciamento de comunidades.
    """

    @staticmethod
    def _verificar_permissao_criar_comunidade(usuario):
        """
        Verifica se o usuário tem permissão para criar comunidades.
        
        Args:
            usuario (Usuario): Perfil de usuário
            
        Returns:
            bool: True se tem permissão
            
        Raises:
            ValueError: Se não tiver permissão
        """
        # Verificar se o usuário está ativo
        if not usuario.is_active:
            raise ValueError(
                f"Usuário {usuario.username} não está ativo. "
                "Apenas usuários ativos podem criar comunidades."
            )
        
        # Verificar se o grupo 'Convivente' existe
        grupo_convivente = Group.objects.filter(name='Convivente').first()
        
        if not grupo_convivente:
            raise ValueError(
                "Grupo 'Convivente' não encontrado. "
                "Execute: python manage.py criar_grupos_permissoes"
            )
        
        # Verificar se o usuário pertence ao grupo
        if not usuario.groups.filter(name='Convivente').exists():
            raise ValueError(
                f"Usuário {usuario.username} não pertence ao grupo 'Convivente'. "
                "Apenas conviventes podem criar comunidades."
            )
        
        # Verificar se tem permissão específica de criar comunidade
        if not usuario.has_perm('comunidades.add_comunidade'):
            raise ValueError(
                f"Usuário {usuario.username} não tem permissão para criar comunidades."
            )
        
        return True

    @staticmethod
    @transaction.atomic
    def criar_comunidade(nome, descricao, criador, icone=None):
        """
        Cria uma nova comunidade com o usuário como primeiro convivente e moderador.
        
        Args:
            nome (str): Nome da comunidade
            descricao (str): Descrição da comunidade
            criador (Usuario): Perfil de usuário que está criando a comunidade
            icone (File, optional): Arquivo de imagem para o ícone da comunidade
            
        Returns:
            Comunidade: A comunidade criada
            
        Raises:
            ValidationError: Se os dados forem inválidos
            ValueError: Se houver erro na criação ou usuário inválido
        """
        
        # Validar dados de entrada
        ComunidadeService._validar_dados_comunidade(nome, descricao)
        
        # Validar se criador é uma instância de Usuario
        if not isinstance(criador, Usuario):
            raise ValueError(
                "O criador deve ser uma instância de Usuario. "
                "Use: comunidade = ComunidadeService.criar_comunidade(..., criador=request.user)"
            )
        
        # Verificar permissão para criar comunidade
        ComunidadeService._verificar_permissao_criar_comunidade(criador)
        
        # Operações de banco de dados em transação atômica
        try:
            with transaction.atomic():
                # Criar a comunidade
                comunidade = Comunidade(
                    nome=nome.strip(),
                    descricao=descricao.strip(),
                    icone=icone
                )
                
                # Não usar full_clean() aqui pois o modelo tem validações
                # que não se aplicam durante a criação (tags obrigatórias, etc)
                comunidade.save()
                
                # Adicionar o criador como convivente e moderador
                comunidade.conviventes.add(criador)
                comunidade.moderadores.add(criador)
                comunidade.save()
                
                return comunidade
                
        except ValidationError as e:
            if hasattr(e, 'message_dict'):
                raise ValidationError(f"Erro ao criar comunidade: {e.message_dict}")
            else:
                raise ValidationError(f"Erro ao criar comunidade: {str(e)}")
        except Exception as e:
            raise ValueError(f"Erro inesperado ao criar comunidade: {str(e)}")

    @staticmethod
    def _validar_dados_comunidade(nome, descricao):
        """
        Valida os dados de entrada para criação de comunidade.
        
        Args:
            nome (str): Nome da comunidade
            descricao (str): Descrição da comunidade
            
        Raises:
            ValidationError: Se os dados forem inválidos
        """
        erros = {}
        
        # Validar nome
        if not nome or not nome.strip():
            erros['nome'] = 'O nome da comunidade é obrigatório.'
        elif len(nome.strip()) < 3:
            erros['nome'] = 'O nome da comunidade deve ter pelo menos 3 caracteres.'
        elif len(nome.strip()) > 25:
            erros['nome'] = 'O nome da comunidade deve ter no máximo 25 caracteres.'
        
        # Validar descrição
        if not descricao or not descricao.strip():
            erros['descricao'] = 'A descrição da comunidade é obrigatória.'
        elif len(descricao.strip()) < 10:
            erros['descricao'] = 'A descrição deve ter pelo menos 10 caracteres.'
        elif len(descricao.strip()) > 500:
            erros['descricao'] = 'A descrição deve ter no máximo 500 caracteres.'
        
        if erros:
            raise ValidationError(erros)

    @staticmethod
    def validar_imagem(arquivo):
        """
        Valida um arquivo de imagem.
        
        Args:
            arquivo (File): Arquivo a ser validado
            
        Returns:
            bool: True se válido
            
        Raises:
            ValidationError: Se o arquivo for inválido
        """
        if not arquivo:
            return True
        
        erros = {}
        
        # Validar tipo de arquivo
        tipos_permitidos = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if arquivo.content_type not in tipos_permitidos:
            erros['icone'] = 'Tipo de arquivo não permitido. Use JPEG, PNG, GIF ou WEBP.'
        
        # Validar tamanho (máx 5MB)
        tamanho_maximo = 5 * 1024 * 1024  # 5MB
        if arquivo.size > tamanho_maximo:
            erros['icone'] = 'A imagem deve ter no máximo 5MB.'
        
        if erros:
            raise ValidationError(erros)
        
        return True

    @staticmethod
    def obter_comunidades_usuario(usuario):
        """
        Obtém todas as comunidades em que o usuário é convivente.
        
        Args:
            usuario (Usuario): Perfil do usuário
            
        Returns:
            QuerySet: Comunidades do usuário
        """
        if not isinstance(usuario, Usuario):
            return Comunidade.objects.none()
        return usuario.comunidades.all()

    @staticmethod
    def obter_comunidades_moderadas(usuario):
        """
        Obtém todas as comunidades que o usuário modera.
        
        Args:
            usuario (Usuario): Perfil do usuário
            
        Returns:
            QuerySet: Comunidades moderadas pelo usuário
        """
        if not isinstance(usuario, Usuario):
            return Comunidade.objects.none()
        return usuario.comunidades_moderadas.all()

        
    @staticmethod
    @transaction.atomic
    def participar_comunidade(usuario, comunidade_id):
            """
            Permite que um usuário participe de uma comunidade pública.
            
            Args:
                usuario (Usuario): Perfil do usuário que quer participar
                comunidade_id (int): ID da comunidade
                
            Returns:
                bool: True se sucesso
                
            Raises:
                ValidationError: Se a comunidade não existir ou dados inválidos
                ValueError: Se regras de negócio forem violadas (ex: comunidade privada, usuário já membro)
            """
            
            # 1. Validar se o usuário é instância válida
            if not isinstance(usuario, Usuario):
                raise ValueError("Usuário inválido fornecido.")

            # 2. Buscar a comunidade
            try:
                comunidade = Comunidade.objects.get(id=comunidade_id)
            except Comunidade.DoesNotExist:
                raise ValidationError("Comunidade não encontrada.")

            # 3. Verificar se usuário já é membro
            if comunidade.conviventes.filter(id=usuario.id).exists():
                raise ValueError(f"Você já é membro da comunidade '{comunidade.nome}'.")

            # 4. Verificar visibilidade (Regra do CDU)
            # Como não podemos criar modelos de Solicitação, apenas Públicas permitem entrada direta
            if comunidade.tipoVisibilidade == 'privado':
                raise ValueError(
                    "Esta comunidade é privada. "
                )

            # 5. Adicionar usuário aos conviventes
            try:
                comunidade.conviventes.add(usuario)
                # Se quiser salvar logs ou atualizar contadores, faria aqui
                comunidade.save() 
                return True
                
            except Exception as e:
                raise ValueError(f"Erro ao processar a participação: {str(e)}")
    
# de post

class PostService:
    @staticmethod
    def _validar_permissao_postagem(usuario, comunidade):
        """
        Verifica pré-condição: O usuário deve ser membro da comunidade.
        """
        if not comunidade.conviventes.filter(id=usuario.id).exists():
            raise ValueError(f"Apenas membros podem postar na comunidade {comunidade.nome}.")
        return True

    @staticmethod
    def _validar_titulo(titulo):
        """
        Verifica regras do CDU relacionadas ao título do post.
        """
        erros = {}
        if not titulo or not titulo.strip():
            erros['titulo'] = 'O título do post é obrigatório.'
        elif len(titulo.strip()) < 5:
            erros['titulo'] = 'O título do post deve ter pelo menos 5 caracteres.'
        elif len(titulo.strip()) > 50:
            erros['titulo'] = 'O título do post deve ter no máximo 50 caracteres.'
        
        if erros:
            raise ValidationError(erros)

    @staticmethod
    def _validar_conteudo(conteudo):
        """
        Verifica regra do CDU: Fluxo Alternativo I (Conteúdo vazio).
        """
        erros = {}
        if not conteudo or not conteudo.strip():
            erros['conteudo'] = 'O conteúdo do post não pode ser vazio.'
        elif len(conteudo.strip()) < 5:
            # Regra extraída do clean() do seu Model Post
            erros['conteudo'] = 'O conteúdo do post deve ter pelo menos 5 caracteres.'
        
        if erros:
            raise ValidationError(erros)

    @staticmethod
    @transaction.atomic
    def criar_post(usuario, comunidade_id, titulo, conteudo):
        """
        Executa a criação do post.
        """
        # 1. Busca Comunidade
        try:
            comunidade = Comunidade.objects.get(id=comunidade_id)
        except Comunidade.DoesNotExist:
            raise ValueError("Comunidade não encontrada.")

        # 2. Valida Permissão (É membro?)
        PostService._validar_permissao_postagem(usuario, comunidade)

        # 3. Valida Título
        PostService._validar_titulo(titulo)

        # 3. Valida Conteúdo
        PostService._validar_conteudo(conteudo)

        # 4. Cria o Post
        # Nota: O CDU menciona Título e Tags, mas seu Model Post só tem 'conteudo'.
        # Seguindo a regra de não alterar o modelo, salvamos apenas o conteudo.
        post = Post(
            comunidade=comunidade,
            autor=usuario,
            titulo=titulo.strip(),
            conteudo=conteudo.strip()
        )
        
        # Garante validações do model
        post.full_clean()
        post.save()
        
        return post