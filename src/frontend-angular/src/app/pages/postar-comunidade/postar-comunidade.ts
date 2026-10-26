import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import { Comunidade, ComunidadeService } from '../../services/comunidade.service';
import { EditorTextoComponent } from '../../shared/editor-texto/editor-texto';
import { LIMITES } from '../../shared/limites';
import { IniciaisPipe, TomDaMarcaPipe } from '../../shared/marca';

@Component({
  selector: 'app-postar-comunidade',
  standalone: true,
  imports: [CommonModule, FormsModule, EditorTextoComponent, IniciaisPipe, TomDaMarcaPipe],
  templateUrl: './postar-comunidade.html',
  styleUrl: './postar-comunidade.css',
})
export class PostarComunidadeComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private comunidadeService = inject(ComunidadeService);

  comunidade = signal<Comunidade | null>(null);
  carregando = signal(false);
  enviando = signal(false);
  erro = signal<string | null>(null);

  titulo = '';
  conteudo = '';
  readonly limites = LIMITES;

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!Number.isFinite(id) || id <= 0) {
      this.router.navigate(['/comunidades']);
      return;
    }
    this.carregarComunidade(id);
  }

  carregarComunidade(id: number): void {
    this.carregando.set(true);
    this.erro.set(null);
    this.comunidadeService.detalhe(id).subscribe({
      next: (comunidade) => {
        this.comunidade.set(comunidade);
        this.carregando.set(false);
        if (!comunidade.is_membro && !comunidade.is_moderador) {
          this.erro.set('Você precisa participar da comunidade para publicar conteúdos');
        }
      },
      error: (err) => {
        this.carregando.set(false);
        if (err?.status === 401) {
          this.router.navigate(['/login']);
        } else if (err?.status === 404) {
          this.erro.set('Comunidade não encontrada.');
        } else {
          this.erro.set('Não foi possível carregar a comunidade.');
        }
      },
    });
  }

  cancelar(): void {
    const comunidade = this.comunidade();
    this.router.navigate(['/comunidades', comunidade?.id ?? '']);
  }

  postar(): void {
    const comunidade = this.comunidade();
    if (!comunidade || this.enviando()) return;

    this.erro.set(null);
    if (!this.titulo.trim()) {
      this.erro.set('Dê um título para a sua postagem.');
      return;
    }
    if (!this.conteudo.trim()) {
      this.erro.set('O conteúdo da postagem não pode estar vazio.');
      return;
    }

    this.enviando.set(true);
    this.comunidadeService.criarPostagem(comunidade.id, {
      titulo: this.titulo,
      conteudo: this.conteudo,
    }).subscribe({
      next: () => {
        this.enviando.set(false);
        this.router.navigate(['/comunidades', comunidade.id]);
      },
      error: (err) => {
        this.enviando.set(false);
        if (err?.status === 401) {
          this.router.navigate(['/login']);
        } else if (err?.status === 403) {
          this.erro.set(err?.error?.erro || 'Você precisa participar da comunidade para publicar conteúdos');
        } else if (err?.error?.conteudo) {
          this.erro.set(err.error.conteudo.join(' '));
        } else if (err?.error?.titulo) {
          this.erro.set(err.error.titulo.join(' '));
        } else {
          this.erro.set('Não foi possível publicar a postagem.');
        }
      },
    });
  }
}