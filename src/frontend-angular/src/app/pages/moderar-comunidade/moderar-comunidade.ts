import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import {
  AcaoModeracao,
  AplicarAcaoPayload,
  Comunidade,
  ComunidadeService,
  MembroComunidade,
  TipoAcaoModeracao,
} from '../../services/comunidade.service';
import { LIMITES } from '../../shared/limites';
import { IniciaisPipe, TomDaMarcaPipe } from '../../shared/marca';

interface ModalState {
  membro: MembroComunidade;
  tipo: TipoAcaoModeracao;
}

interface HistoricoState {
  carregando: boolean;
  acoes: AcaoModeracao[] | null;
  erro: string | null;
}

@Component({
  selector: 'app-moderar-comunidade',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, IniciaisPipe, TomDaMarcaPipe],
  templateUrl: './moderar-comunidade.html',
})
export class ModerarComunidadeComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private comunidadeService = inject(ComunidadeService);

  comunidade = signal<Comunidade | null>(null);
  membros = signal<MembroComunidade[]>([]);
  carregando = signal(false);
  erro = signal<string | null>(null);
  feedback = signal<string | null>(null);

  modal = signal<ModalState | null>(null);
  justificativa = '';
  readonly limites = LIMITES;
  duracaoDias = 7;
  aplicando = signal(false);
  erroModal = signal<string | null>(null);

  /** Histórico carregado por membro (id → estado). */
  historicos = signal<Record<number, HistoricoState>>({});

  private comunidadeId = 0;

  /** Membros conviventes (exclui o próprio moderador). */
  readonly membrosVisiveis = computed(() =>
    this.membros().filter((m) => !m.is_moderador),
  );

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!Number.isFinite(id) || id <= 0) {
      this.router.navigate(['/comunidades']);
      return;
    }
    this.comunidadeId = id;
    this.carregarComunidade();
    this.carregarMembros();
  }

  carregarComunidade(): void {
    this.comunidadeService.detalhe(this.comunidadeId).subscribe({
      next: (c) => {
        this.comunidade.set(c);
        if (!c.is_moderador) {
          this.router.navigate(['/comunidades', this.comunidadeId]);
        }
      },
      error: () => this.erro.set('Não foi possível carregar a comunidade.'),
    });
  }

  carregarMembros(): void {
    this.carregando.set(true);
    this.comunidadeService.listarMembros(this.comunidadeId).subscribe({
      next: (lista) => {
        this.membros.set(lista);
        this.carregando.set(false);
      },
      error: (err) => {
        this.carregando.set(false);
        if (err?.status === 403) {
          this.router.navigate(['/comunidades', this.comunidadeId]);
        } else {
          this.erro.set('Não foi possível carregar os membros.');
        }
      },
    });
  }

  abrirModal(membro: MembroComunidade, tipo: TipoAcaoModeracao): void {
    this.justificativa = '';
    this.duracaoDias = 7;
    this.erroModal.set(null);
    this.modal.set({ membro, tipo });
  }

  fecharModal(): void {
    if (this.aplicando()) return;
    this.modal.set(null);
  }

  confirmar(): void {
    const state = this.modal();
    if (!state || this.aplicando()) return;

    const payload: AplicarAcaoPayload = {
      convivente_id: state.membro.id,
      tipo: state.tipo,
      justificativa: this.justificativa.trim(),
    };
    if (state.tipo === 'restringir') {
      payload.duracao_dias = this.duracaoDias;
    }

    // Validações locais antes de enviar
    if (state.tipo === 'banir' && !payload.justificativa) {
      this.erroModal.set('Justificativa é obrigatória para banimento.');
      return;
    }
    if (state.tipo === 'restringir' && (!payload.duracao_dias || payload.duracao_dias <= 0 || payload.duracao_dias > 365)) {
      this.erroModal.set('Informe uma duração entre 1 e 365 dias.');
      return;
    }

    this.aplicando.set(true);
    this.erroModal.set(null);
    this.comunidadeService.moderar(this.comunidadeId, payload).subscribe({
      next: (acao) => {
        this.aplicando.set(false);
        const alvoId = state.membro.id;
        this.modal.set(null);
        this.feedback.set(
          `${acao.tipo_display} aplicado(a) em ${acao.convivente}.`,
        );
        // invalida histórico em cache do membro afetado
        this.historicos.update((map) => {
          const { [alvoId]: _, ...rest } = map;
          return rest;
        });
        this.carregarMembros();
      },
      error: (err) => {
        this.aplicando.set(false);
        const msg = err?.error?.erro;
        if (typeof msg === 'string') {
          this.erroModal.set(msg);
        } else if (Array.isArray(msg)) {
          this.erroModal.set(msg.join(' '));
        } else {
          this.erroModal.set('Não foi possível concluir a moderação. Tente novamente.');
        }
      },
    });
  }

  limparFeedback(): void {
    this.feedback.set(null);
  }

  /** Abre/fecha o histórico de um membro. Carrega sob demanda na primeira abertura. */
  toggleHistorico(membro: MembroComunidade): void {
    const atual = this.historicos()[membro.id];
    if (atual) {
      // já aberto → fechar removendo do map
      this.historicos.update((map) => {
        const { [membro.id]: _, ...rest } = map;
        return rest;
      });
      return;
    }
    this.historicos.update((map) => ({
      ...map,
      [membro.id]: { carregando: true, acoes: null, erro: null },
    }));
    this.comunidadeService.historicoConvivente(this.comunidadeId, membro.id).subscribe({
      next: (acoes) => {
        this.historicos.update((map) => ({
          ...map,
          [membro.id]: { carregando: false, acoes, erro: null },
        }));
      },
      error: () => {
        this.historicos.update((map) => ({
          ...map,
          [membro.id]: { carregando: false, acoes: null, erro: 'Não foi possível carregar o histórico.' },
        }));
      },
    });
  }

  historicoDe(id: number): HistoricoState | null {
    return this.historicos()[id] ?? null;
  }
}
