import { Component, computed, effect, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NavigationEnd, Router, RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { filter } from 'rxjs';

import { AuthService } from './core/auth.service';
import { GuiaService } from './core/guia.service';
import { ComunidadeService } from './services/comunidade.service';
import { BotaoAjudaComponent } from './shared/guia/botao-ajuda';
import { ConviteGuiaComponent } from './shared/guia/convite-guia';
import { GuiaTourComponent } from './shared/guia/guia-tour';
import { CorDaMarcaPipe, IniciaisPipe, TomDaMarcaPipe } from './shared/marca';

@Component({
  selector: 'app-root',
  standalone: true,
  templateUrl: './app.html',
  imports: [
    CommonModule, RouterOutlet, RouterLink, RouterLinkActive, CorDaMarcaPipe, IniciaisPipe, TomDaMarcaPipe,
    BotaoAjudaComponent, ConviteGuiaComponent, GuiaTourComponent,
  ],
})
export class AppComponent {
  title = 'TeVejo - Frontend';
  private auth = inject(AuthService);
  private router = inject(Router);
  private comunidades = inject(ComunidadeService);
  private guia = inject(GuiaService);
  readonly guiaAtivo = this.guia.ativo;

  readonly username = this.auth.username;
  readonly isConvivente = this.auth.isConvivente;
  readonly isCurador = this.auth.isCurador;
  readonly perfil = this.auth.perfil;
  readonly minhasComunidades = this.comunidades.minhas;

  /** Comunidades onde o usuário é moderador — controla visibilidade do item "Moderação" */
  readonly comunidadesModeradas = computed(() =>
    this.minhasComunidades().filter((c) => c.is_moderador),
  );

  readonly podeModerar = computed(() => this.comunidadesModeradas().length > 0);

  readonly drawerAberto = signal(false);

  /** Rotas onde NÃO mostramos o shell (header + sidebar) */
  private readonly rotasSemShell = ['/login', '/cadastro', '/termo-consentimento'];
  readonly mostrarShell = signal(true);

  constructor() {
    effect(() => {
      if (this.auth.token()) {
        this.comunidades.carregarMinhas().subscribe({ error: () => {} });
        if (!this.auth.perfil()) {
          this.auth.carregarPerfil().subscribe({ error: () => {} });
        }
      } else {
        this.comunidades.limparMinhas();
      }
    });

    // No celular o menu fica num drawer: o guia o abre quando o passo é sobre ele.
    effect(() => {
      const precisa = this.guia.precisaMenu();
      if (this.guia.ativo() && window.innerWidth < 1024) {
        this.drawerAberto.set(precisa);
      }
    });

    this.router.events
      .pipe(filter((e): e is NavigationEnd => e instanceof NavigationEnd))
      .subscribe((e) => {
        this.drawerAberto.set(this.guia.precisaMenu() && window.innerWidth < 1024);
        this.mostrarShell.set(
          !this.rotasSemShell.some((r) => e.urlAfterRedirects.startsWith(r)),
        );
        // A rolagem fica no <main>, não na janela: cada tela nova começa do topo.
        document.getElementById('main-content')?.scrollTo({ top: 0 });
      });
  }

  alternarDrawer(): void { this.drawerAberto.update((v) => !v); }
  fecharDrawer(): void { this.drawerAberto.set(false); }

  primeiroNome(nome: string | null | undefined): string {
    return (nome ?? '').trim().split(/\s+/)[0] ?? '';
  }

  logout(): void {
    this.guia.encerrar();
    this.auth.logout();
    this.comunidades.limparMinhas();
    this.router.navigate(['/login']);
  }
}
