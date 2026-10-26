import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter } from '@angular/router';

import { CriarComunidade } from './criar-comunidade';

describe('CriarComunidade', () => {
  let component: CriarComunidade;
  let fixture: ComponentFixture<CriarComunidade>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CriarComunidade],
      providers: [
        provideRouter([]),
        provideHttpClient(),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(CriarComunidade);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
