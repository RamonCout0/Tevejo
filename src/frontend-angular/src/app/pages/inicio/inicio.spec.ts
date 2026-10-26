import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';

import { AuthService, PerfilUsuario } from '../../core/auth.service';
import { InicioComponent } from './inicio';

const perfilConvivente: PerfilUsuario = {
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

describe('InicioComponent (CDU028)', () => {
  let auth: AuthService;

  const renderizar = () => {
    const fixture = TestBed.createComponent(InicioComponent);
    fixture.detectChanges();
    return fixture.nativeElement as HTMLElement;
  };

  const rotasDosCartoes = (el: HTMLElement) =>
    Array.from(el.querySelectorAll('ul a')).map((a) => a.getAttribute('href'));

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({
      imports: [InicioComponent],
      providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()],
    });
    auth = TestBed.inject(AuthService);
  });

  afterEach(() => localStorage.clear());

  it('dá boas-vindas ao visitante e oferece criar conta e entrar', () => {
    const el = renderizar();

    expect(el.textContent).toContain('Bem-vindo(a), visitante!');
    expect(el.textContent).toContain('O que você está procurando?');
    expect(el.querySelector('a[href="/login"]')).not.toBeNull();
    expect(el.querySelector('a[href="/cadastro"]')).not.toBeNull();
  });

  it('mostra os caminhos da plataforma e o convite para fazer parte', () => {
    const rotas = rotasDosCartoes(renderizar());

    expect(rotas).toEqual([
      '/conteudo-educacional', '/comunidades', '/discussoes', '/encontros', '/ajuda', '/cadastro',
    ]);
  });

  it('avisa o visitante que os encontros pedem login', () => {
    expect(renderizar().textContent).toContain('Entre para ver');
  });

  it('cumprimenta o convivente pelo primeiro nome e oferece criar comunidade', () => {
    auth.username.set('ana');
    auth.perfil.set(perfilConvivente);
    const el = renderizar();

    expect(el.textContent).toContain('Olá, Ana!');
    expect(el.textContent).not.toContain('visitante');
    expect(el.querySelector('section a[href="/login"]')).toBeNull();
    expect(rotasDosCartoes(el)).toContain('/criar-comunidade');
    expect(rotasDosCartoes(el)).not.toContain('/cadastro');
  });

  it('não oferece criar comunidade para o curador', () => {
    auth.username.set('carla');
    auth.perfil.set({ ...perfilConvivente, username: 'carla', nome: 'Carla', is_convivente: false, is_curador: true });

    const rotas = rotasDosCartoes(renderizar());
    expect(rotas).not.toContain('/criar-comunidade');
    expect(rotas).not.toContain('/cadastro');
  });
});
