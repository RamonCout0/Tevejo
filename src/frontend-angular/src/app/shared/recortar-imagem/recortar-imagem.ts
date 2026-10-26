import {
  Component,
  ElementRef,
  OnDestroy,
  afterNextRender,
  computed,
  input,
  output,
  signal,
  viewChild,
} from '@angular/core';
import { CommonModule } from '@angular/common';

const ZOOM_MIN = 1;
const ZOOM_MAX = 4;
const PASSO_TECLADO = 10;

/**
 * Modal para recortar uma imagem antes do upload: arrastar posiciona, o
 * controle de zoom (ou a roda do mouse) redimensiona. Devolve um File já no
 * tamanho e proporção usados na tela (foto de perfil, ícone, banner).
 */
@Component({
  selector: 'app-recortar-imagem',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './recortar-imagem.html',
  host: { '(document:keydown.escape)': 'cancelar()' },
})
export class RecortarImagemComponent implements OnDestroy {
  /** Imagem escolhida pelo usuário. */
  readonly arquivo = input.required<File>();
  /** Largura ÷ altura da área de recorte (1 = quadrado, 4 = banner). */
  readonly proporcao = input(1);
  /** Máscara circular (foto de perfil e ícone). */
  readonly redondo = input(false);
  /** Largura em px da imagem gerada (nunca amplia além do original). */
  readonly larguraSaida = input(512);
  readonly titulo = input('Ajustar imagem');

  readonly recortado = output<File>();
  readonly cancelado = output<void>();

  private readonly area = viewChild.required<ElementRef<HTMLDivElement>>('area');

  readonly url = computed(() => URL.createObjectURL(this.arquivo()));
  readonly carregada = signal(false);
  readonly erro = signal<string | null>(null);
  readonly zoom = signal(ZOOM_MIN);
  readonly zoomMin = ZOOM_MIN;
  readonly zoomMax = ZOOM_MAX;

  // Posição do canto superior esquerdo da imagem dentro da área (px de tela).
  readonly x = signal(0);
  readonly y = signal(0);

  private imagem: HTMLImageElement | null = null;
  private larguraArea = 0;
  private alturaArea = 0;
  private arraste: { px: number; py: number; x: number; y: number } | null = null;
  private observador: ResizeObserver | null = null;

  /** Escala que faz a imagem cobrir a área com zoom 1. */
  private readonly escalaBase = signal(1);
  private readonly larguraNatural = signal(0);
  private readonly alturaNatural = signal(0);

  readonly escala = computed(() => this.escalaBase() * this.zoom());
  readonly largura = computed(() => this.larguraNatural() * this.escala());
  readonly altura = computed(() => this.alturaNatural() * this.escala());

  constructor() {
    afterNextRender(() => {
      this.observador = new ResizeObserver(() => this.medirArea(true));
      this.observador.observe(this.area().nativeElement);
    });
  }

  ngOnDestroy(): void {
    this.observador?.disconnect();
    URL.revokeObjectURL(this.url());
  }

  aoCarregar(evento: Event): void {
    this.imagem = evento.target as HTMLImageElement;
    this.larguraNatural.set(this.imagem.naturalWidth);
    this.alturaNatural.set(this.imagem.naturalHeight);
    this.medirArea(false);
    this.carregada.set(true);
  }

  aoFalhar(): void {
    this.erro.set('Não foi possível abrir esta imagem. Tente outro arquivo.');
  }

  // ----- Arrastar -----

  iniciarArraste(evento: PointerEvent): void {
    if (!this.carregada()) return;
    (evento.currentTarget as HTMLElement).setPointerCapture(evento.pointerId);
    this.arraste = { px: evento.clientX, py: evento.clientY, x: this.x(), y: this.y() };
  }

  arrastar(evento: PointerEvent): void {
    if (!this.arraste) return;
    this.posicionar(
      this.arraste.x + evento.clientX - this.arraste.px,
      this.arraste.y + evento.clientY - this.arraste.py,
    );
  }

  finalizarArraste(): void {
    this.arraste = null;
  }

  // ----- Zoom -----

  aoMudarZoom(evento: Event): void {
    this.aplicarZoom(Number((evento.target as HTMLInputElement).value));
  }

  aoRolar(evento: WheelEvent): void {
    if (!this.carregada()) return;
    evento.preventDefault();
    this.aplicarZoom(this.zoom() * (evento.deltaY < 0 ? 1.08 : 1 / 1.08));
  }

  aoTeclar(evento: KeyboardEvent): void {
    const movimentos: Record<string, [number, number]> = {
      ArrowLeft: [PASSO_TECLADO, 0],
      ArrowRight: [-PASSO_TECLADO, 0],
      ArrowUp: [0, PASSO_TECLADO],
      ArrowDown: [0, -PASSO_TECLADO],
    };
    const mov = movimentos[evento.key];
    if (mov) {
      evento.preventDefault();
      this.posicionar(this.x() + mov[0], this.y() + mov[1]);
    } else if (evento.key === '+' || evento.key === '=') {
      this.aplicarZoom(this.zoom() + 0.1);
    } else if (evento.key === '-') {
      this.aplicarZoom(this.zoom() - 0.1);
    }
  }

  /** Muda o zoom mantendo fixo o ponto da imagem que está no centro da área. */
  private aplicarZoom(novo: number): void {
    const zoom = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, novo));
    const escalaAntes = this.escala();
    const centroX = (this.larguraArea / 2 - this.x()) / escalaAntes;
    const centroY = (this.alturaArea / 2 - this.y()) / escalaAntes;
    this.zoom.set(zoom);
    const escala = this.escala();
    this.posicionar(this.larguraArea / 2 - centroX * escala, this.alturaArea / 2 - centroY * escala);
  }

  /** Garante que a imagem sempre cubra toda a área de recorte. */
  private posicionar(x: number, y: number): void {
    this.x.set(Math.min(0, Math.max(this.larguraArea - this.largura(), x)));
    this.y.set(Math.min(0, Math.max(this.alturaArea - this.altura(), y)));
  }

  private medirArea(manterCentro: boolean): void {
    const img = this.imagem;
    const caixa = this.area().nativeElement.getBoundingClientRect();
    if (!img || !caixa.width || !caixa.height) return;

    const escalaAntes = this.escala();
    const centroX = (this.larguraArea / 2 - this.x()) / escalaAntes;
    const centroY = (this.alturaArea / 2 - this.y()) / escalaAntes;

    this.larguraArea = caixa.width;
    this.alturaArea = caixa.height;
    this.escalaBase.set(Math.max(caixa.width / img.naturalWidth, caixa.height / img.naturalHeight));

    const escala = this.escala();
    if (manterCentro && this.carregada()) {
      this.posicionar(caixa.width / 2 - centroX * escala, caixa.height / 2 - centroY * escala);
    } else {
      // Começa centralizada.
      this.posicionar(
        (caixa.width - img.naturalWidth * escala) / 2,
        (caixa.height - img.naturalHeight * escala) / 2,
      );
    }
  }

  // ----- Resultado -----

  confirmar(): void {
    const img = this.imagem;
    if (!img) return;

    const escala = this.escala();
    const sx = -this.x() / escala;
    const sy = -this.y() / escala;
    const sw = this.larguraArea / escala;
    const sh = this.alturaArea / escala;

    const larguraFinal = Math.round(Math.min(this.larguraSaida(), sw));
    const alturaFinal = Math.round(larguraFinal / this.proporcao());

    const canvas = document.createElement('canvas');
    canvas.width = larguraFinal;
    canvas.height = alturaFinal;
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      this.erro.set('Seu navegador não conseguiu recortar a imagem.');
      return;
    }
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(img, sx, sy, sw, sh, 0, 0, larguraFinal, alturaFinal);

    // PNG preserva transparência; o resto vira JPEG (arquivo menor).
    const tipo = this.arquivo().type === 'image/png' ? 'image/png' : 'image/jpeg';
    const extensao = tipo === 'image/png' ? 'png' : 'jpg';
    const nomeBase = this.arquivo().name.replace(/\.[^.]+$/, '') || 'imagem';

    canvas.toBlob(
      (blob) => {
        if (!blob) {
          this.erro.set('Não foi possível gerar a imagem recortada.');
          return;
        }
        this.recortado.emit(new File([blob], `${nomeBase}.${extensao}`, { type: tipo }));
      },
      tipo,
      0.9,
    );
  }

  cancelar(): void {
    this.cancelado.emit();
  }
}
