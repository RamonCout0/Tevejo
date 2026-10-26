from django.views.generic import (
    CreateView, ListView, RedirectView, TemplateView, DetailView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.http import Http404, JsonResponse
from django.db.models import Q

from .services import ComunidadeService, PostService
from .models import Comunidade, Post
from usuarios.mixins import RoleRequiredMixin
from usuarios.models import Usuario


class ComunidadeContextMixin:
    """Mixin para adicionar contexto de comunidades do usuário."""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['comunidades_usuario'] = ComunidadeService.obter_comunidades_usuario(
                self.request.user
            )
            context['comunidades_moderador'] = ComunidadeService.obter_comunidades_moderadas(
                self.request.user
            )
        else:
            context['comunidades_moderador'] = []
            context['comunidades_usuario'] = []
        return context


class CriarComunidadeView(RoleRequiredMixin, ComunidadeContextMixin, CreateView):
    """View para criar uma nova comunidade. Apenas conviventes podem criar."""
    required_roles = ['convivente']
    model = Comunidade
    template_name = 'comunidades/criarcomunidade.html'
    fields = ['nome', 'descricao', 'icone']
    success_url = reverse_lazy('principal:discussoes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'criar_comunidade'
        return context

    def form_valid(self, form):
        try:
            nome = form.cleaned_data.get('nome', '').strip()
            descricao = form.cleaned_data.get('descricao', '').strip()
            icone = form.cleaned_data.get('icone')
            
            # Validar imagem se fornecida
            if icone:
                ComunidadeService.validar_imagem(icone)
            
            # Criar comunidade usando o service
            comunidade = ComunidadeService.criar_comunidade(
                nome=nome,
                descricao=descricao,
                criador=self.request.user,
                icone=icone
            )
            
            messages.success(
                self.request,
                f'Comunidade "{comunidade.nome}" criada com sucesso!'
            )
            
            # ✅ Redireciona diretamente (o service já salvou)
            return redirect('principal:comunidade', pk=comunidade.id)
            
        except ValidationError as e:
            if hasattr(e, 'message_dict'):
                for campo, erros in e.message_dict.items():
                    for erro in erros:
                        messages.error(self.request, f'{campo}: {erro}')
            else:
                messages.error(self.request, str(e))
            return self.form_invalid(form)
        except ValueError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(
                self.request, 
                f'Erro inesperado ao criar comunidade: {str(e)}'
            )
            return self.form_invalid(form)


class ParticiparComunidadeView(RoleRequiredMixin, LoginRequiredMixin, RedirectView):
    """Permite que um usuário logado participe de uma comunidade."""
    required_roles = ['convivente']

    def get_redirect_url(self, *args, **kwargs):
        comunidade_id = kwargs.get('comunidade_id')
        comunidade = get_object_or_404(Comunidade, id=comunidade_id)
        usuario = self.request.user

        if comunidade.conviventes.filter(id=usuario.id).exists():
            messages.warning(
                self.request,
                f"Você já participa da comunidade {comunidade.nome}!"
            )
        else:
            comunidade.conviventes.add(usuario)
            messages.success(
                self.request,
                f"Bem-vindo(a) à comunidade {comunidade.nome}!"
            )

        return reverse_lazy('principal:comunidade', kwargs={'pk': comunidade.id})


class CriarPostView(RoleRequiredMixin, ComunidadeContextMixin, CreateView):
    """Cria um novo post em uma comunidade. Apenas conviventes podem postar."""
    required_roles = ['convivente']
    model = Post  # Será usado PostService
    template_name = 'comunidades/criarpost.html'
    fields = ['titulo', 'conteudo']
    success_url = reverse_lazy('principal:discussoes')

    def get_success_url(self):
        return reverse_lazy('principal:comunidade', kwargs={'pk': self.comunidade_id})

    def dispatch(self, request, *args, **kwargs):
        self.comunidade_id = kwargs.get('comunidade_id')
        self.comunidade = get_object_or_404(Comunidade, id=self.comunidade_id)
        
        # Verificar se o usuário é membro da comunidade
        if not self.comunidade.conviventes.filter(id=request.user.id).exists():
            messages.error(request, "Você não é membro desta comunidade.")
            raise Http404("Você não tem permissão para postar nesta comunidade.")
        
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comunidade'] = self.comunidade
        context['active_page'] = 'comunidade'
        return context

    def post(self, request, *args, **kwargs):
        titulo = request.POST.get('titulo')
        conteudo = request.POST.get('conteudo')
        
        try:
            PostService.criar_post(
                usuario=request.user,
                comunidade_id=self.comunidade_id,
                titulo=titulo,
                conteudo=conteudo
            )
            messages.success(request, "Post realizado com sucesso!")
            return redirect(self.get_success_url())
        except ValidationError as e:
            if hasattr(e, 'message_dict'):
                for campo, erros in e.message_dict.items():
                    for erro in erros:
                        messages.error(request, f"{erro}")
            else:
                messages.error(request, str(e))
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Erro ao criar post: {str(e)}")
        
        return redirect(self.get_success_url())


class SairComunidadeView(LoginRequiredMixin, RedirectView):
    """Remove o usuário de uma comunidade."""
    
    def get_redirect_url(self, *args, **kwargs):
        comunidade_id = kwargs.get('comunidade_id')
        comunidade = get_object_or_404(Comunidade, id=comunidade_id)
        usuario = self.request.user

        if comunidade.conviventes.filter(id=usuario.id).exists():
            comunidade.conviventes.remove(usuario)
            messages.success(
                self.request,
                f"Você saiu da comunidade {comunidade.nome}."
            )
        else:
            messages.warning(
                self.request,
                "Você não participa desta comunidade!"
            )

        return reverse_lazy('principal:comunidade', kwargs={'pk': comunidade.id})


class ExplorarComunidadesView(RoleRequiredMixin, LoginRequiredMixin, ComunidadeContextMixin, ListView):
    """Lista todas as comunidades disponíveis para exploração."""
    required_roles = ['convivente']
    model = Comunidade
    template_name = 'comunidades/explorar_comunidades.html'
    context_object_name = 'comunidades'
    paginate_by = 10

    def get_queryset(self):
        return Comunidade.objects.order_by('-dataCriacao')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'explorar_comunidades'
        return context


class ComunidadeView(RoleRequiredMixin, ComunidadeContextMixin, LoginRequiredMixin, DetailView):
    """Exibe detalhes de uma comunidade específica."""
    required_roles = ['convivente']
    model = Comunidade
    template_name = 'comunidades/comunidade.html'
    context_object_name = 'comunidade'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = self.object.posts.all().order_by('-dataPostagem')
        context['comunidade_id'] = self.object.id
        context['active_page'] = 'comunidade'
        
        return context


class ModerancaoView(ComunidadeContextMixin, TemplateView):
    """View para moderação de comunidades."""
    template_name = 'comunidades/moderação.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'comunidade'
        return context


class DiscussaoView(ComunidadeContextMixin, TemplateView):
    """View para discussões públicas."""
    template_name = 'comunidades/comunidade.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'comunidade'
        return context


class BuscarComunidadesAPIView(View):
    """API para buscar comunidades em tempo real."""
    
    def get(self, request):
        query = request.GET.get('q', '').strip()
        
        if not query or len(query) < 2:
            return JsonResponse({'resultados': []})
        
        # Buscar comunidades por nome ou descrição
        comunidades = Comunidade.objects.filter(
            Q(nome__icontains=query) | Q(descricao__icontains=query)
        ).order_by('nome')[:10]  # Limitar a 10 resultados
        
        resultados = []
        for comunidade in comunidades:
            resultados.append({
                'id': comunidade.id,
                'nome': comunidade.nome,
                'descricao': comunidade.descricao[:100] + ('...' if len(comunidade.descricao) > 100 else ''),
                'membros': comunidade.conviventes.count(),
                'icone': comunidade.icone.url if comunidade.icone else None,
                'url': f'/comunidade/{comunidade.id}/'
            })
        
        return JsonResponse({'resultados': resultados})