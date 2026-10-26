import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter } from '@angular/router';

import { ConteudoEducacionalComponent } from './conteudo-educacional';

describe('ConteudoEducacionalComponent', () => {
  let component: ConteudoEducacionalComponent;
  let fixture: ComponentFixture<ConteudoEducacionalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ConteudoEducacionalComponent],
      providers: [
        provideRouter([]),
        provideHttpClient(),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ConteudoEducacionalComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
