import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';


import { AuthService } from '../../core/auth.service';
import { ConteudoEducacional, ConteudoService } from '../../services/conteudo.service';
import { Tag, TagsService } from '../../services/tags.service';
import { CorDaMarcaPipe, IniciaisPipe, TomDaMarcaPipe } from '../../shared/marca';
import { TextoSimplesPipe } from '../../shared/texto-rico/texto-rico';

@Component({
  selector: 'app-conteudo-educacional',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, CorDaMarcaPipe, IniciaisPipe, TomDaMarcaPipe, TextoSimplesPipe],
  templateUrl: './conteudo-educacional.html',
  styleUrl: './conteudo-educacional.css',
  
})
export class ConteudoEducacionalComponent implements OnInit {
  private conteudoService = inject(ConteudoService);
  private tagsService = inject(TagsService);
  private auth = inject(AuthService);

  readonly isCurador = this.auth.isCurador;

  conteudos = signal<ConteudoEducacional[]>([]);
  tags = signal<Tag[]>([]);
  tagSelecionada = signal<number | null>(null);
  busca = signal('');
  carregando = signal(false);
  erro = signal<string | null>(null);

  ngOnInit(): void {
    this.carregar();
    this.tagsService.listar().subscribe({
      next: (tags) => this.tags.set(tags),
      error: () => this.tags.set([]),
    });
  }

  carregar(): void {
    this.carregando.set(true);
    this.erro.set(null);
    this.conteudoService.listar().subscribe({
      next: (lista) => {
        this.conteudos.set(lista);
        this.carregando.set(false);
      },
      error: (err) => {
        this.erro.set(
          err?.status === 401
            ? 'Sessão expirada. Faça login novamente.'
            : 'Não foi possível carregar os conteúdos.'
        );
        this.carregando.set(false);
      },
    });
  }

  filtrar(tagId: number | null): void {
    this.tagSelecionada.set(tagId);
  }

  get conteudosFiltrados(): ConteudoEducacional[] {
    const tagId = this.tagSelecionada();
    const termo = this.busca().trim().toLowerCase();
    return this.conteudos().filter((c) => {
      if (tagId !== null && !c.tipos.some((t) => t.id === tagId)) return false;
      if (!termo) return true;
      return [c.titulo, c.fonte, c.descricao, c.curador?.nome ?? '', ...c.tipos.map((t) => t.nome)]
        .some((campo) => campo.toLowerCase().includes(termo));
    });
  }
}
