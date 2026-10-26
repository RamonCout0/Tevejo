import { Component, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';

import { AuthService } from '../../core/auth.service';

/** CDU019 - Termo de Consentimento e Responsabilidade. */
@Component({
  selector: 'app-termo-consentimento',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './termo-consentimento.component.html',
})
export class TermoConsentimentoComponent {
  private auth = inject(AuthService);
  private router = inject(Router);

  enviando = signal(false);
  erro = signal<string | null>(null);

  aoConcordar(): void {
    if (this.enviando()) return;
    this.erro.set(null);
    this.enviando.set(true);

    this.auth.aceitarTermo().subscribe({
      next: () => {
        this.enviando.set(false);
        this.router.navigate(['/conteudo-educacional']);
      },
      error: () => {
        // Fluxo Alternativo II
        this.enviando.set(false);
        this.erro.set('Não foi possível registrar sua aceitação. Tente novamente.');
      },
    });
  }

  aoRecusar(): void {
    // Fluxo Alternativo I: sem aceite não há acesso às telas internas.
    this.auth.logout();
    this.router.navigate(['/login'], { queryParams: { termo: 'recusado' } });
  }
}
