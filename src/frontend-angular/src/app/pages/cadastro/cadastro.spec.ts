import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';

import { CadastroComponent } from './cadastro';

describe('CadastroComponent (CDU002)', () => {
  let component: CadastroComponent;
  let http: HttpTestingController;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({
      imports: [CadastroComponent],
      providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()],
    });
    component = TestBed.createComponent(CadastroComponent).componentInstance;
    http = TestBed.inject(HttpTestingController);

    component.nome = 'Maria Silva';
    component.username = 'maria';
    component.email = 'maria@tevejo.com';
    component.password = 'SenhaForte@123';
  });

  afterEach(() => localStorage.clear());

  it('só acusa senhas diferentes depois que a confirmação começa a ser digitada', () => {
    expect(component.senhasDiferentes()).toBe(false);
    component.confirmacao = 'Senha';
    expect(component.senhasDiferentes()).toBe(true);
    component.confirmacao = 'SenhaForte@123';
    expect(component.senhasDiferentes()).toBe(false);
  });

  it('mostra a senha e a confirmação de forma independente', () => {
    component.mostrarConfirmacao.set(true);

    expect(component.mostrarConfirmacao()).toBe(true);
    expect(component.mostrarSenha()).toBe(false);
  });

  it('não envia o cadastro quando as senhas não coincidem', () => {
    component.confirmacao = 'SenhaForte@124';
    component.criarConta();

    expect(component.erro()).toBe('As senhas não coincidem.');
    http.expectNone((req) => req.url.endsWith('/usuarios/cadastro/'));
  });

  it('envia a confirmação junto com a senha', () => {
    component.confirmacao = 'SenhaForte@123';
    component.criarConta();

    const req = http.expectOne((r) => r.url.endsWith('/usuarios/cadastro/'));
    expect(req.request.body.password_confirmacao).toBe('SenhaForte@123');
  });
});
