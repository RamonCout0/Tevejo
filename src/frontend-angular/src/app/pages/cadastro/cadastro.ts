import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { AuthService } from '../../core/auth.service';
import { HeroMarcaComponent } from '../../shared/hero-marca/hero-marca';
import { LIMITES } from '../../shared/limites';


@Component({
  selector: 'app-cadastro',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, HeroMarcaComponent],
  templateUrl: './cadastro.html',
})
export class CadastroComponent {
  private auth = inject(AuthService);
  private router = inject(Router);

  nome = '';
  username = '';
  email = '';
  password = '';
  confirmacao = '';
  mostrarSenha = signal(false);
  mostrarConfirmacao = signal(false);
  readonly limites = LIMITES;

  enviando = signal(false);
  erro = signal<string | null>(null);

  /** Só acusa depois que a confirmação começou a ser digitada. */
  senhasDiferentes(): boolean {
    return this.confirmacao.length > 0 && this.confirmacao !== this.password;
  }

  voltar(): void {
    this.router.navigate(['/login']);
  }

  criarConta(): void {
    if (this.enviando()) return;
    this.erro.set(null);

    if (this.nome.trim().length < 3) {
      this.erro.set('O nome precisa ter pelo menos 3 caracteres.');
      return;
    }
    if (!this.email.includes('@')) {
      this.erro.set('Informe um e-mail válido.');
      return;
    }
    if (this.password.length < 8) {
      this.erro.set('A senha precisa ter pelo menos 8 caracteres.');
      return;
    }
    if (this.senhasDiferentes()) {
      this.erro.set('As senhas não coincidem.');
      return;
    }
    if (!this.username.trim()) {
      this.erro.set('Escolha um nome de usuário.');
      return;
    }

    this.enviando.set(true);

    this.auth.cadastrar({
      nome: this.nome,
      username: this.username,
      email: this.email,
      password: this.password,
      password_confirmacao: this.confirmacao,
    }).subscribe({
      next: () => {
        this.enviando.set(false);
        this.router.navigateByUrl(this.auth.rotaAposEntrar());
      },
      error: (err) => {
        this.enviando.set(false);
        if (err.error && typeof err.error === 'object') {
          const msgs = Object.values(err.error).flat();
          this.erro.set(msgs.join(' '));
        } else {
          this.erro.set('Não consegui criar sua conta agora. Confira os dados e tente novamente.');
        }
      },
    });
  }
}
