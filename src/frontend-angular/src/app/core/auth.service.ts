import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Observable, map, tap } from 'rxjs';

import { environment } from '../../environments/environment';

const TOKEN_KEY = 'tevejo_token';
const REFRESH_KEY = 'tevejo_refresh';
const USER_KEY = 'tevejo_user';

export interface PerfilUsuario {
  id: number;
  username: string;
  email: string;
  nome: string;
  biografia: string | null;
  foto: string | null;
  is_convivente: boolean;
  is_curador: boolean;
  /** CDU019: convivente ainda não aceitou a versão vigente do termo. */
  precisa_aceitar_termo: boolean;
  /** CDU026: ainda não respondeu ao convite do guia condutor. */
  mostrar_convite_guia: boolean;
}

/** Resposta de login, login com Google e cadastro. */
export interface SessaoResponse {
  access: string;
  refresh: string;
  usuario: PerfilUsuario;
}

export type LoginResponse = SessaoResponse;
export type CadastroResponse = SessaoResponse;

export interface CadastroPayload {
  nome: string;
  username: string;
  email: string;
  password: string;
  password_confirmacao: string;
}

function lerStorage(chave: string): string | null {
  try {
    return localStorage.getItem(chave);
  } catch {
    return null;
  }
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private base = environment.apiUrl;

  readonly token = signal<string | null>(lerStorage(TOKEN_KEY));
  readonly username = signal<string | null>(lerStorage(USER_KEY));
  readonly perfil = signal<PerfilUsuario | null>(null);

  readonly isConvivente = computed(() => this.perfil()?.is_convivente ?? false);
  readonly isCurador = computed(() => this.perfil()?.is_curador ?? false);

  login(identificador: string, password: string): Observable<LoginResponse> {
    // O campo da tela aceita usuário OU e-mail. O backend espera a chave certa:
    // procura por `email` quando há '@', senão por `username`.
    const credenciais = identificador.includes('@')
      ? { email: identificador, password }
      : { username: identificador, password };
    return this.http
      .post<LoginResponse>(`${this.base}/usuarios/login/`, credenciais)
      .pipe(tap((res) => this.iniciarSessao(res)));
  }

  loginGoogle(idToken: string): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${this.base}/usuarios/login/google/`, { id_token: idToken })
      .pipe(tap((res) => this.iniciarSessao(res)));
  }

  cadastrar(dados: CadastroPayload): Observable<CadastroResponse> {
    return this.http
      .post<CadastroResponse>(`${this.base}/usuarios/cadastro/`, dados)
      .pipe(tap((res) => this.iniciarSessao(res)));
  }

  carregarPerfil(): Observable<PerfilUsuario> {
    return this.http
      .get<PerfilUsuario>(`${this.base}/usuarios/me/`)
      .pipe(tap((p) => this.perfil.set(p)));
  }

  atualizarPerfil(payload: FormData): Observable<PerfilUsuario> {
    return this.http
      .patch<PerfilUsuario>(`${this.base}/usuarios/me/`, payload)
      .pipe(
        tap((p) => {
          this.perfil.set(p);
          this.username.set(p.username);
          localStorage.setItem(USER_KEY, p.username);
        }),
      );
  }

  /** CDU019: registra o aceite da versão vigente do termo. */
  aceitarTermo(): Observable<PerfilUsuario> {
    return this.http
      .post<PerfilUsuario>(`${this.base}/usuarios/me/aceitar-termo/`, {})
      .pipe(tap((p) => this.perfil.set(p)));
  }

  /** Destino após entrar: o termo, se ainda não foi aceito; senão a tela pedida. */
  rotaAposEntrar(padrao = '/conteudo-educacional'): string {
    return this.perfil()?.precisa_aceitar_termo ? '/termo-consentimento' : padrao;
  }

  /**
   * Troca o refresh token por um novo access token (o access dura 30 min).
   * Usado pelo interceptor quando uma requisição volta 401.
   */
  renovarToken(): Observable<string> {
    const refresh = lerStorage(REFRESH_KEY);
    return this.http
      .post<{ access: string }>(`${this.base}/token/refresh/`, { refresh })
      .pipe(
        map((res) => res.access),
        tap((access) => {
          localStorage.setItem(TOKEN_KEY, access);
          this.token.set(access);
        }),
      );
  }

  temRefreshToken(): boolean {
    return !!lerStorage(REFRESH_KEY);
  }

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
    this.token.set(null);
    this.username.set(null);
    this.perfil.set(null);
  }

  isLoggedIn(): boolean {
    return !!this.token();
  }

  private iniciarSessao(res: SessaoResponse): void {
    localStorage.setItem(TOKEN_KEY, res.access);
    localStorage.setItem(REFRESH_KEY, res.refresh);
    localStorage.setItem(USER_KEY, res.usuario.username);
    this.token.set(res.access);
    this.username.set(res.usuario.username);
    this.perfil.set(res.usuario);
  }
}
