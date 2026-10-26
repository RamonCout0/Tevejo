import { CommonModule } from '@angular/common';
import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { AuthService } from '../../core/auth.service';
import {
  ConteudoEducacional,
  ConteudoService,
  DenunciaPayload,
  MotivoDenuncia,
} from '../../services/conteudo.service';
import { LIMITES } from '../../shared/limites';
import { IniciaisPipe, TomDaMarcaPipe } from '../../shared/marca';
import { TextoRicoPipe } from '../../shared/texto-rico/texto-rico';

interface MotivoOpcao {
  valor: MotivoDenuncia;
  label: string;
}

@Component({
  selector: 'app-detalhe-conteudo',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, IniciaisPipe, TomDaMarcaPipe, TextoRicoPipe],
  templateUrl: './detalhe-conteudo.html',
  styleUrl: './detalhe-conteudo.css',
})
export class DetalheConteudoComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private auth = inject(AuthService);
  private conteudoService = inject(ConteudoService);

  conteudo = signal<ConteudoEducacional | null>(null);
  carregando = signal(true);
  erro = signal<string | null>(null);

  // Modal de denúncia
  modalAberto = signal(false);
  motivo: MotivoDenuncia = 'desatualizado';
  descricao = '';
  enviando = signal(false);
  erroModal = signal<string | null>(null);
  feedback = signal<string | null>(null);

  readonly motivos: MotivoOpcao[] = [
    { valor: 'desatualizado', label: 'Conteúdo desatualizado' },
    { valor: 'incorreto', label: 'Incorreto segundo novos estudos' },
    { valor: 'link_quebrado', label: 'Link quebrado' },
    { valor: 'outro', label: 'Outro' },
  ];

  readonly isConvivente = this.auth.isConvivente;
  readonly limites = LIMITES;

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!id) {
      this.erro.set('Conteúdo inválido.');
      this.carregando.set(false);
      return;
    }

    this.conteudoService.obterPorId(id).subscribe({
      next: (resposta) => {
        this.conteudo.set(resposta);
        this.carregando.set(false);
      },
      error: () => {
        this.erro.set('Não foi possível carregar o conteúdo.');
        this.carregando.set(false);
      },
    });
  }

  abrirModalDenuncia(): void {
    // Visitante → login (Fluxo Alt III do CDU022)
    if (!this.auth.isLoggedIn()) {
      this.router.navigate(['/login']);
      return;
    }
    this.motivo = 'desatualizado';
    this.descricao = '';
    this.erroModal.set(null);
    this.modalAberto.set(true);
  }

  fecharModal(): void {
    if (this.enviando()) return;
    this.modalAberto.set(false);
  }

  confirmarDenuncia(): void {
    const c = this.conteudo();
    if (!c || this.enviando()) return;

    const payload: DenunciaPayload = {
      motivo: this.motivo,
      descricao: this.descricao.trim(),
    };

    this.enviando.set(true);
    this.erroModal.set(null);

    this.conteudoService.denunciar(c.id, payload).subscribe({
      next: (denuncia) => {
        this.enviando.set(false);
        this.modalAberto.set(false);
        this.feedback.set('Denúncia registrada. Obrigado pela contribuição!');
        // atualiza o estado para mostrar o aviso de "já denunciou"
        this.conteudo.update((atual) =>
          atual
            ? {
                ...atual,
                minha_denuncia: {
                  id: denuncia.id,
                  motivo: denuncia.motivo,
                  motivo_display: denuncia.motivo_display,
                  status: denuncia.status,
                  criado_em: denuncia.criado_em,
                },
              }
            : atual,
        );
      },
      error: (err) => {
        this.enviando.set(false);
        if (err?.status === 401) {
          this.router.navigate(['/login']);
          return;
        }
        const msg = err?.error?.erro ?? err?.error?.detail;
        if (typeof msg === 'string') {
          this.erroModal.set(msg);
        } else if (Array.isArray(msg)) {
          this.erroModal.set(msg.join(' '));
        } else {
          this.erroModal.set('Não foi possível registrar a denúncia. Tente novamente.');
        }
      },
    });
  }

  limparFeedback(): void {
    this.feedback.set(null);
  }
}
