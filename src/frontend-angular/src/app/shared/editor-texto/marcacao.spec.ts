import { Editor } from '@tiptap/core';
import Highlight from '@tiptap/extension-highlight';
import StarterKit from '@tiptap/starter-kit';

import { textoRicoParaHtml } from '../texto-rico/texto-rico';
import { jsonParaMarcacao } from './marcacao';

/** Carrega a marcação no editor real e converte de volta. */
function idaEVolta(marcacao: string): string {
  const editor = new Editor({
    element: document.createElement('div'),
    extensions: [StarterKit.configure({ heading: false, code: false, codeBlock: false, horizontalRule: false }), Highlight],
    content: textoRicoParaHtml(marcacao),
  });
  const resultado = jsonParaMarcacao(editor.getJSON());
  editor.destroy();
  return resultado;
}

describe('marcação do editor visual', () => {
  it('converte as formatações de texto', () => {
    const doc = {
      type: 'doc',
      content: [{
        type: 'paragraph',
        content: [
          { type: 'text', text: 'a', marks: [{ type: 'bold' }] },
          { type: 'text', text: ' ' },
          { type: 'text', text: 'b', marks: [{ type: 'italic' }] },
          { type: 'text', text: ' ' },
          { type: 'text', text: 'c', marks: [{ type: 'underline' }] },
          { type: 'text', text: ' ' },
          { type: 'text', text: 'd', marks: [{ type: 'highlight' }] },
          { type: 'text', text: ' ' },
          { type: 'text', text: 'e', marks: [{ type: 'strike' }] },
        ],
      }],
    };
    expect(jsonParaMarcacao(doc)).toBe('**a** _b_ __c__ ==d== ~~e~~');
  });

  it('deixa espaços das pontas fora da marca', () => {
    const doc = { type: 'doc', content: [{ type: 'paragraph', content: [
      { type: 'text', text: 'Olá ' },
      { type: 'text', text: 'mundo ', marks: [{ type: 'bold' }] },
      { type: 'text', text: 'feliz' },
    ] }] };
    expect(jsonParaMarcacao(doc)).toBe('Olá **mundo** feliz');
  });

  it('converte links com texto e links soltos', () => {
    const doc = { type: 'doc', content: [{ type: 'paragraph', content: [
      { type: 'text', text: 'site', marks: [{ type: 'link', attrs: { href: 'https://tevejo.app' } }] },
      { type: 'text', text: ' e ' },
      { type: 'text', text: 'https://gov.br', marks: [{ type: 'link', attrs: { href: 'https://gov.br' } }] },
    ] }] };
    expect(jsonParaMarcacao(doc)).toBe('[site](https://tevejo.app) e https://gov.br');
  });

  it('preserva o texto na ida e volta pelo editor', () => {
    const casos = [
      'Texto simples',
      '**negrito** _itálico_ __sublinhado__ ==grifado== ~~riscado~~',
      'Primeira linha\nSegunda linha\n\nOutro parágrafo',
      '- rotina visual\n- abafador de ruído',
      '1. primeiro\n2. segundo',
      '> uma citação importante',
      'Veja [o guia](https://www.gov.br/saude) e https://tevejo.app',
      'Combinado **_negrito e itálico_** aqui',
    ];
    for (const caso of casos) {
      expect(idaEVolta(caso)).toBe(caso);
    }
  });
});
