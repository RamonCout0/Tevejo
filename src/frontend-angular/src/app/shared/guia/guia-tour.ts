import { Component, ElementRef, OnDestroy, computed, effect, inject, signal, viewChild } from '@angular/core';
import { CommonModule } from '@angular/common';

import { GuiaService } from '../../core/guia.service';

interface Caixa {
  top: number;
  left: number;
  width: number;
  height: number;
}

type Lado = 'direita' | 'esquerda' | 'abaixo' | 'acima' | 'centro';

const FOLGA = 8;          // espaço entre o alvo e a borda do destaque
const LARGURA_BALAO = 340;
const MARGEM_TELA = 16;
const RAIO = 16;          // cantos arredondados do destaque

/**
 * Sobreposição do guia condutor (CDU026): escurece a tela, recorta um
 * destaque em volta do elemento do passo atual e mostra o balão do Gui com
 * uma seta apontando para ele.
 */
@Component({
  selector: 'app-guia-tour',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './guia-tour.html',
  host: {
    '(document:keydown)': 'aoTeclar($event)',
    '(window:resize)': 'medir()',
  },
})
export class GuiaTourComponent implements OnDestroy {
  readonly guia = inject(GuiaService);

  private readonly balao = viewChild<ElementRef<HTMLElement>>('balao');

  /** Posição do elemento destacado (null = passo sem alvo, balão no centro). */
  readonly alvo = signal<Caixa | null>(null);
  readonly alturaBalao = signal(220);
  private relogio: ReturnType<typeof setInterval> | null = null;
  private tentativas = 0;
  private passoMedido: string | null = null;

  readonly destaque = computed(() => {
    const a = this.alvo();
    if (!a) return null;
    return {
      top: a.top - FOLGA,
      left: a.left - FOLGA,
      width: a.width + FOLGA * 2,
      height: a.height + FOLGA * 2,
    };
  });

  /** Caminho SVG: a tela inteira menos um retângulo arredondado em volta do alvo. */
  readonly mascara = computed(() => {
    this.alvo(); // recalcula quando o alvo (ou a janela, via medir) muda
    const w = window.innerWidth;
    const h = window.innerHeight;
    const tela = `M0 0H${w}V${h}H0Z`;
    const d = this.destaque();
    if (!d) return tela;
    const r = Math.min(RAIO, d.width / 2, d.height / 2);
    const { left: x, top: y, width: lw, height: lh } = d;
    const furo =
      `M${x + r} ${y}H${x + lw - r}A${r} ${r} 0 0 1 ${x + lw} ${y + r}` +
      `V${y + lh - r}A${r} ${r} 0 0 1 ${x + lw - r} ${y + lh}` +
      `H${x + r}A${r} ${r} 0 0 1 ${x} ${y + lh - r}` +
      `V${y + r}A${r} ${r} 0 0 1 ${x + r} ${y}Z`;
    return tela + furo;
  });

  /** Onde o balão fica em relação ao alvo, conforme o espaço disponível. */
  readonly lado = computed<Lado>(() => {
    const d = this.destaque();
    if (!d) return 'centro';
    const largura = window.innerWidth;
    const altura = window.innerHeight;
    if (largura < 640) {
      return d.top + d.height + this.alturaBalao() + 24 < altura ? 'abaixo' : 'acima';
    }
    if (d.left + d.width + LARGURA_BALAO + 32 < largura && d.width < largura / 2) return 'direita';
    if (d.top + d.height + this.alturaBalao() + 24 < altura) return 'abaixo';
    if (d.top - this.alturaBalao() - 24 > 0) return 'acima';
    if (d.left - LARGURA_BALAO - 32 > 0) return 'esquerda';
    // Alvo grande: fica do lado com mais espaço, encostado na borda da tela.
    return altura - (d.top + d.height) >= d.top ? 'abaixo' : 'acima';
  });

  readonly posicaoBalao = computed(() => {
    const d = this.destaque();
    const lado = this.lado();
    const largura = Math.min(LARGURA_BALAO, window.innerWidth - MARGEM_TELA * 2);
    const limitarX = (x: number) => Math.max(MARGEM_TELA, Math.min(x, window.innerWidth - largura - MARGEM_TELA));
    const limitarY = (y: number) => Math.max(MARGEM_TELA, Math.min(y, window.innerHeight - this.alturaBalao() - MARGEM_TELA));

    if (!d || lado === 'centro') {
      return { left: (window.innerWidth - largura) / 2, top: limitarY((window.innerHeight - this.alturaBalao()) / 2), width: largura };
    }
    switch (lado) {
      case 'direita':
        return { left: d.left + d.width + 20, top: limitarY(d.top + d.height / 2 - 40), width: largura };
      case 'esquerda':
        return { left: d.left - largura - 20, top: limitarY(d.top + d.height / 2 - 40), width: largura };
      case 'abaixo':
        return { left: limitarX(d.left + d.width / 2 - largura / 2), top: limitarY(d.top + d.height + 18), width: largura };
      default:
        return { left: limitarX(d.left + d.width / 2 - largura / 2), top: limitarY(d.top - this.alturaBalao() - 18), width: largura };
    }
  });

  /** Posição da seta: aponta para o centro do alvo, presa à borda do balão. */
  readonly posicaoSeta = computed(() => {
    const d = this.destaque();
    const b = this.posicaoBalao();
    const lado = this.lado();
    if (!d || lado === 'centro') return null;
    if (lado === 'direita' || lado === 'esquerda') {
      const y = Math.max(18, Math.min(d.top + d.height / 2 - b.top, this.alturaBalao() - 18));
      return { top: y, left: lado === 'direita' ? -7 : b.width - 7 };
    }
    const x = Math.max(18, Math.min(d.left + d.width / 2 - b.left, b.width - 18));
    return { left: x, top: lado === 'abaixo' ? -7 : this.alturaBalao() - 7 };
  });

  constructor() {
    // A cada passo, procura o alvo (a rota pode estar carregando) e acompanha
    // mudanças de layout enquanto o guia estiver aberto.
    effect(() => {
      const ativo = this.guia.ativo();
      const passo = this.guia.passoAtual();
      this.pararRelogio();
      if (!ativo || !passo) return;
      this.tentativas = 0;
      this.passoMedido = null;
      this.alvo.set(null);
      this.relogio = setInterval(() => this.medir(), 120);
      setTimeout(() => this.balao()?.nativeElement.focus(), 50);
    });
  }

  ngOnDestroy(): void {
    this.pararRelogio();
  }

  medir(): void {
    const passo = this.guia.passoAtual();
    if (!this.guia.ativo() || !passo) return;

    const balao = this.balao()?.nativeElement;
    if (balao) this.alturaBalao.set(balao.offsetHeight);

    if (!passo.alvo) {
      this.alvo.set(null);
      return;
    }

    const elemento = this.encontrarAlvo(passo.alvo);
    if (!elemento) {
      // Espera a tela carregar; se o alvo não existir, mostra o balão no centro.
      this.tentativas++;
      if (this.tentativas > 25) this.alvo.set(null);
      return;
    }

    if (this.passoMedido !== passo.id) {
      this.passoMedido = passo.id;
      // Alvo alto vai para o topo, sobrando espaço para o balão embaixo.
      const alto = elemento.getBoundingClientRect().height > window.innerHeight * 0.35;
      elemento.scrollIntoView({ block: alto ? 'start' : 'center', inline: 'nearest', behavior: 'smooth' });
    }
    const r = elemento.getBoundingClientRect();
    const atual = this.alvo();
    if (!atual || Math.abs(atual.top - r.top) > 0.5 || Math.abs(atual.left - r.left) > 0.5
      || Math.abs(atual.width - r.width) > 0.5 || Math.abs(atual.height - r.height) > 0.5) {
      this.alvo.set({ top: r.top, left: r.left, width: r.width, height: r.height });
    }
  }

  /** Mesmo `data-guia` pode existir no menu do computador e no do celular: usa o visível. */
  private encontrarAlvo(nome: string): HTMLElement | null {
    const candidatos = [...document.querySelectorAll<HTMLElement>(`[data-guia="${nome}"]`)];
    return candidatos.find((el) => {
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0 && r.right > 0 && r.left < window.innerWidth;
    }) ?? null;
  }

  aoTeclar(evento: KeyboardEvent): void {
    if (!this.guia.ativo()) return;
    if (evento.key === 'Escape') {
      evento.preventDefault();
      this.guia.encerrar();
    } else if (evento.key === 'ArrowRight') {
      evento.preventDefault();
      this.guia.proximo();
    } else if (evento.key === 'ArrowLeft') {
      evento.preventDefault();
      this.guia.anterior();
    }
  }

  private pararRelogio(): void {
    if (this.relogio) clearInterval(this.relogio);
    this.relogio = null;
  }
}
