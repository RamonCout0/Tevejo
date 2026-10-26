import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';

import { AuthService, PerfilUsuario } from './auth.service';
import { GuiaService } from './guia.service';

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
  mostrar_convite_guia: true,
};

describe('GuiaService', () => {
  let guia: GuiaService;
  let auth: AuthService;
  let http: HttpTestingController;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({
      providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()],
    });
    guia = TestBed.inject(GuiaService);
    auth = TestBed.inject(AuthService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => localStorage.clear());

  it('mostra o convite só para quem ainda não respondeu e já aceitou o termo', () => {
    auth.perfil.set(perfilBase);
    expect(guia.mostrarConvite()).toBe(true);

    auth.perfil.set({ ...perfilBase, precisa_aceitar_termo: true });
    expect(guia.mostrarConvite()).toBe(false);

    auth.perfil.set({ ...perfilBase, mostrar_convite_guia: false });
    expect(guia.mostrarConvite()).toBe(false);
  });

  it('convivente vê os passos de criar comunidade; curador vê o de publicar conteúdo', () => {
    auth.perfil.set(perfilBase);
    const doConvivente = guia.passos().map((p) => p.id);
    expect(doConvivente).toContain('criar-nome');
    expect(doConvivente).not.toContain('publicar-conteudo');

    auth.perfil.set({ ...perfilBase, is_convivente: false, is_curador: true });
    const doCurador = guia.passos().map((p) => p.id);
    expect(doCurador).toContain('publicar-conteudo');
    expect(doCurador).not.toContain('criar-nome');
  });

  it('aceitar o convite registra a resposta e inicia o guia', () => {
    auth.perfil.set(perfilBase);

    guia.responderConvite(true);

    const req = http.expectOne('/api/usuarios/me/guia/');
    expect(req.request.method).toBe('POST');
    req.flush({ ...perfilBase, mostrar_convite_guia: false });
    expect(guia.ativo()).toBe(true);
    expect(guia.indice()).toBe(0);
    expect(guia.mostrarConvite()).toBe(false);
  });

  it('recusar o convite não inicia o guia e destaca o botão de ajuda', () => {
    auth.perfil.set(perfilBase);

    guia.responderConvite(false);
    http.expectOne('/api/usuarios/me/guia/').flush({});

    expect(guia.ativo()).toBe(false);
    expect(guia.destacarAjuda()).toBe(true);
    expect(guia.mostrarConvite()).toBe(false);
  });

  it('avança, volta e encerra no último passo', () => {
    auth.perfil.set(perfilBase);
    guia.iniciar();

    guia.anterior();
    expect(guia.indice()).toBe(0);

    guia.proximo();
    expect(guia.indice()).toBe(1);

    guia.indice.set(guia.passos().length - 1);
    expect(guia.ehUltimo()).toBe(true);
    guia.proximo();
    expect(guia.ativo()).toBe(false);
  });
});
