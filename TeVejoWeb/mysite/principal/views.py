from django.views.generic import TemplateView, DetailView, ListView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

from comunidades.models import Comunidade, Comentario, Post
from comunidades.services import ComunidadeService


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
            context['comunidades_usuario'] = []
            context['comunidades_moderador'] = []
        return context


class HomeView(RedirectView):
    """View da página inicial que redireciona para discussões."""
    url = '/principal/discussoes/'


class DiscussoesView(ComunidadeContextMixin, TemplateView):
    """View de discussões públicas."""
    template_name = 'principal/discussao.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'discussoes'
        context['posts'] = Post.objects.select_related('comunidade', 'autor').order_by('-dataPostagem')
        return context


class ConteudosView(LoginRequiredMixin, ComunidadeContextMixin, TemplateView):
    """View de conteúdos educacionais."""
    template_name = "principal/conteudos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'conteudos'
        return context


class EncontrosView(LoginRequiredMixin, ComunidadeContextMixin, TemplateView):
    """View de encontros."""
    template_name = "principal/encontros.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'encontros'
        return context


class CriarComunidadeView(LoginRequiredMixin, ComunidadeContextMixin, TemplateView):
    """View para criar uma nova comunidade."""
    template_name = "comunidades/criarcomunidade.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'criar_comunidade'
        return context


class GerenciarComunidadesView(LoginRequiredMixin, ComunidadeContextMixin, TemplateView):
    """View para gerenciar comunidades do usuário."""
    template_name = "comunidades/gerenciar_comunidades.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'gerenciar_comunidades'
        return context


class ComunidadeDetailView(LoginRequiredMixin, ComunidadeContextMixin, DetailView):
    """View para exibir detalhes de uma comunidade específica."""
    model = Comunidade
    template_name = "comunidades/comunidade.html"
    context_object_name = "comunidade"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = self.object.posts.all().order_by('-dataPostagem')
        context['comunidade_id'] = self.object.id
        context['active_page'] = 'comunidade'
        return context
