import { AfterViewInit, Component, ElementRef, inject, signal, viewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { environment } from '../../../environments/environment';
import { AuthService } from '../../core/auth.service';
import { HeroMarcaComponent } from '../../shared/hero-marca/hero-marca';


declare const google: any;

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, HeroMarcaComponent],
  templateUrl: './login.html',
})
export class LoginComponent implements AfterViewInit {
  private auth = inject(AuthService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  private googleButton = viewChild<ElementRef<HTMLElement>>('googleButton');

  username = '';
  password = '';
  mostrarSenha = signal(false);
  enviando = signal(false);
  erro = signal<string | null>(
    // CDU019 - Fluxo Alternativo I: voltou para cá por recusar o termo.
    this.route.snapshot.queryParamMap.get('termo') === 'recusado'
      ? 'O aceite é obrigatório para utilizar a plataforma TeVejo.'
      : null,
  );

  ngAfterViewInit(): void {
    const botao = this.googleButton()?.nativeElement;
    if (!botao || typeof google === 'undefined') return;

    google.accounts.id.initialize({
      client_id: environment.googleClientId,
      callback: (resposta: { credential: string }) => this.onGoogleCredential(resposta.credential),
    });
    google.accounts.id.renderButton(botao, { theme: 'outline', size: 'large', width: 320 });
  }

  onGoogleCredential(idToken: string): void {
    if (this.enviando()) return;
    this.erro.set(null);
    this.enviando.set(true);

    this.auth.loginGoogle(idToken).subscribe({
      next: () => {
        this.enviando.set(false);
        this.router.navigateByUrl(this.auth.rotaAposEntrar());
      },
      error: () => {
        this.enviando.set(false);
        this.erro.set('Não foi possível entrar com o Google.');
      },
    });
  }

  onSubmit(): void {
    if (this.enviando()) return;
    this.erro.set(null);
    this.enviando.set(true);

    this.auth.login(this.username, this.password).subscribe({
      next: () => {
        this.enviando.set(false);
        this.router.navigateByUrl(this.auth.rotaAposEntrar());
      },
      error: () => {
        this.enviando.set(false);
        this.erro.set('Usuário ou senha inválidos.');
      },
    });
  }
}
