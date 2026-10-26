from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from comunidades.services import ComunidadeService
from .services import ConteudoService
from .models import ConteudoEducacional
from usuarios.mixins import RoleRequiredMixin
from usuarios.models import Curador


class ListaConteudosView(ListView):
    """Lista conteúdos com filtro opcional por tag."""
    model = ConteudoEducacional
    template_name = 'conteudos/conteudos.html'
    context_object_name = 'conteudos'
    paginate_by = 10

    def get_queryset(self):
        conteudos = ConteudoService.obter_conteudos_publicados()
        tag_id = self.request.GET.get('tag')
        
        if tag_id:
            conteudos = conteudos.filter(tipos__id=tag_id)
        
        return conteudos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = ConteudoService.obter_tags()
        context['tag_ativa'] = int(self.request.GET.get('tag')) if self.request.GET.get('tag') else None
        context['active_page'] = 'conteudos'
        
        # Verifica se o usuário logado é um curador
        if self.request.user.is_authenticated:
            context['eh_curador'] = Curador.objects.filter(pk=self.request.user.pk).exists()
            context['comunidades_usuario'] = ComunidadeService.obter_comunidades_usuario(
                self.request.user
            )
            context['comunidades_moderador'] = ComunidadeService.obter_comunidades_moderadas(
                self.request.user
            )
        else:
            context['eh_curador'] = False
            context['comunidades_usuario'] = []
            context['comunidades_moderador'] = []
        
        return context


class CriarConteudoView(RoleRequiredMixin, CreateView):
    """View para criação de novos conteúdos. Apenas curadores podem criar."""
    required_roles = ['curador']
    model = ConteudoEducacional
    template_name = 'conteudos/criar_editar_conteudo.html'
    fields = ['titulo', 'fonte', 'descricao', 'tipos']
    success_url = reverse_lazy('conteudos:conteudos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Novo Conteúdo'
        context['tags'] = ConteudoService.obter_tags()
        return context

    def form_valid(self, form):
        try:
            curador = Curador.objects.get(pk=self.request.user.pk)
            form.instance.curador = curador
            
            # Validar dados antes de salvar
            ConteudoService._validar_dados_conteudo(
                form.cleaned_data.get('titulo'),
                form.cleaned_data.get('fonte'),
                form.cleaned_data.get('descricao'),
                form.cleaned_data.get('tipos')
            )
            
            messages.success(self.request, 'Conteúdo publicado com sucesso!')
            return super().form_valid(form)
        except (ValidationError, ValueError) as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f'Erro ao criar conteúdo: {str(e)}')
            return self.form_invalid(form)


class EditarConteudoView(RoleRequiredMixin, UpdateView):
    """View para edição de conteúdos existentes. Apenas curadores podem editar."""
    required_roles = ['curador']
    model = ConteudoEducacional
    template_name = 'conteudos/criar_editar_conteudo.html'
    fields = ['titulo', 'fonte', 'descricao', 'tipos']
    success_url = reverse_lazy('conteudos:conteudos')
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar Conteúdo'
        context['tags'] = ConteudoService.obter_tags()
        context['tipos_selecionados'] = list(
            self.object.tipos.values_list('id', flat=True)
        )
        return context

    def form_valid(self, form):
        try:
            curador = Curador.objects.get(pk=self.request.user.pk)
            
            # Verificar se é o proprietário
            if form.instance.curador != curador:
                messages.error(
                    self.request, 
                    'Você só pode editar conteúdos que você mesmo publicou.'
                )
                return self.form_invalid(form)
            
            # Validar dados
            ConteudoService._validar_dados_conteudo(
                form.cleaned_data.get('titulo'),
                form.cleaned_data.get('fonte'),
                form.cleaned_data.get('descricao'),
                form.cleaned_data.get('tipos')
            )
            
            messages.success(self.request, 'Conteúdo atualizado com sucesso!')
            return super().form_valid(form)
        except (ValidationError, ValueError) as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f'Erro ao editar conteúdo: {str(e)}')
            return self.form_invalid(form)


class DeletarConteudoView(RoleRequiredMixin, DeleteView):
    """View para exclusão de conteúdo. Apenas curadores podem deletar."""
    required_roles = ['curador']
    model = ConteudoEducacional
    success_url = reverse_lazy('conteudos:conteudos')
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        try:
            curador = Curador.objects.get(pk=self.request.user.pk)
            self.object = self.get_object()
            
            # Verificar se é o proprietário
            if self.object.curador != curador:
                messages.error(
                    self.request,
                    'Você só pode deletar conteúdos que você mesmo publicou.'
                )
                return redirect(self.success_url)
            
            messages.success(self.request, 'Conteúdo removido permanentemente.')
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(self.request, str(e))
            return redirect(self.success_url)


class VerConteudoView(DetailView):
    """Visualizar conteúdo. Qualquer um pode visualizar."""
    model = ConteudoEducacional
    template_name = 'conteudos/ver_conteudo.html'
    context_object_name = 'conteudo'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            context['eh_curador'] = Curador.objects.filter(
                pk=self.request.user.pk
            ).exists()
        else:
            context['eh_curador'] = False
        
        return context
