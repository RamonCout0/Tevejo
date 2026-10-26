import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

import { ComunidadeService, Encontro } from '../../services/comunidade.service';
import { CorDaMarcaPipe, TomDaMarcaPipe } from '../../shared/marca';
import { TextoRicoPipe } from '../../shared/texto-rico/texto-rico';

/** CDU005 - Visualizar Encontros Públicos. */
@Component({
  selector: 'app-encontros',
  standalone: true,
  imports: [CommonModule, RouterLink, CorDaMarcaPipe, TomDaMarcaPipe, TextoRicoPipe],
  templateUrl: './encontros.html',
})
export class EncontrosComponent {
  private comunidades = inject(ComunidadeService);

  readonly encontros = signal<Encontro[]>([]);
  readonly carregando = signal(true);
  readonly erro = signal<string | null>(null);
  readonly apenasMinhas = signal(false);
  readonly selecionadoId = signal<number | null>(null);

  constructor() {
    this.carregar();
  }

  carregar(): void {
    this.carregando.set(true);
    this.erro.set(null);
    this.comunidades.listarEncontrosPublicos(this.apenasMinhas()).subscribe({
      next: (lista) => {
        this.encontros.set(lista);
        this.carregando.set(false);
      },
      error: () => {
        // Fluxo Alternativo II
        this.erro.set('Não foi possível carregar as informações do encontro. Tente novamente mais tarde.');
        this.carregando.set(false);
      },
    });
  }

  filtrar(apenasMinhas: boolean): void {
    if (this.apenasMinhas() === apenasMinhas) return;
    this.apenasMinhas.set(apenasMinhas);
    this.selecionadoId.set(null);
    this.carregar();
  }

  alternarDetalhes(id: number): void {
    this.selecionadoId.update((atual) => (atual === id ? null : id));
  }

  tagsDe(encontro: Encontro): string[] {
    return (encontro.tags ?? '').split(',').map((t) => t.trim()).filter(Boolean);
  }
}
