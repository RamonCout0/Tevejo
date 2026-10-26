import {
  Component,
  ElementRef,
  OnDestroy,
  afterNextRender,
  computed,
  forwardRef,
  input,
  signal,
  viewChild,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import { Editor } from '@tiptap/core';
import Highlight from '@tiptap/extension-highlight';
import { Placeholder } from '@tiptap/extensions';
import StarterKit from '@tiptap/starter-kit';

import { textoRicoParaHtml } from '../texto-rico/texto-rico';
import { jsonParaMarcacao } from './marcacao';

type Formato = 'bold' | 'italic' | 'underline' | 'highlight' | 'strike' | 'bulletList' | 'orderedList' | 'blockquote' | 'link';

const URL_PERMITIDA = /^(https?:\/\/|\/(?!\/))/i;

/**
 * Editor de texto visual ("o que você vê é o que sai"): negrito, itálico,
 * sublinhado, grifado, riscado, listas, citação e link aparecem formatados
 * enquanto a pessoa digita, sem símbolos.
 *
 * Por dentro o valor continua sendo a marcação de texto rico do TeVejo
 * (ver `marcacao.ts` e o pipe `textoRico`), então o backend e os textos já
 * publicados não mudam. Funciona com [(ngModel)] e com formControlName.
 */
@Component({
  selector: 'app-editor-texto',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './editor-texto.html',
  providers: [{ provide: NG_VALUE_ACCESSOR, useExisting: forwardRef(() => EditorTextoComponent), multi: true }],
})
export class EditorTextoComponent implements ControlValueAccessor, OnDestroy {
  readonly limite = input(2000);
  readonly linhas = input(6);
  readonly placeholder = input('');
  readonly idCampo = input<string | null>(null);
  readonly rotulo = input('Texto');
  /** Versão enxuta (comentários): só os botões mais usados. */
  readonly compacto = input(false);

  private readonly area = viewChild.required<ElementRef<HTMLDivElement>>('area');

  readonly valor = signal('');
  readonly desabilitado = signal(false);
  /** Formatações ativas onde o cursor está (deixa o botão "aceso"). */
  readonly ativos = signal<Partial<Record<Formato, boolean>>>({});
  readonly avisoLimite = signal(false);

  readonly usados = computed(() => this.valor().length);
  readonly classeContador = computed(() => {
    const proporcao = this.usados() / this.limite();
    if (proporcao >= 1) return 'tv-contador tv-contador-limite';
    if (proporcao >= 0.9) return 'tv-contador tv-contador-alerta';
    return 'tv-contador';
  });

  private editor: Editor | null = null;
  /** Último valor emitido: evita recarregar o editor (e perder o cursor) com o próprio eco do ngModel. */
  private ultimoEmitido: string | null = null;
  private valorPendente = '';

  private aoMudar: (valor: string) => void = () => {};
  private aoTocar: () => void = () => {};

  constructor() {
    afterNextRender(() => this.criarEditor());
  }

  ngOnDestroy(): void {
    this.editor?.destroy();
  }

  private criarEditor(): void {
    this.editor = new Editor({
      element: this.area().nativeElement,
      editable: !this.desabilitado(),
      content: textoRicoParaHtml(this.valorPendente),
      extensions: [
        StarterKit.configure({
          heading: false,
          code: false,
          codeBlock: false,
          horizontalRule: false,
          link: {
            openOnClick: false,
            autolink: true,
            defaultProtocol: 'https',
            isAllowedUri: (url) => URL_PERMITIDA.test(url),
            HTMLAttributes: { rel: 'noopener noreferrer', target: '_blank' },
          },
        }),
        Highlight,
        Placeholder.configure({ placeholder: () => this.placeholder() }),
      ],
      editorProps: {
        attributes: {
          class: 'tv-texto-rico tv-editor-area',
          role: 'textbox',
          'aria-multiline': 'true',
          'aria-label': this.rotulo(),
          ...(this.idCampo() ? { id: this.idCampo()! } : {}),
          style: `min-height: ${this.linhas() * 26}px`,
        },
      },
      onUpdate: ({ editor }) => this.aoEditar(editor),
      onSelectionUpdate: ({ editor }) => this.atualizarAtivos(editor),
      onTransaction: ({ editor }) => this.atualizarAtivos(editor),
      onBlur: () => this.aoTocar(),
    });
    this.valor.set(this.valorPendente);
  }

  private aoEditar(editor: Editor): void {
    const marcacao = jsonParaMarcacao(editor.getJSON());
    if (marcacao.length > this.limite()) {
      // Passou do limite (ex.: colou um texto enorme): desfaz a última ação.
      this.avisoLimite.set(true);
      editor.commands.undo();
      return;
    }
    this.avisoLimite.set(false);
    this.valor.set(marcacao);
    this.ultimoEmitido = marcacao;
    this.aoMudar(marcacao);
  }

  private atualizarAtivos(editor: Editor): void {
    const formatos: Formato[] = ['bold', 'italic', 'underline', 'highlight', 'strike', 'bulletList', 'orderedList', 'blockquote', 'link'];
    this.ativos.set(Object.fromEntries(formatos.map((f) => [f, editor.isActive(f)])));
  }

  // ----- ControlValueAccessor -----

  writeValue(valor: string | null): void {
    const texto = valor ?? '';
    if (texto === this.ultimoEmitido) return;
    this.valorPendente = texto;
    this.valor.set(texto);
    this.ultimoEmitido = texto;
    this.editor?.commands.setContent(textoRicoParaHtml(texto), { emitUpdate: false });
  }

  registerOnChange(fn: (valor: string) => void): void {
    this.aoMudar = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.aoTocar = fn;
  }

  setDisabledState(desabilitado: boolean): void {
    this.desabilitado.set(desabilitado);
    this.editor?.setEditable(!desabilitado);
  }

  // ----- Barra de formatação -----

  aplicar(formato: Formato): void {
    const cadeia = this.editor?.chain().focus();
    if (!cadeia) return;
    const comandos: Record<Exclude<Formato, 'link'>, () => unknown> = {
      bold: () => cadeia.toggleBold().run(),
      italic: () => cadeia.toggleItalic().run(),
      underline: () => cadeia.toggleUnderline().run(),
      highlight: () => cadeia.toggleHighlight().run(),
      strike: () => cadeia.toggleStrike().run(),
      bulletList: () => cadeia.toggleBulletList().run(),
      orderedList: () => cadeia.toggleOrderedList().run(),
      blockquote: () => cadeia.toggleBlockquote().run(),
    };
    if (formato === 'link') {
      this.alternarLink();
    } else {
      comandos[formato]();
    }
  }

  private alternarLink(): void {
    const editor = this.editor;
    if (!editor) return;
    if (editor.isActive('link')) {
      editor.chain().focus().extendMarkRange('link').unsetLink().run();
      return;
    }
    const resposta = prompt('Endereço do link (ex.: https://www.gov.br/saude):');
    const url = resposta?.trim();
    if (!url) return;
    const final = URL_PERMITIDA.test(url) ? url : `https://${url}`;
    const { empty } = editor.state.selection;
    if (empty) {
      editor.chain().focus().insertContent({ type: 'text', text: final, marks: [{ type: 'link', attrs: { href: final } }] }).run();
    } else {
      editor.chain().focus().extendMarkRange('link').setLink({ href: final }).run();
    }
  }

  focar(): void {
    this.editor?.commands.focus();
  }
}
