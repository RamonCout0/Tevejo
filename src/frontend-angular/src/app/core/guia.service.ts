import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';

import { environment } from '../../environments/environment';
import { AuthService, PerfilUsuario } from './auth.service';

/**
 * Um passo do guia condutor (CDU026).
 *
 * `alvo` é o valor do atributo `data-guia` do elemento destacado; sem alvo o
 * balão aparece no centro da tela. `rota` é aberta antes de mostrar o passo.
 */
export interface PassoGuia {
  id: string;
  titulo: string;
  texto: string;
  alvo?: string;
  rota?: string;
  /** O alvo fica no menu lateral (no celular o menu é aberto sozinho). */
  noMenu?: boolean;
  /** Só aparece para quem tem esse papel. */
  papel?: 'convivente' | 'curador';
}

const PASSOS: PassoGuia[] = [
  {
    id: 'boas-vindas',
    titulo: 'Oi! Eu sou o Gui 👋',
    texto: 'Vou te mostrar, em poucos passos, como o TeVejo funciona. Você pode sair quando quiser e me chamar de novo pelo botão de ajuda.',
  },
  {
    id: 'discussoes',
    alvo: 'menu-discussoes',
    noMenu: true,
    titulo: 'Discussões públicas',
    texto: 'Aqui aparecem as conversas mais recentes das comunidades: dúvidas, conquistas e experiências de outras famílias.',
  },
  {
    id: 'conteudos',
    alvo: 'menu-conteudos',
    noMenu: true,
    titulo: 'Conteúdos educacionais',
    texto: 'Textos sobre o autismo revisados por curadores (profissionais). Informação confiável, sem achismo.',
  },
  {
    id: 'comunidades',
    alvo: 'menu-comunidades',
    noMenu: true,
    titulo: 'Comunidades',
    texto: 'Grupos de pessoas que conversam sobre um assunto em comum, como escola, terapias ou direitos. Você pode participar de quantas quiser.',
  },
  {
    id: 'busca-comunidades',
    rota: '/comunidades',
    alvo: 'busca-comunidades',
    titulo: 'Encontre a sua comunidade',
    texto: 'Digite o que procura ou toque em uma categoria. Ao abrir uma comunidade, toque em "Participar" para entrar.',
  },
  {
    id: 'criar-nome',
    rota: '/criar-comunidade',
    alvo: 'cc-nome',
    papel: 'convivente',
    titulo: 'Como criar uma comunidade',
    texto: 'Não achou um grupo do seu jeito? Crie o seu! Comece dando um nome fácil de entender e uma descrição do que vocês vão conversar.',
  },
  {
    id: 'criar-categoria',
    rota: '/criar-comunidade',
    alvo: 'cc-categoria',
    papel: 'convivente',
    titulo: 'Escolha o assunto',
    texto: 'Toque na categoria que mais combina. É por ela que outras pessoas vão encontrar a sua comunidade.',
  },
  {
    id: 'criar-imagens',
    rota: '/criar-comunidade',
    alvo: 'cc-imagens',
    papel: 'convivente',
    titulo: 'Deixe com a sua cara',
    texto: 'Coloque um ícone e um banner. Depois de escolher a foto, dá para arrastar e dar zoom para ajustar o recorte.',
  },
  {
    id: 'criar-confirmar',
    rota: '/criar-comunidade',
    alvo: 'cc-criar',
    papel: 'convivente',
    titulo: 'Pronto para criar',
    texto: 'Ao tocar em "Criar comunidade", você vira moderador(a): pode postar, criar encontros e cuidar para que todos se sintam acolhidos.',
  },
  {
    id: 'publicar-conteudo',
    rota: '/conteudo-educacional',
    alvo: 'publicar-conteudo',
    papel: 'curador',
    titulo: 'Publique conteúdos',
    texto: 'Como curador(a), é por aqui que você publica materiais confiáveis para as famílias.',
  },
  {
    id: 'encontros',
    alvo: 'menu-encontros',
    noMenu: true,
    titulo: 'Encontros',
    texto: 'Rodas de conversa e passeios marcados pelas comunidades, presenciais ou online.',
  },
  {
    id: 'perfil',
    alvo: 'usuario',
    noMenu: true,
    titulo: 'Seu perfil',
    texto: 'Toque aqui para trocar sua foto, escrever sobre você e ver suas postagens. O botão ao lado serve para sair da conta.',
  },
  {
    id: 'ajuda',
    alvo: 'botao-ajuda',
    titulo: 'Estou sempre por aqui',
    texto: 'Sempre que tiver dúvida, toque neste botão: dá para refazer este guia ou ler as perguntas frequentes.',
  },
];

@Injectable({ providedIn: 'root' })
export class GuiaService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private auth = inject(AuthService);

  /** Tour em andamento. */
  readonly ativo = signal(false);
  readonly indice = signal(0);
  /** O convite foi fechado nesta sessão (antes da resposta chegar do servidor). */
  private readonly conviteFechado = signal(false);
  /** Destaca o botão de ajuda por alguns segundos (depois de recusar o convite). */
  readonly destacarAjuda = signal(false);

  /** Passos que valem para o papel de quem está logado. */
  readonly passos = computed(() => {
    const perfil = this.auth.perfil();
    return PASSOS.filter((p) => !p.papel || this.temPapel(perfil, p.papel));
  });

  readonly passoAtual = computed(() => this.passos()[this.indice()] ?? null);
  readonly ehPrimeiro = computed(() => this.indice() === 0);
  readonly ehUltimo = computed(() => this.indice() === this.passos().length - 1);

  /** No celular o menu lateral precisa estar aberto para mostrar o alvo. */
  readonly precisaMenu = computed(() => this.ativo() && !!this.passoAtual()?.noMenu);

  /** CDU026: convite no primeiro acesso (depois do termo de consentimento). */
  readonly mostrarConvite = computed(() => {
    const perfil = this.auth.perfil();
    return !!perfil
      && perfil.mostrar_convite_guia
      && !perfil.precisa_aceitar_termo
      && !this.conviteFechado()
      && !this.ativo();
  });

  /** Resposta ao convite: "sim" inicia o guia; "agora não" mostra onde fica a ajuda. */
  responderConvite(aceitou: boolean): void {
    this.conviteFechado.set(true);
    this.http.post(`${environment.apiUrl}/usuarios/me/guia/`, {}).subscribe({
      next: () => {
        const perfil = this.auth.perfil();
        if (perfil) this.auth.perfil.set({ ...perfil, mostrar_convite_guia: false });
      },
      error: () => {},
    });
    if (aceitou) {
      this.iniciar();
    } else {
      this.destacarAjuda.set(true);
      setTimeout(() => this.destacarAjuda.set(false), 6000);
    }
  }

  iniciar(): void {
    this.indice.set(0);
    this.ativo.set(true);
    this.irParaRotaDoPasso();
  }

  proximo(): void {
    if (this.ehUltimo()) {
      this.encerrar();
      return;
    }
    this.indice.update((i) => i + 1);
    this.irParaRotaDoPasso();
  }

  anterior(): void {
    if (this.ehPrimeiro()) return;
    this.indice.update((i) => i - 1);
    this.irParaRotaDoPasso();
  }

  encerrar(): void {
    this.ativo.set(false);
  }

  private irParaRotaDoPasso(): void {
    const rota = this.passoAtual()?.rota;
    if (rota && this.router.url.split('?')[0] !== rota) {
      this.router.navigateByUrl(rota);
    }
  }

  private temPapel(perfil: PerfilUsuario | null, papel: 'convivente' | 'curador'): boolean {
    if (!perfil) return false;
    return papel === 'convivente' ? perfil.is_convivente : perfil.is_curador;
  }
}
