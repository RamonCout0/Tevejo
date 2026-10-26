import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { AuthService } from '../../core/auth.service';
import { ComentarioPostagem, Comunidade, ComunidadeService, Encontro, PostagemComunidade } from '../../services/comunidade.service';
import { EditorTextoComponent } from '../../shared/editor-texto/editor-texto';
import { LIMITES } from '../../shared/limites';
import { IniciaisPipe, TomDaMarcaPipe } from '../../shared/marca';
import { TextoRicoPipe, TextoSimplesPipe } from '../../shared/texto-rico/texto-rico';

@Component({
  selector: 'app-comunidade-detalhe',
  standalone: true,
  imports: [
    CommonModule, FormsModule, RouterLink, EditorTextoComponent,
    IniciaisPipe, TomDaMarcaPipe, TextoRicoPipe, TextoSimplesPipe,
  ],
  templateUrl: './comunidade-detalhe.html',
})
export class ComunidadeDetalheComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private auth = inject(AuthService);
  private comunidadeService = inject(ComunidadeService);

  comunidade = signal<Comunidade | null>(null);
  carregando = signal(false);
  erro = signal<string | null>(null);
  acaoEmCurso = signal(false);
  postagens = signal<PostagemComunidade[]>([]);
  encontros = signal<Encontro[]>([]);
  comentariosAbertos = signal<Record<number, boolean>>({});
  denunciasAbertas = signal<Record<number, boolean>>({});
  comentariosTexto = signal<Record<number, string>>({});
  denunciaMotivo = signal<Record<number, string>>({});
  denunciaDetalhe = signal<Record<number, string>>({});
  // Interações em comentários (por id do comentário-raiz).
  respostasVisiveis = signal<Record<number, boolean>>({});
  respostaComposer = signal<Record<number, boolean>>({});
  respostaTexto = signal<Record<number, string>>({});
  denunciaComentAberta = signal<Record<number, boolean>>({});
  denunciaComentMotivo = signal<Record<number, string>>({});
  denunciaComentDetalhe = signal<Record<number, string>>({});
  interacaoEmCurso = signal<string | null>(null);
  /** Postagens longas abertas com "Ler mais". */
  expandidos = signal<Record<number, boolean>>({});
  /** Descrição da comunidade aberta com "Ver mais". */
  descricaoAberta = signal(false);
  readonly limites = LIMITES;
  sucessoInteracao = signal<string | null>(null);

  readonly autenticado = computed(() => this.auth.isLoggedIn());
  readonly isConvivente = this.auth.isConvivente;
  readonly meuPerfil = this.auth.perfil;
  /** Botão Participar visível para visitantes (caem em /login) e Conviventes. */
  readonly podeVerParticipar = computed(
    () => !this.autenticado() || this.isConvivente(),
  );

  ngOnInit(): void {
    // Reage à troca de :id (ex.: barra lateral) mesmo com o componente reaproveitado.
    this.route.paramMap.subscribe((params) => {
      const id = Number(params.get('id'));
      if (!Number.isFinite(id) || id <= 0) {
        this.router.navigate(['/comunidades']);
        return;
      }
      this.reiniciarEstado();
      this.carregar(id);
    });
  }

  /** Limpa estado de interação ao mudar de comunidade, evitando "vazar" de uma para outra. */
  private reiniciarEstado(): void {
    this.comunidade.set(null);
    this.postagens.set([]);
    this.encontros.set([]);
    this.comentariosAbertos.set({});
    this.denunciasAbertas.set({});
    this.comentariosTexto.set({});
    this.denunciaMotivo.set({});
    this.denunciaDetalhe.set({});
    this.respostasVisiveis.set({});
    this.respostaComposer.set({});
    this.respostaTexto.set({});
    this.denunciaComentAberta.set({});
    this.denunciaComentMotivo.set({});
    this.denunciaComentDetalhe.set({});
    this.interacaoEmCurso.set(null);
    this.sucessoInteracao.set(null);
    this.expandidos.set({});
    this.descricaoAberta.set(false);
    this.erro.set(null);
  }

  carregar(id: number): void {
    this.carregando.set(true);
    this.erro.set(null);
    this.comunidadeService.detalhe(id).subscribe({
      next: (c) => {
        this.comunidade.set(c);
        this.carregarPostagens(c.id);
        this.carregarEncontros(c.id);
        this.carregando.set(false);
      },
      error: (err) => {
        this.carregando.set(false);
        this.erro.set(err?.status === 404 ? 'Comunidade não encontrada.' : 'Erro ao carregar comunidade.');
      },
    });
  }

  carregarEncontros(id: number): void {
    this.comunidadeService.listarEncontros(id).subscribe({
      next: (lista) => this.encontros.set(lista),
      error: () => this.encontros.set([]),
    });
  }

  carregarPostagens(id: number): void {
    this.comunidadeService.listarPostagens(id).subscribe({
      next: (postagens) => this.postagens.set(postagens),
      error: () => this.postagens.set([]),
    });
  }

  postar(): void {
    const c = this.comunidade();
    if (!c) return;
    if (!this.auth.isLoggedIn()) {
      this.router.navigate(['/login']);
      return;
    }
    if (!c.is_membro && !c.is_moderador) {
      this.erro.set('Você precisa participar da comunidade para publicar conteúdos');
      return;
    }
    this.router.navigate(['/comunidades', c.id, 'postar']);
  }

  curtir(postagem: PostagemComunidade): void {
    const c = this.comunidade();
    if (!this.podeInteragir(c) || this.interacaoEmCurso()) return;

    this.interacaoEmCurso.set(`curtir-${postagem.id}`);
    this.erro.set(null);
    this.comunidadeService.curtirPostagem(c.id, postagem.id).subscribe({
      next: (resposta) => {
        this.atualizarPostagem(resposta.postagem);
        this.interacaoEmCurso.set(null);
      },
      error: (err) => this.tratarErroInteracao(err, 'Não foi possível registrar sua curtida.'),
    });
  }

  alternarComentarios(postagem: PostagemComunidade): void {
    this.comentariosAbertos.update((estado) => ({
      ...estado,
      [postagem.id]: !estado[postagem.id],
    }));
    this.denunciasAbertas.update((estado) => ({ ...estado, [postagem.id]: false }));
  }

  alternarDenuncia(postagem: PostagemComunidade): void {
    this.denunciasAbertas.update((estado) => ({
      ...estado,
      [postagem.id]: !estado[postagem.id],
    }));
  }

  comentarioAberto(postagemId: number): boolean {
    return !!this.comentariosAbertos()[postagemId];
  }

  denunciaAberta(postagemId: number): boolean {
    return !!this.denunciasAbertas()[postagemId];
  }

  comentarioValor(postagemId: number): string {
    return this.comentariosTexto()[postagemId] ?? '';
  }

  atualizarComentario(postagemId: number, valor: string): void {
    this.comentariosTexto.update((estado) => ({ ...estado, [postagemId]: valor }));
  }

  motivoValor(postagemId: number): string {
    return this.denunciaMotivo()[postagemId] ?? '';
  }

  atualizarMotivo(postagemId: number, valor: string): void {
    this.denunciaMotivo.update((estado) => ({ ...estado, [postagemId]: valor }));
  }

  detalheDenunciaValor(postagemId: number): string {
    return this.denunciaDetalhe()[postagemId] ?? '';
  }

  atualizarDetalheDenuncia(postagemId: number, valor: string): void {
    this.denunciaDetalhe.update((estado) => ({ ...estado, [postagemId]: valor }));
  }

  comentar(postagem: PostagemComunidade): void {
    const c = this.comunidade();
    const conteudo = this.comentarioValor(postagem.id).trim();
    if (!this.podeInteragir(c) || this.interacaoEmCurso()) return;
    if (!conteudo) {
      this.erro.set('Não foi possível publicar seu comentário. Verifique o conteúdo e tente novamente.');
      return;
    }

    this.interacaoEmCurso.set(`comentar-${postagem.id}`);
    this.erro.set(null);
    this.comunidadeService.comentarPostagem(c.id, postagem.id, { conteudo }).subscribe({
      next: (atualizada) => {
        this.atualizarPostagem(atualizada);
        this.atualizarComentario(postagem.id, '');
        this.comentariosAbertos.update((estado) => ({ ...estado, [postagem.id]: true }));
        this.interacaoEmCurso.set(null);
      },
      error: (err) => this.tratarErroInteracao(err, 'Não foi possível publicar seu comentário. Verifique o conteúdo e tente novamente.'),
    });
  }

  // ----- Interações em comentários (curtir, responder, denunciar) -----

  curtirComentario(postagem: PostagemComunidade, coment: ComentarioPostagem): void {
    const c = this.comunidade();
    if (!this.podeInteragir(c) || this.interacaoEmCurso()) return;

    this.interacaoEmCurso.set(`curtir-coment-${coment.id}`);
    this.erro.set(null);
    this.comunidadeService.curtirComentario(c.id, postagem.id, coment.id).subscribe({
      next: (resposta) => {
        this.atualizarPostagem(resposta.postagem);
        this.interacaoEmCurso.set(null);
      },
      error: (err) => this.tratarErroInteracao(err, 'Não foi possível registrar sua curtida.'),
    });
  }

  alternarRespostas(comentId: number): void {
    this.respostasVisiveis.update((e) => ({ ...e, [comentId]: !e[comentId] }));
  }

  respostaVisivel(comentId: number): boolean {
    return !!this.respostasVisiveis()[comentId];
  }

  /** Abre o compositor de resposta do comentário-raiz. Ao responder uma resposta, menciona o autor. */
  abrirResposta(coment: ComentarioPostagem, ehResposta: boolean): void {
    const raizId = ehResposta ? (coment.parent ?? coment.id) : coment.id;
    this.respostasVisiveis.update((e) => ({ ...e, [raizId]: true }));
    this.respostaComposer.update((e) => ({ ...e, [raizId]: true }));
    if (ehResposta) {
      const mencao = `@${coment.autor} `;
      const atual = this.respostaTexto()[raizId] ?? '';
      if (!atual.includes(mencao)) {
        this.atualizarResposta(raizId, mencao + atual.trimStart());
      }
    }
  }

  fecharResposta(raizId: number): void {
    this.respostaComposer.update((e) => ({ ...e, [raizId]: false }));
    this.atualizarResposta(raizId, '');
  }

  respostaComposerAberta(raizId: number): boolean {
    return !!this.respostaComposer()[raizId];
  }

  respostaValor(raizId: number): string {
    return this.respostaTexto()[raizId] ?? '';
  }

  atualizarResposta(raizId: number, valor: string): void {
    this.respostaTexto.update((e) => ({ ...e, [raizId]: valor }));
  }

  responder(postagem: PostagemComunidade, raizId: number): void {
    const c = this.comunidade();
    const conteudo = this.respostaValor(raizId).trim();
    if (!this.podeInteragir(c) || this.interacaoEmCurso()) return;
    if (!conteudo) {
      this.erro.set('Não foi possível publicar sua resposta. Verifique o conteúdo e tente novamente.');
      return;
    }

    this.interacaoEmCurso.set(`responder-${raizId}`);
    this.erro.set(null);
    this.comunidadeService.comentarPostagem(c.id, postagem.id, { conteudo, parent: raizId }).subscribe({
      next: (atualizada) => {
        this.atualizarPostagem(atualizada);
        this.atualizarResposta(raizId, '');
        this.respostaComposer.update((e) => ({ ...e, [raizId]: false }));
        this.respostasVisiveis.update((e) => ({ ...e, [raizId]: true }));
        this.interacaoEmCurso.set(null);
      },
      error: (err) => this.tratarErroInteracao(err, 'Não foi possível publicar sua resposta.'),
    });
  }

  alternarDenunciaComentario(comentId: number): void {
    this.denunciaComentAberta.update((e) => ({ ...e, [comentId]: !e[comentId] }));
  }

  denunciaComentarioAberta(comentId: number): boolean {
    return !!this.denunciaComentAberta()[comentId];
  }

  motivoComentValor(comentId: number): string {
    return this.denunciaComentMotivo()[comentId] ?? '';
  }

  atualizarMotivoComent(comentId: number, valor: string): void {
    this.denunciaComentMotivo.update((e) => ({ ...e, [comentId]: valor }));
  }

  detalheComentValor(comentId: number): string {
    return this.denunciaComentDetalhe()[comentId] ?? '';
  }

  atualizarDetalheComent(comentId: number, valor: string): void {
    this.denunciaComentDetalhe.update((e) => ({ ...e, [comentId]: valor }));
  }

  denunciarComentario(postagem: PostagemComunidade, coment: ComentarioPostagem): void {
    const c = this.comunidade();
    const motivo = this.motivoComentValor(coment.id);
    if (!this.podeInteragir(c) || this.interacaoEmCurso()) return;
    if (!motivo) {
      this.erro.set('Selecione um motivo para denunciar o comentário.');
      return;
    }

    this.interacaoEmCurso.set(`denunciar-coment-${coment.id}`);
    this.erro.set(null);
    this.sucessoInteracao.set(null);
    this.comunidadeService.denunciarComentario(c.id, postagem.id, coment.id, {
      motivo,
      detalhe: this.detalheComentValor(coment.id),
    }).subscribe({
      next: (resposta) => {
        this.sucessoInteracao.set(resposta.mensagem);
        this.denunciaComentAberta.update((e) => ({ ...e, [coment.id]: false }));
        this.atualizarMotivoComent(coment.id, '');
        this.atualizarDetalheComent(coment.id, '');
        this.interacaoEmCurso.set(null);
      },
      error: (err) => this.tratarErroInteracao(err, 'Não foi possível enviar a denúncia.'),
    });
  }

  denunciar(postagem: PostagemComunidade): void {
    const c = this.comunidade();
    const motivo = this.motivoValor(postagem.id);
    if (!this.podeInteragir(c) || this.interacaoEmCurso()) return;
    if (!motivo) {
      this.erro.set('Selecione um motivo para denunciar a postagem.');
      return;
    }

    this.interacaoEmCurso.set(`denunciar-${postagem.id}`);
    this.erro.set(null);
    this.sucessoInteracao.set(null);
    this.comunidadeService.denunciarPostagem(c.id, postagem.id, {
      motivo,
      detalhe: this.detalheDenunciaValor(postagem.id),
    }).subscribe({
      next: (resposta) => {
        this.sucessoInteracao.set(resposta.mensagem);
        this.denunciasAbertas.update((estado) => ({ ...estado, [postagem.id]: false }));
        this.atualizarMotivo(postagem.id, '');
        this.atualizarDetalheDenuncia(postagem.id, '');
        this.interacaoEmCurso.set(null);
      },
      error: (err) => this.tratarErroInteracao(err, 'Não foi possível enviar a denúncia.'),
    });
  }

  private podeInteragir(c: Comunidade | null): c is Comunidade {
    if (!c) return false;
    if (!this.auth.isLoggedIn()) {
      this.router.navigate(['/login']);
      return false;
    }
    if (!c.is_membro && !c.is_moderador) {
      this.erro.set('Você precisa participar da comunidade para interagir com a postagem.');
      return false;
    }
    return true;
  }

  private atualizarPostagem(postagem: PostagemComunidade): void {
    this.postagens.update((lista) => lista.map((item) => item.id === postagem.id ? postagem : item));
  }

  private tratarErroInteracao(err: any, mensagemPadrao: string): void {
    if (err?.status === 401) {
      this.router.navigate(['/login']);
      return;
    }
    this.erro.set(err?.error?.erro || err?.error?.conteudo?.join?.(' ') || mensagemPadrao);
    this.interacaoEmCurso.set(null);
  }  

  /** Postagens com mais de ~700 caracteres começam recolhidas. */
  ehLongo(conteudo: string): boolean {
    const texto = conteudo ?? '';
    return texto.length > 700 || texto.split(/\n/).length > 14;
  }

  expandido(id: number): boolean {
    return !!this.expandidos()[id];
  }

  descricaoLonga(descricao: string): boolean {
    return (descricao?.length ?? 0) > 220;
  }

  alternarExpandido(id: number): void {
    this.expandidos.update((e) => ({ ...e, [id]: !e[id] }));
  }

  nomeMeu(): string {
    return this.auth.perfil()?.nome || this.auth.username() || '?';
  }

  /** Devolve a URL da foto se o autor é o usuário atual; senão null (cai pra iniciais). */
  fotoDe(autorUsername: string): string | null {
    const me = this.auth.perfil();
    if (!me) return null;
    return autorUsername === me.username ? me.foto : null;
  }

  participar(): void {
    if (!this.auth.isLoggedIn()) {
      this.router.navigate(['/login']);
      return;
    }
    const c = this.comunidade();
    if (!c || this.acaoEmCurso()) return;
    this.acaoEmCurso.set(true);
    this.comunidadeService.participar(c.id).subscribe({
      next: (atualizada) => {
        this.comunidade.set(atualizada);
        this.acaoEmCurso.set(false);
      },
      error: (err) => {
        this.acaoEmCurso.set(false);
        if (err?.status === 401) {
          this.router.navigate(['/login']);
        } else if (err?.status === 403) {
          // Backend pode devolver {erro: "Você foi banido..."} ou {detail: "Apenas Conviventes..."}
          const msg = err?.error?.erro ?? err?.error?.detail
            ?? 'Você não tem permissão para participar desta comunidade.';
          this.erro.set(msg);
        } else {
          this.erro.set('Não foi possível entrar na comunidade.');
        }
      },
    });
  }

  sair(): void {
    const c = this.comunidade();
    if (!c || this.acaoEmCurso()) return;
    if (!confirm(`Deseja sair de "${c.nome}"?`)) return;
    this.acaoEmCurso.set(true);
    this.comunidadeService.sair(c.id).subscribe({
      next: (atualizada) => {
        this.comunidade.set(atualizada);
        this.acaoEmCurso.set(false);
      },
      error: () => {
        this.acaoEmCurso.set(false);
        this.erro.set('Não foi possível sair da comunidade.');
      },
    });
  }
}
