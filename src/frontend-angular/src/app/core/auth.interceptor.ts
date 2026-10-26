import { HttpErrorResponse, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { inject } from '@angular/core';
import { Observable, catchError, finalize, shareReplay, switchMap, throwError } from 'rxjs';

import { AuthService } from './auth.service';

/** Endpoints públicos de autenticação — não devem receber Authorization (token velho geraria 401). */
const ROTAS_PUBLICAS = [
  '/usuarios/cadastro/',
  '/usuarios/login/',
  '/usuarios/login/google/',
  '/token/refresh/',
];

/** Renovação em andamento, compartilhada pelas requisições que tomarem 401 ao mesmo tempo. */
let renovacaoEmCurso$: Observable<string> | null = null;

function comToken(req: HttpRequest<unknown>, token: string): HttpRequest<unknown> {
  const prefixo = token.includes('.') ? 'Bearer' : 'Token';
  return req.clone({ setHeaders: { Authorization: `${prefixo} ${token}` } });
}

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const token = auth.token();
  const ehRotaPublica = ROTAS_PUBLICAS.some((rota) => req.url.includes(rota));
  if (!token || ehRotaPublica) {
    return next(req);
  }

  return next(comToken(req, token)).pipe(
    catchError((erro: unknown) => {
      if (!(erro instanceof HttpErrorResponse) || erro.status !== 401) {
        return throwError(() => erro);
      }

      // Access token vencido (dura 30 min): tenta renovar com o refresh token.
      // Se não der, encerra a sessão. Leituras são repetidas sem token, pois
      // páginas públicas (conteúdos, comunidades) funcionam para visitantes.
      const encerrarSessao = (erroFinal: unknown) => {
        auth.logout();
        return req.method === 'GET' ? next(req) : throwError(() => erroFinal);
      };

      if (!auth.temRefreshToken()) {
        return encerrarSessao(erro);
      }

      renovacaoEmCurso$ ??= auth.renovarToken().pipe(
        finalize(() => (renovacaoEmCurso$ = null)),
        shareReplay(1),
      );

      return renovacaoEmCurso$.pipe(
        catchError(() => {
          auth.logout();
          return throwError(() => erro);
        }),
        switchMap((novoToken) => next(comToken(req, novoToken))),
        catchError((erroRetentativa: unknown) =>
          erroRetentativa instanceof HttpErrorResponse && erroRetentativa.status === 401
            ? encerrarSessao(erroRetentativa)
            : throwError(() => erroRetentativa),
        ),
      );
    }),
  );
};
