import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { ComunidadeService, PostagemComunidade, Comunidade } from '../../services/comunidade.service';
import { IniciaisPipe, TomDaMarcaPipe } from '../../shared/marca';
import { TextoSimplesPipe } from '../../shared/texto-rico/texto-rico';

interface DiscussaoItem {
  postagem: PostagemComunidade;
  comunidade: Comunidade;
}

@Component({
  selector: 'app-discussoes',
  standalone: true,
  imports: [CommonModule, RouterLink, IniciaisPipe, TomDaMarcaPipe, TextoSimplesPipe],
  templateUrl: './discussoes.html',
})
export class DiscussoesComponent {
  private comunidades = inject(ComunidadeService);

  readonly carregando = signal(true);
  readonly erro = signal<string | null>(null);
  readonly itens = signal<DiscussaoItem[]>([]);

  constructor() {
    this.carregar();
  }

  carregar(): void {
    this.carregando.set(true);
    this.erro.set(null);

    this.comunidades.listar().subscribe({
      next: (comunidades) => {
        // Agregamos postagens das comunidades públicas mais ativas.
        // (Backend ainda não tem endpoint de feed global — versão interim.)
        const publicas = comunidades.slice(0, 8);

        Promise.all(
          publicas.map((c) =>
            firstValueFrom(this.comunidades.listarPostagens(c.id)).then((postagens) =>
              postagens.map((p) => ({ postagem: p, comunidade: c })),
            ).catch(() => [] as DiscussaoItem[]),
          ),
        ).then((listas) => {
          const todas = listas.flat();
          todas.sort((a, b) => (a.postagem.criado_em < b.postagem.criado_em ? 1 : -1));
          this.itens.set(todas.slice(0, 20));
          this.carregando.set(false);
        });
      },
      error: () => {
        this.erro.set('Não consegui carregar as discussões agora. Tente novamente em instantes.');
        this.carregando.set(false);
      },
    });
  }
}
