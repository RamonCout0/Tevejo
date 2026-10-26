import { TestBed } from '@angular/core/testing';
import { HttpClient, provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';

import { authInterceptor } from './auth.interceptor';
import { AuthService } from './auth.service';

describe('authInterceptor', () => {
  let http: HttpClient;
  let controle: HttpTestingController;
  let auth: AuthService;

  beforeEach(() => {
    localStorage.clear();
    localStorage.setItem('tevejo_token', 'access.velho.jwt');
    localStorage.setItem('tevejo_refresh', 'refresh.valido.jwt');

    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([authInterceptor])),
        provideHttpClientTesting(),
      ],
    });
    http = TestBed.inject(HttpClient);
    controle = TestBed.inject(HttpTestingController);
    auth = TestBed.inject(AuthService);
  });

  afterEach(() => {
    controle.verify();
    localStorage.clear();
  });

  it('envia o access token como Bearer', () => {
    http.get('/api/comunidades/').subscribe();

    const req = controle.expectOne('/api/comunidades/');
    expect(req.request.headers.get('Authorization')).toBe('Bearer access.velho.jwt');
    req.flush([]);
  });

  it('não envia token para as rotas de login', () => {
    http.post('/api/usuarios/login/', {}).subscribe();

    const req = controle.expectOne('/api/usuarios/login/');
    expect(req.request.headers.has('Authorization')).toBe(false);
    req.flush({});
  });

  it('renova o token após 401 e repete a requisição', () => {
    let resposta: unknown;
    http.get('/api/comunidades/minhas/').subscribe((r) => (resposta = r));

    controle.expectOne('/api/comunidades/minhas/').flush(null, { status: 401, statusText: 'Unauthorized' });

    const refresh = controle.expectOne('/api/token/refresh/');
    expect(refresh.request.body).toEqual({ refresh: 'refresh.valido.jwt' });
    refresh.flush({ access: 'access.novo.jwt' });

    const repetida = controle.expectOne('/api/comunidades/minhas/');
    expect(repetida.request.headers.get('Authorization')).toBe('Bearer access.novo.jwt');
    repetida.flush(['ok']);

    expect(resposta).toEqual(['ok']);
    expect(auth.token()).toBe('access.novo.jwt');
  });

  it('com refresh vencido encerra a sessão e repete leituras sem token', () => {
    let resposta: unknown;
    http.get('/api/conteudos/conteudo-educacional/').subscribe((r) => (resposta = r));

    controle.expectOne('/api/conteudos/conteudo-educacional/')
      .flush(null, { status: 401, statusText: 'Unauthorized' });
    controle.expectOne('/api/token/refresh/').flush(null, { status: 401, statusText: 'Unauthorized' });

    const anonima = controle.expectOne('/api/conteudos/conteudo-educacional/');
    expect(anonima.request.headers.has('Authorization')).toBe(false);
    anonima.flush([]);

    expect(resposta).toEqual([]);
    expect(auth.isLoggedIn()).toBe(false);
  });
});
