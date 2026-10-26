import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';

import { GuiaService } from '../../core/guia.service';

/** CDU026 - convite do guia condutor, mostrado no primeiro acesso. */
@Component({
  selector: 'app-convite-guia',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div *ngIf="guia.mostrarConvite()" class="fixed inset-0 z-[95] flex items-end sm:items-center justify-center p-4 tv-fade-in"
         style="background: rgba(18,18,20,0.5);" role="dialog" aria-modal="true" aria-labelledby="convite-guia-titulo">
      <div class="w-full max-w-md tv-card tv-card-marca tv-scale-in overflow-hidden" style="box-shadow: var(--tv-shadow-lg);">
        <div class="relative px-7 pt-9 pb-4 text-center" style="background: var(--tv-gradiente-suave);">
          <img src="/assets/personagens/gui.svg" alt="Gui, o guia do TeVejo" class="w-16 mx-auto tv-guia-mascote">
          <img src="/assets/girassol.svg" alt="" aria-hidden="true" class="absolute right-5 top-6 w-10 rotate-12 opacity-90">
        </div>
        <div class="p-7 pt-5 space-y-4 text-center">
          <h2 id="convite-guia-titulo" class="tv-page-title" style="font-size: 1.5rem;">Quer que eu te mostre o site?</h2>
          <p class="tv-page-subtitle">
            Eu sou o <strong>Gui</strong>. Em menos de um minuto te mostro para que serve cada parte do TeVejo
            e como criar ou participar de uma comunidade.
          </p>
          <div class="flex flex-col gap-2 pt-2">
            <button type="button" class="tv-btn tv-btn-primary tv-btn-lg w-full" (click)="guia.responderConvite(true)">
              <i class="fas fa-route" aria-hidden="true"></i> Sim, me mostra!
            </button>
            <button type="button" class="tv-btn tv-btn-ghost w-full" (click)="guia.responderConvite(false)">
              Agora não
            </button>
          </div>
          <p class="text-xs" style="color: var(--color-tv-muted-fg);">
            Você pode me chamar depois pelo botão de ajuda, no canto inferior direito.
          </p>
        </div>
      </div>
    </div>
  `,
})
export class ConviteGuiaComponent {
  readonly guia = inject(GuiaService);
}
