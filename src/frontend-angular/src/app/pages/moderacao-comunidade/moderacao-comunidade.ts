import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { Comunidade, ComunidadeService, DenunciaPostagem } from '../../services/comunidade.service';
import { IniciaisPipe, TomDaMarcaPipe } from '../../shared/marca';
import { TextoRicoPipe } from '../../shared/texto-rico/texto-rico';

@Component({
  selector: 'app-moderacao-comunidade',
  standalone: true,
  imports: [CommonModule, RouterLink, IniciaisPipe, TomDaMarcaPipe, TextoRicoPipe],
  templateUrl: './moderacao-comunidade.html',
  styleUrl: './moderacao-comunidade.css',
})
export class ModeracaoComunidadeComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private comunidadeService = inject(ComunidadeService);

  comunidade = signal<Comunidade | null>(null);
  denuncias = signal<DenunciaPostagem[]>([]);
  pendentesCount = signal(0);
  analisadasCount = signal(0);
  carregando = signal(false);
  acaoEmCurso = signal<number | null>(null);
  erro = signal<string | null>(null);
  sucesso = signal<string | null>(null);

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!Number.isFinite(id) || id <= 0) {
      this.router.navigate(['/comunidades']);
      return;
    }

    this.carregar(id);
  }

  carregar(id: number): void {
    this.carregando.set(true);
    this.erro.set(null);
    this.sucesso.set(null);

    this.comunidadeService.detalhe(id).subscribe({
      next: (comunidade) => {
        this.comunidade.set(comunidade);
        if (!comunidade.is_moderador) {
          this.carregando.set(false);
          this.erro.set('Apenas o moderador da comunidade pode analisar denúncias.');
          return;
        }
        this.carregarDenuncias(id);
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

  carregarDenuncias(id: number): void {
    this.comunidadeService.carregarModeracao(id).subscribe({
      next: (moderacao) => {
        this.denuncias.set(moderacao.pendentes);
        this.pendentesCount.set(moderacao.pendentes_count);
        this.analisadasCount.set(moderacao.analisadas_count);
        this.carregando.set(false);
      },
      error: (err) => {
        this.carregando.set(false);
        if (err?.status === 401) {
          this.router.navigate(['/login']);
        } else if (err?.status === 403) {
          this.erro.set(err?.error?.erro || 'Apenas o moderador da comunidade pode analisar denúncias.');
        } else {
          this.erro.set('Não foi possível carregar as denúncias pendentes.');
        }
      },
    });
  }

  removerPostagem(denuncia: DenunciaPostagem): void {
    this.analisar(denuncia, 'aprovar');
  }

  manterPostagem(denuncia: DenunciaPostagem): void {
    this.analisar(denuncia, 'reprovar');
  }

  private analisar(denuncia: DenunciaPostagem, acao: 'aprovar' | 'reprovar'): void {
    const comunidade = this.comunidade();
    if (!comunidade || this.acaoEmCurso()) return;

    this.acaoEmCurso.set(denuncia.id);
    this.erro.set(null);
    this.sucesso.set(null);

    const requisicao = acao === 'aprovar'
      ? this.comunidadeService.aprovarDenuncia(comunidade.id, denuncia.id)
      : this.comunidadeService.reprovarDenuncia(comunidade.id, denuncia.id);

    requisicao.subscribe({
      next: (resposta) => {
        this.denuncias.update((lista) => lista.filter((item) => item.id !== denuncia.id));
        this.pendentesCount.update((valor) => Math.max(valor - 1, 0));
        this.analisadasCount.update((valor) => valor + 1);
        this.sucesso.set(resposta.mensagem);
        this.acaoEmCurso.set(null);
      },
      error: (err) => {
        this.erro.set(err?.error?.erro || 'Não foi possível analisar a denúncia.');
        this.acaoEmCurso.set(null);
      },
    });
  }

  inicial(nome: string): string {
    return (nome || '?').trim().slice(0, 1).toUpperCase();
  }
}