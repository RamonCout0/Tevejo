import { inject } from '@angular/core';
import { CanActivateFn, Router, UrlTree } from '@angular/router';
import { Observable, map, catchError, of } from 'rxjs';

import { ComunidadeService } from '../services/comunidade.service';

/**
 * Bloqueia rotas de criação de conteúdo (postar) para quem:
 *   - não é membro da comunidade
 *   - está banido
 *   - está com restrição ativa
 *
 * Em qualquer caso redireciona para a tela de detalhe da comunidade,
 * onde o usuário já vê o banner explicando o estado.
 */
export const podePostarGuard: CanActivateFn = (
  route,
): boolean | UrlTree | Observable<boolean | UrlTree> => {
  const router = inject(Router);
  const comunidades = inject(ComunidadeService);

  const idParam = route.paramMap.get('id');
  const id = Number(idParam);
  if (!Number.isFinite(id) || id <= 0) {
    return router.parseUrl('/comunidades');
  }

  const detalhe = router.parseUrl(`/comunidades/${id}`);

  return comunidades.detalhe(id).pipe(
    map((c) => {
      if (c.is_moderador) return true; // moderador pode postar sempre
      if (c.fui_banido) return detalhe;
      if (!c.is_membro) return detalhe;
      if (c.minha_restricao) return detalhe;
      return true;
    }),
    catchError(() => of(detalhe)),
  );
};
