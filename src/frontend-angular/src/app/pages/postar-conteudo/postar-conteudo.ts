import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { ConteudoService } from '../../services/conteudo.service';
import { Tag, TagsService } from '../../services/tags.service';
import { EditorTextoComponent } from '../../shared/editor-texto/editor-texto';
import { LIMITES } from '../../shared/limites';

interface TagSelecionavel extends Tag {
  selecionada: boolean;
}

@Component({
  selector: 'app-postar-conteudo',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule, EditorTextoComponent],
  templateUrl: './postar-conteudo.html',
  styleUrl: './postar-conteudo.css',
})
export class PostarConteudoComponent implements OnInit {
  private tagsService = inject(TagsService);
  private conteudoService = inject(ConteudoService);
  private router = inject(Router);

  tituloConteudo = '';
  fonteConteudo = '';
  descricaoConteudo = '';
  novaTag = '';
  readonly limites = LIMITES;

  tags = signal<TagSelecionavel[]>([]);
  enviando = signal(false);
  criandoTag = signal(false);
  erro = signal<string | null>(null);

  ngOnInit(): void {
    this.tagsService.listar().subscribe({
      next: (tags) => this.tags.set(tags.map((t) => ({ ...t, selecionada: false }))),
      error: () => this.erro.set('Não foi possível carregar as tags.'),
    });
  }

  toggleTag(tag: TagSelecionavel): void {
    this.tags.update((arr) =>
      arr.map((t) => (t.id === tag.id ? { ...t, selecionada: !t.selecionada } : t))
    );
  }

  criarTag(): void {
    const nome = this.novaTag.trim();
    if (this.criandoTag() || !nome) return;
    if (nome.length < 3) {
      this.erro.set('O nome da categoria deve ter pelo menos 3 caracteres.');
      return;
    }
    const existente = this.tags().find((t) => t.nome.toLowerCase() === nome.toLowerCase());
    if (existente) {
      if (!existente.selecionada) this.toggleTag(existente);
      this.novaTag = '';
      return;
    }

    this.erro.set(null);
    this.criandoTag.set(true);
    this.tagsService.criar(nome).subscribe({
      next: (tag) => {
        this.tags.update((arr) => [...arr, { ...tag, selecionada: true }]);
        this.novaTag = '';
        this.criandoTag.set(false);
      },
      error: () => {
        this.erro.set('Não foi possível criar a categoria.');
        this.criandoTag.set(false);
      },
    });
  }

  onSubmit(): void {
    if (this.enviando()) return;
    this.erro.set(null);

    const tipos_ids = this.tags()
      .filter((t) => t.selecionada)
      .map((t) => t.id);

    this.enviando.set(true);
    this.conteudoService
      .criar({
        titulo: this.tituloConteudo,
        fonte: this.fonteConteudo,
        descricao: this.descricaoConteudo,
        tipos_ids,
      })
      .subscribe({
        next: () => {
          this.enviando.set(false);
          this.router.navigate(['/conteudo-educacional']);
        },
        error: (err) => {
          this.enviando.set(false);
          if (err?.status === 401) {
            this.erro.set('Você precisa estar logado para postar.');
          } else if (err?.status === 403) {
            this.erro.set('Apenas curadores podem postar conteúdo.');
          } else if (err?.error && typeof err.error === 'object') {
            this.erro.set(Object.values(err.error).flat().join(' '));
          } else {
            this.erro.set('Falha ao enviar conteúdo.');
          }
        },
      });
  }
}
