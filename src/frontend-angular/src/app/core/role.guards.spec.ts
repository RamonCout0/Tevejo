import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { ActivatedRouteSnapshot, RouterStateSnapshot, UrlTree, provideRouter } from '@angular/router';

import { AuthService, PerfilUsuario } from './auth.service';
import { conviventeGuard, termoAceitoGuard } from './role.guards';

const perfilBase: PerfilUsuario = {
  id: 1,
  username: 'ana',
  email: 'ana@tevejo.com',
  nome: 'Ana Lima',
  biografia: null,
  foto: null,
  is_convivente: true,
  is_curador: false,
  precisa_aceitar_termo: false,
  mostrar_convite_guia: false,
};

describe('role guards', () => {
  let auth: AuthService;

  const executar = (guard: typeof conviventeGuard) =>
    TestBed.runInInjectionContext(() =>
      guard({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot),
    );

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({
      providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()],
    });
    auth = TestBed.inject(AuthService);
  });

  afterEach(() => localStorage.clear());

  it('visitante acessa rotas públicas', () => {
    expect(executar(termoAceitoGuard)).toBe(true);
  });

  it('visitante é mandado ao login em rota de convivente', () => {
    const resultado = executar(conviventeGuard) as UrlTree;
    expect(resultado.toString()).toBe('/login');
  });

  it('convivente sem aceite do termo vai para o termo', () => {
    auth.token.set('access.jwt');
    auth.perfil.set({ ...perfilBase, precisa_aceitar_termo: true });

    expect((executar(termoAceitoGuard) as UrlTree).toString()).toBe('/termo-consentimento');
    expect((executar(conviventeGuard) as UrlTree).toString()).toBe('/termo-consentimento');
  });

  it('convivente com termo aceito passa', () => {
    auth.token.set('access.jwt');
    auth.perfil.set(perfilBase);

    expect(executar(conviventeGuard)).toBe(true);
  });

  it('curador não acessa rota de convivente', () => {
    auth.token.set('access.jwt');
    auth.perfil.set({ ...perfilBase, is_convivente: false, is_curador: true });

    expect((executar(conviventeGuard) as UrlTree).toString()).toBe('/comunidades');
  });
});
