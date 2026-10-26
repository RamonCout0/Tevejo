import { Component, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

import { AuthService } from '../../core/auth.service';

interface Caminho {
  titulo: string;
  descricao: string;
  icone: string;
  /** Classe de cor da marca (tv-tom-0 … tv-tom-6). */
  tom: string;
  rota: string;
  acao: string;
}

/** CDU028 - Visualizar Página Inicial: boas-vindas e os caminhos da plataforma. */
@Component({
  selector: 'app-inicio',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './inicio.html',
})
export class InicioComponent {
  private auth = inject(AuthService);

  readonly logado = computed(() => !!this.auth.username());

  readonly primeiroNome = computed(() => {
    const p = this.auth.perfil();
    const nome = (p?.nome || this.auth.username() || '').trim();
    return nome.split(' ')[0];
  });

  readonly caminhos = computed<Caminho[]>(() => {
    const logado = this.logado();
    const lista: Caminho[] = [
      {
        titulo: 'Aprender sobre o TEA',
        descricao: 'Conteúdos confiáveis, escritos por curadores e sempre com a fonte.',
        icone: 'fas fa-book-open',
        tom: 'tv-tom-0',
        rota: '/conteudo-educacional',
        acao: 'Ver conteúdos',
      },
      {
        titulo: 'Conversar com quem vive o mesmo',
        descricao: 'Comunidades sobre rotina, escola, direitos, sensibilidade e muito mais.',
        icone: 'fas fa-users',
        tom: 'tv-tom-2',
        rota: '/comunidades',
        acao: 'Explorar comunidades',
      },
      {
        titulo: 'Ver o que estão conversando',
        descricao: 'Dúvidas, conquistas e experiências postadas nas comunidades.',
        icone: 'fas fa-comments',
        tom: 'tv-tom-1',
        rota: '/discussoes',
        acao: 'Ver discussões',
      },
      {
        titulo: 'Participar de encontros',
        descricao: 'Rodas de conversa e eventos, presenciais ou on-line, marcados pelas comunidades.',
        icone: 'far fa-calendar',
        tom: 'tv-tom-4',
        rota: '/encontros',
        acao: logado ? 'Ver encontros' : 'Entre para ver',
      },
      {
        titulo: 'Tirar uma dúvida sobre o site',
        descricao: 'Respostas rápidas e ilustradas para as dúvidas mais comuns.',
        icone: 'far fa-circle-question',
        tom: 'tv-tom-5',
        rota: '/ajuda',
        acao: 'Abrir a ajuda',
      },
    ];

    if (!logado) {
      lista.push({
        titulo: 'Quero fazer parte',
        descricao: 'Crie sua conta gratuita para participar das comunidades e dos encontros.',
        icone: 'fas fa-seedling',
        tom: 'tv-tom-6',
        rota: '/cadastro',
        acao: 'Criar conta',
      });
    } else if (this.auth.isConvivente()) {
      lista.push({
        titulo: 'Criar minha comunidade',
        descricao: 'Reúna pessoas em torno de um assunto e cuide da conversa como moderador(a).',
        icone: 'fas fa-circle-plus',
        tom: 'tv-tom-6',
        rota: '/criar-comunidade',
        acao: 'Criar comunidade',
      });
    }
    return lista;
  });
}
