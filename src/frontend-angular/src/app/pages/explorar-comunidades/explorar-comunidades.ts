import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { AuthService } from '../../core/auth.service';
import { Comunidade, ComunidadeService } from '../../services/comunidade.service';
import { CATEGORIAS, categoriaDoFiltro } from '../../shared/categorias';
import { IniciaisPipe, TomDaMarcaPipe } from '../../shared/marca';

@Component({
  selector: 'app-explorar-comunidades',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, IniciaisPipe, TomDaMarcaPipe],
  templateUrl: './explorar-comunidades.html',
})
export class ExplorarComunidadesComponent implements OnInit {
  private comunidadeService = inject(ComunidadeService);
  private auth = inject(AuthService);
  private router = inject(Router);

  comunidades = signal<Comunidade[]>([]);
  carregando = signal(false);
  erro = signal<string | null>(null);
  acaoEmId = signal<number | null>(null);

  readonly autenticado = computed(() => this.auth.isLoggedIn());
  readonly isConvivente = this.auth.isConvivente;
  /** Mostra o botão Participar: visitantes (caem em /login) e Conviventes. */
  readonly podeVerParticipar = computed(
    () => !this.autenticado() || this.isConvivente(),
  );

  filtro = '';
  private filtroSignal = signal('');
  /** Categoria escolhida nos chips (null = todas). */
  readonly categoria = signal<string | null>(null);

  /**
   * Chips de filtro: as categorias fixas que têm pelo menos uma comunidade,
   * na ordem da lista. Categorias antigas (texto livre) contam como "Outros".
   */
  readonly categorias = computed(() => {
    const contagem = new Map<string, number>();
    for (const c of this.comunidades()) {
      const cat = categoriaDoFiltro(c.categoria);
      contagem.set(cat, (contagem.get(cat) ?? 0) + 1);
    }
    return CATEGORIAS.filter((cat) => contagem.has(cat.nome)).map((cat) => ({
      ...cat,
      total: contagem.get(cat.nome)!,
    }));
  });

  readonly comunidadesFiltradas = computed(() => {
    const termo = this.filtroSignal().trim().toLowerCase();
    const categoria = this.categoria();
    const lista = categoria
      ? this.comunidades().filter((c) => categoriaDoFiltro(c.categoria) === categoria)
      : this.comunidades();
    if (!termo) return lista;
    return lista.filter(
      (c) =>
        c.nome.toLowerCase().includes(termo) ||
        c.categoria.toLowerCase().includes(termo) ||
        c.descricao.toLowerCase().includes(termo),
    );
  });

  ngOnInit(): void {
    this.carregar();
  }

  onFiltroChange(valor: string): void {
    this.filtroSignal.set(valor ?? '');
  }

  carregar(): void {
    this.carregando.set(true);
    this.erro.set(null);
    this.comunidadeService.listar().subscribe({
      next: (lista) => {
        this.comunidades.set(lista);
        this.carregando.set(false);
      },
      error: () => {
        this.erro.set('Não foi possível carregar as comunidades.');
        this.carregando.set(false);
      },
    });
  }

  participar(c: Comunidade, event: Event): void {
    event.stopPropagation();
    if (!this.auth.isLoggedIn()) {
      this.router.navigate(['/login']);
      return;
    }
    if (this.acaoEmId() !== null) return;
    this.acaoEmId.set(c.id);
    this.comunidadeService.participar(c.id).subscribe({
      next: (atualizada) => {
        this.comunidades.update((lista) =>
          lista.map((item) => (item.id === atualizada.id ? atualizada : item)),
        );
        this.acaoEmId.set(null);
      },
      error: (err) => {
        this.acaoEmId.set(null);
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
}
