from django.views.generic import FormView, TemplateView, View
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .forms import LoginForm, CadastroForm
from .services import AuthenticationService, RegistrationService


# ============================================================
# CSRF FAILURE
# ============================================================

def csrf_failure(request, reason=""):
    """
    Redireciona para login ou cadastro se o CSRF falhar,
    exibindo mensagem de sessão expirada.
    """
    messages.error(request, "Sua sessão expirou. Por favor, tente novamente.")

    if "cadastro" in request.path:
        return redirect("usuarios:cadastro")

    return redirect("usuarios:login")


# ============================================================
# LOGIN
# ============================================================

@method_decorator(csrf_protect, name='dispatch')
class LoginView(FormView):
    """View de login de usuários."""
    form_class = LoginForm
    template_name = "usuarios/login.html"
    success_url = reverse_lazy('principal:discussoes')

    def form_valid(self, form):
        username = form.cleaned_data["username"].strip()
        password = form.cleaned_data["password"]

        result = AuthenticationService.authenticate(username, password)

        if result["success"]:
            # Login bem-sucedido
            auth_login(self.request, result["user"])
            messages.success(self.request, f"Bem-vindo(a), {result['user'].nome}!")
            
            # Redirecionar para a página solicitada ou página padrão
            next_url = self.request.GET.get('next', self.success_url)
            return redirect(next_url) if next_url else super().form_valid(form)
        
        # Erro de autenticação
        form.add_error(None, "Usuário ou senha inválidos.")
        return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        # Redirecionar se já está autenticado
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)


# ============================================================
# CADASTRO
# ============================================================

@method_decorator(csrf_protect, name='dispatch')
class CadastroView(FormView):
    """View para cadastro de novos usuários."""
    form_class = CadastroForm
    template_name = "usuarios/cadastro.html"
    success_url = reverse_lazy('usuarios:login')

    def form_valid(self, form):
        result = RegistrationService.register(
            username=form.cleaned_data["username"],
            nome=form.cleaned_data["nome"],
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
            foto=form.cleaned_data.get("foto"),
            biografia=form.cleaned_data.get("biografia"),
        )

        if result["success"]:
            # Cadastro bem-sucedido
            messages.success(
                self.request,
                "Conta criada com sucesso! Faça login para continuar."
            )
            return super().form_valid(form)

        # Erros do service ficam no formulário
        if result["error"] == "email_exists":
            form.add_error(None, "E-mail já cadastrado.")
        elif result["error"] == "username_exists":
            form.add_error(None, "Nome de usuário já cadastrado.")
        else:
            form.add_error(None, "Erro ao criar usuário. Tente novamente.")
        
        return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        # Redirecionar se já está autenticado
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)


# ============================================================
# PERFIL
# ============================================================

class PerfilView(TemplateView):
    """View do perfil do usuário."""
    template_name = "usuarios/perfil.html"
    
    def get(self, request, *args, **kwargs):
        """Redireciona se não autenticado."""
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        from usuarios.models import Curador
        from comunidades.models import Comentario
        from collections import OrderedDict
        
        context['perfil'] = user
        
        # Verifica se é curador tentando acessar como Curador
        is_curador = False
        try:
            # Tenta pegar a instância de Curador
            curador = Curador.objects.get(pk=user.pk)
            is_curador = True
            context['conteudos'] = curador.conteudos.all()
            context['especialidade'] = curador.especialidade
        except Curador.DoesNotExist:
            is_curador = False
        
        context['is_curador'] = is_curador
        
        if not is_curador:
            # Se for convivente, busca comunidades e comentários agrupados
            context['comunidades'] = user.comunidades.all()
            
            # Agrupar comentários por comunidade, mantendo ordem
            comentarios = Comentario.objects.filter(
                autor=user
            ).select_related('post', 'post__comunidade').order_by('-dataComentario')
            
            # Criar dicionário agrupado mantendo ordem de primeira aparição
            comentarios_por_comunidade = OrderedDict()
            for comentario in comentarios:
                comunidade = comentario.post.comunidade
                if comunidade not in comentarios_por_comunidade:
                    comentarios_por_comunidade[comunidade] = []
                comentarios_por_comunidade[comunidade].append(comentario)
            
            context['comentarios_por_comunidade'] = comentarios_por_comunidade
        
        return context


# ============================================================
# ACESSO NEGADO
# ============================================================

class AcessoNegadoView(TemplateView):
    """
    Página exibida quando o usuário não tem permissão para acessar um recurso.
    """
    template_name = "usuarios/acesso_negado.html"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        response.status_code = 403
        return response


# ============================================================
# LOGOUT
# ============================================================

class LogoutView(TemplateView):
    """
    Desloga o usuário e adiciona mensagem de informação.
    """
    success_url = reverse_lazy('usuarios:login')

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        messages.info(request, "Você saiu da sua conta com sucesso.")
        return redirect(self.success_url)


# ============================================================
# EDITAR FOTO DO PERFIL
# ============================================================

@require_http_methods(["POST"])
def editar_foto_perfil(request):
    """Atualiza a foto do perfil do usuário."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Não autenticado'}, status=401)
    
    if 'foto' not in request.FILES:
        return JsonResponse({'error': 'Nenhuma foto enviada'}, status=400)
    
    try:
        user = request.user
        user.foto = request.FILES['foto']
        user.save()
        return JsonResponse({
            'success': True,
            'message': 'Foto atualizada com sucesso!',
            'foto_url': user.foto.url
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ============================================================
# EDITAR BIOGRAFIA DO PERFIL
# ============================================================

@require_http_methods(["POST"])
def editar_biografia_perfil(request):
    """Atualiza a biografia do usuário."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Não autenticado'}, status=401)
    
    biografia = request.POST.get('biografia', '').strip()
    
    if len(biografia) < 5:
        return JsonResponse({'error': 'Biografia deve ter pelo menos 5 caracteres'}, status=400)
    
    if len(biografia) > 500:
        return JsonResponse({'error': 'Biografia não pode ter mais de 500 caracteres'}, status=400)
    
    try:
        user = request.user
        user.biografia = biografia
        user.save()
        return JsonResponse({
            'success': True,
            'message': 'Biografia atualizada com sucesso!',
            'biografia': user.biografia
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
