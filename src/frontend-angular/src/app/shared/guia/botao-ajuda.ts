import { Component, ElementRef, inject, signal, viewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';

import { AuthService } from '../../core/auth.service';
import { GuiaService } from '../../core/guia.service';

/** CDU027 - botão fixo de ajuda: refazer o guia ou abrir as perguntas frequentes. */
@Component({
  selector: 'app-botao-ajuda',
  standalone: true,
  imports: [CommonModule, RouterLink],
  host: { '(document:click)': 'aoClicarFora($event)', '(document:keydown.escape)': 'aberto.set(false)' },
  template: `
    <div #raiz class="fixed bottom-5 right-5 z-[60] flex flex-col items-end gap-3">

      <!-- Menu -->
      <div *ngIf="aberto()" id="menu-ajuda" class="tv-card tv-scale-in w-72 overflow-hidden" style="box-shadow: var(--tv-shadow-lg);"
           role="menu" aria-label="Ajuda">
        <div class="px-5 py-4 flex items-center gap-3" style="background: var(--tv-gradiente-suave);">
          <img src="/assets/personagens/gui.svg" alt="" class="w-8" aria-hidden="true">
          <div>
            <p class="font-semibold" style="font-family: var(--tv-font-display);">Precisa de ajuda?</p>
            <p class="text-xs" style="color: var(--color-tv-muted-fg);">O Gui está aqui pra isso.</p>
          </div>
        </div>
        <div class="p-2">
          <button *ngIf="logado()" type="button" role="menuitem" class="sidebar-item" (click)="iniciarGuia()">
            <span class="sidebar-icon" style="color: var(--color-tv-primary);"><i class="fas fa-route" aria-hidden="true"></i></span>
            <span class="min-w-0">
              <span class="block font-semibold">Fazer o guia</span>
              <span class="block text-xs font-normal" style="color: var(--color-tv-muted-fg);">Passo a passo pelo site</span>
            </span>
          </button>
          <a routerLink="/ajuda" role="menuitem" class="sidebar-item" (click)="aberto.set(false)">
            <span class="sidebar-icon" style="color: #22A6BF;"><i class="fas fa-circle-question" aria-hidden="true"></i></span>
            <span class="min-w-0">
              <span class="block font-semibold">Dúvidas frequentes</span>
              <span class="block text-xs font-normal" style="color: var(--color-tv-muted-fg);">Respostas com ilustrações</span>
            </span>
          </a>
        </div>
      </div>

      <!-- Aviso depois de recusar o convite -->
      <div *ngIf="guia.destacarAjuda() && !aberto()" class="tv-card tv-scale-in px-4 py-3 text-sm max-w-[16rem]" role="status"
           style="box-shadow: var(--tv-shadow-lg);">
        Tudo bem! Quando quiser, é só tocar aqui. 👇
      </div>

      <button type="button" data-guia="botao-ajuda" class="tv-ajuda-botao" [class.tv-ajuda-pulso]="guia.destacarAjuda()"
              (click)="aberto.set(!aberto())" [attr.aria-expanded]="aberto()" aria-controls="menu-ajuda"
              aria-label="Ajuda: guia e dúvidas frequentes" title="Ajuda">
        <img *ngIf="!aberto()" src="/assets/personagens/gui.svg" alt="" class="w-7" aria-hidden="true">
        <i *ngIf="aberto()" class="fas fa-times text-lg" style="color: var(--color-tv-primary-ink);" aria-hidden="true"></i>
      </button>
    </div>
  `,
})
export class BotaoAjudaComponent {
  readonly guia = inject(GuiaService);
  private auth = inject(AuthService);
  private router = inject(Router);

  private readonly raiz = viewChild.required<ElementRef<HTMLElement>>('raiz');
  readonly aberto = signal(false);

  logado(): boolean {
    return this.auth.isLoggedIn();
  }

  iniciarGuia(): void {
    this.aberto.set(false);
    this.guia.iniciar();
  }

  aoClicarFora(evento: MouseEvent): void {
    if (this.aberto() && !this.raiz().nativeElement.contains(evento.target as Node)) {
      this.aberto.set(false);
    }
  }
}
