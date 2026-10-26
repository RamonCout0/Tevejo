import { Component, input } from '@angular/core';
import { RouterLink } from '@angular/router';

/** Painel lateral com a marca (login, cadastro): logo, padrão e os pilares do TeVejo. */
@Component({
  selector: 'app-hero-marca',
  standalone: true,
  imports: [RouterLink],
  template: `
    <div class="relative h-full flex flex-col justify-between overflow-hidden px-12 py-10 tv-padrao"
         style="background-color: var(--color-tv-creme);">
      <div class="tv-faixa-marca absolute inset-x-0 top-0"></div>

      <!-- Brilho suave nas cores da marca -->
      <div class="absolute -top-32 -right-32 w-96 h-96 rounded-full blur-3xl opacity-40"
           style="background: radial-gradient(circle, #5EE0CD, transparent 70%);" aria-hidden="true"></div>
      <div class="absolute -bottom-40 -left-24 w-[28rem] h-[28rem] rounded-full blur-3xl opacity-30"
           style="background: radial-gradient(circle, #635AE0, transparent 70%);" aria-hidden="true"></div>

      <a routerLink="/" aria-label="TeVejo, página inicial" class="relative inline-flex">
        <img src="/assets/logo.svg" alt="TeVejo" class="h-16 w-auto">
      </a>

      <div class="relative space-y-6">
        <p class="tv-page-eyebrow" style="color: var(--color-tv-primary-ink);">{{ eyebrow() }}</p>
        <h1 class="leading-[1.1]" style="font-family: var(--tv-font-display); font-weight: 600; font-size: 2.6rem; color: var(--color-tv-tinta);">
          {{ titulo() }}
          <span class="tv-texto-gradiente">{{ destaque() }}</span>
        </h1>
        <p class="text-lg leading-relaxed max-w-[34ch]" style="color: var(--color-tv-muted-fg);">
          Para famílias, cuidadores, educadores e pessoas autistas: informação, conexão e acolhimento.
        </p>
      </div>

      <ul class="relative grid gap-3">
        <li class="flex items-center gap-3 p-3 rounded-2xl" style="background: rgba(255,255,255,0.75); backdrop-filter: blur(6px);">
          <span class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 tv-tom-0"><i class="fas fa-book-open" aria-hidden="true"></i></span>
          <span class="text-sm"><strong>Informar</strong> com conteúdos confiáveis sobre o TEA</span>
        </li>
        <li class="flex items-center gap-3 p-3 rounded-2xl" style="background: rgba(255,255,255,0.75); backdrop-filter: blur(6px);">
          <span class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 tv-tom-2"><i class="fas fa-hand-holding-heart" aria-hidden="true"></i></span>
          <span class="text-sm"><strong>Conscientizar</strong> e reduzir preconceitos com empatia</span>
        </li>
        <li class="flex items-center gap-3 p-3 rounded-2xl" style="background: rgba(255,255,255,0.75); backdrop-filter: blur(6px);">
          <span class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 tv-tom-5"><i class="fas fa-users" aria-hidden="true"></i></span>
          <span class="text-sm"><strong>Apoiar</strong> com um espaço seguro para trocar experiências</span>
        </li>
      </ul>
    </div>
  `,
})
export class HeroMarcaComponent {
  readonly eyebrow = input('Plataforma TEA');
  readonly titulo = input('Um lugar onde cada pessoa');
  readonly destaque = input('é vista.');
}
