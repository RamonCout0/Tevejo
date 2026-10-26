import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import { Comunidade, ComunidadeService } from '../../services/comunidade.service';
import { CATEGORIAS } from '../../shared/categorias';
import { EditorTextoComponent } from '../../shared/editor-texto/editor-texto';
import { LIMITES } from '../../shared/limites';
import { IniciaisPipe, TomDaMarcaPipe } from '../../shared/marca';
import { RecortarImagemComponent } from '../../shared/recortar-imagem/recortar-imagem';
import { TextoRicoPipe } from '../../shared/texto-rico/texto-rico';

/**
 * Criar comunidade e, em `/comunidades/:id/editar`, editar/excluir (CDU012).
 * As duas telas compartilham o formulário, a prévia e o recorte de imagens.
 */
@Component({
  selector: 'app-criar-comunidade',
  standalone: true,
  imports: [
    CommonModule, FormsModule, RecortarImagemComponent, EditorTextoComponent,
    IniciaisPipe, TomDaMarcaPipe, TextoRicoPipe,
  ],
  templateUrl: './criar-comunidade.html',
  styleUrl: './criar-comunidade.css',
})
export class CriarComunidade implements OnInit {
  private comunidadeService = inject(ComunidadeService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  /** Comunidade em edição; null = modo criação. */
  readonly editando = signal<Comunidade | null>(null);
  readonly modoEdicao = computed(() => this.editando() !== null);
  readonly carregando = signal(false);
  readonly limites = LIMITES;
  readonly categorias = CATEGORIAS;

  nome = '';
  descricao = '';
  categoria = '';
  regras = '';

  fileName = 'Nenhuma imagem selecionada';
  bannerFileName = 'Nenhum banner selecionado';
  readonly imagePreview = signal<string | null>(null);
  readonly bannerPreview = signal<string | null>(null);
  private arquivoIcone: File | null = null;
  private arquivoBanner: File | null = null;
  private removerIcone = false;
  private removerBanner = false;

  enviando = signal(false);
  excluindo = signal(false);
  erro = signal<string | null>(null);

  /** Imagem aguardando recorte e qual campo ela vai preencher. */
  recorte = signal<{ arquivo: File; campo: 'icone' | 'banner' } | null>(null);

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (id > 0) {
      this.carregarParaEdicao(id);
    }
  }

  private carregarParaEdicao(id: number): void {
    this.carregando.set(true);
    this.comunidadeService.detalhe(id).subscribe({
      next: (c) => {
        if (!c.is_moderador) {
          // Pré-condição do CDU012: só o moderador gerencia a comunidade.
          this.router.navigate(['/comunidades', id]);
          return;
        }
        this.nome = c.nome;
        this.descricao = c.descricao;
        this.categoria = c.categoria;
        this.regras = c.regras ?? '';
        this.imagePreview.set(c.icone);
        this.bannerPreview.set(c.banner);
        this.editando.set(c);
        this.carregando.set(false);
      },
      error: (err) => {
        this.carregando.set(false);
        this.erro.set(err?.status === 404 ? 'Comunidade não encontrada.' : 'Não foi possível carregar a comunidade.');
      },
    });
  }

  onIconeSelected(event: Event): void {
    this.abrirRecorte(event, 'icone');
  }

  onBannerSelected(event: Event): void {
    this.abrirRecorte(event, 'banner');
  }

  private abrirRecorte(event: Event, campo: 'icone' | 'banner'): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    input.value = ''; // permite escolher o mesmo arquivo de novo
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      this.erro.set('Selecione um arquivo de imagem.');
      return;
    }
    this.erro.set(null);
    this.recorte.set({ arquivo: file, campo });
  }

  aoRecortar(file: File): void {
    const campo = this.recorte()?.campo;
    this.recorte.set(null);
    const reader = new FileReader();
    if (campo === 'icone') {
      this.arquivoIcone = file;
      this.removerIcone = false;
      this.fileName = file.name;
      reader.onload = () => this.imagePreview.set(reader.result as string);
    } else {
      this.arquivoBanner = file;
      this.removerBanner = false;
      this.bannerFileName = file.name;
      reader.onload = () => this.bannerPreview.set(reader.result as string);
    }
    reader.readAsDataURL(file);
  }

  ehCategoriaDaLista(): boolean {
    return CATEGORIAS.some((c) => c.nome === this.categoria);
  }

  removerImagem(campo: 'icone' | 'banner', evento: Event): void {
    evento.stopPropagation(); // o botão fica dentro da área que abre o seletor
    if (campo === 'icone') {
      this.arquivoIcone = null;
      this.removerIcone = !!this.editando()?.icone;
      this.imagePreview.set(null);
    } else {
      this.arquivoBanner = null;
      this.removerBanner = !!this.editando()?.banner;
      this.bannerPreview.set(null);
    }
  }

  onSubmit(): void {
    if (this.enviando()) return;
    this.erro.set(null);
    if (!this.ehCategoriaDaLista()) {
      this.erro.set('Escolha uma categoria para a comunidade.');
      return;
    }
    this.enviando.set(true);

    const comunidade = this.editando();
    const requisicao = comunidade
      ? this.comunidadeService.atualizar(comunidade.id, {
          nome: this.nome,
          descricao: this.descricao,
          categoria: this.categoria,
          regras: this.regras,
          icone: this.arquivoIcone,
          banner: this.arquivoBanner,
          removerIcone: this.removerIcone,
          removerBanner: this.removerBanner,
        })
      : this.comunidadeService.criar({
          nome: this.nome,
          descricao: this.descricao,
          categoria: this.categoria,
          regras: this.regras,
          icone: this.arquivoIcone,
          banner: this.arquivoBanner,
        });

    requisicao.subscribe({
      next: (salva) => {
        this.enviando.set(false);
        this.router.navigate(['/comunidades', salva.id]);
      },
      error: (err) => {
        this.enviando.set(false);
        this.erro.set(this.mensagemErro(err));
      },
    });
  }

  /** CDU012 - Fluxo Alternativo I. */
  excluir(): void {
    const comunidade = this.editando();
    if (!comunidade || this.excluindo()) return;
    const confirmado = confirm(
      `Excluir a comunidade "${comunidade.nome}"? Todas as postagens, comentários e encontros ` +
        'serão removidos permanentemente.',
    );
    if (!confirmado) return;

    this.erro.set(null);
    this.excluindo.set(true);
    this.comunidadeService.excluir(comunidade.id).subscribe({
      next: () => this.router.navigate(['/comunidades']),
      error: (err) => {
        this.excluindo.set(false);
        this.erro.set(this.mensagemErro(err, 'Não foi possível excluir a comunidade.'));
      },
    });
  }

  cancelar(): void {
    const comunidade = this.editando();
    this.router.navigate(comunidade ? ['/comunidades', comunidade.id] : ['/comunidades']);
  }

  private mensagemErro(err: any, padrao?: string): string {
    if (err?.status === 401) {
      return 'Faça login para continuar.';
    }
    if (err?.status === 403) {
      return err?.error?.erro ?? (this.modoEdicao()
        ? 'Apenas o moderador pode gerenciar esta comunidade.'
        : 'Apenas Conviventes podem criar comunidades.');
    }
    if (err?.error && typeof err.error === 'object') {
      return Object.values(err.error).flat().join(' ');
    }
    return padrao ?? (this.modoEdicao() ? 'Não foi possível salvar as alterações.' : 'Não foi possível criar a comunidade.');
  }
}
