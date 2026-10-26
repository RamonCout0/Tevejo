import { inject } from '@angular/core';
import { CanActivateFn, Router, UrlTree } from '@angular/router';
import { Observable, map, catchError, of } from 'rxjs';

import { AuthService, PerfilUsuario } from './auth.service';

/**
 * Resolve o perfil do usuário (carregando se necessário) e devolve o resultado
 * do predicado aplicado sobre o perfil.
 *
 * Também aplica o CDU019: convivente que ainda não aceitou o termo vigente é
 * levado para a tela do termo antes de acessar qualquer tela interna.
 */
function checarPapel(
  predicado: (perfil: PerfilUsuario) => boolean,
  redirectTo: string,
  exigeLogin = true,
): CanActivateFn {
  return (): boolean | UrlTree | Observable<boolean | UrlTree> => {
    const auth = inject(AuthService);
    const router = inject(Router);

    if (!auth.isLoggedIn()) {
      return exigeLogin ? router.parseUrl('/login') : true;
    }

    const decidir = (p: PerfilUsuario): boolean | UrlTree => {
      if (p.precisa_aceitar_termo) return router.parseUrl('/termo-consentimento');
      return predicado(p) ? true : router.parseUrl(redirectTo);
    };

    const perfilAtual = auth.perfil();
    if (perfilAtual) {
      return decidir(perfilAtual);
    }

    return auth.carregarPerfil().pipe(
      map(decidir),
      // Sessão inválida (ex.: refresh vencido): o interceptor já fez logout.
      catchError(() => of(exigeLogin ? router.parseUrl('/login') : true)),
    );
  };
}

/** Rotas públicas: visitantes passam; usuário logado precisa ter aceitado o termo. */
export const termoAceitoGuard: CanActivateFn = checarPapel(() => true, '/', false);

export const authGuard: CanActivateFn = checarPapel(() => true, '/login');

export const conviventeGuard: CanActivateFn = checarPapel(
  (p) => p.is_convivente,
  '/comunidades',
);

export const curadorGuard: CanActivateFn = checarPapel(
  (p) => p.is_curador,
  '/conteudo-educacional',
);

/** A tela do termo só faz sentido para quem está logado e ainda precisa aceitar. */
export const termoPendenteGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  if (!auth.isLoggedIn()) return router.parseUrl('/login');

  const decidir = (p: PerfilUsuario) =>
    p.precisa_aceitar_termo ? true : router.parseUrl('/conteudo-educacional');

  const perfilAtual = auth.perfil();
  if (perfilAtual) return decidir(perfilAtual);
  return auth.carregarPerfil().pipe(
    map(decidir),
    catchError(() => of(router.parseUrl('/login'))),
  );
};
