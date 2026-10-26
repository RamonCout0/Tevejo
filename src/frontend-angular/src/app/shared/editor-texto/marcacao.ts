import type { JSONContent } from '@tiptap/core';

/**
 * Converte o documento do editor visual (Tiptap/ProseMirror) para a marcação
 * de texto rico que é salva no banco e lida pelo pipe `textoRico`:
 *
 *   **negrito**  _itálico_  __sublinhado__  ==grifado==  ~~riscado~~
 *   [texto](url)   "- item"   "1. item"   "> citação"
 *
 * O caminho inverso (marcação -> editor) usa `textoRicoParaHtml`, já que o
 * Tiptap entende o HTML que ele gera.
 */

const MARCAS: Record<string, [string, string]> = {
  bold: ['**', '**'],
  underline: ['__', '__'],
  highlight: ['==', '=='],
  strike: ['~~', '~~'],
  italic: ['_', '_'],
};

/** Ordem de aninhamento: a primeira fica por fora. */
const ORDEM = ['bold', 'underline', 'highlight', 'strike', 'italic'];

function textoComMarcas(no: JSONContent): string {
  let texto = no.text ?? '';
  if (!texto) return '';
  const marcas = no.marks ?? [];

  // Espaços nas pontas ficam fora das marcas ("** a**" não seria reconhecido).
  const inicio = texto.match(/^\s*/)?.[0] ?? '';
  const fim = texto.match(/\s*$/)?.[0] ?? '';
  let miolo = texto.slice(inicio.length, texto.length - fim.length);
  if (!miolo) return texto;

  const tipos = new Set(marcas.map((m) => m.type));
  for (const tipo of [...ORDEM].reverse()) {
    if (tipos.has(tipo)) {
      const [abre, fecha] = MARCAS[tipo];
      miolo = `${abre}${miolo}${fecha}`;
    }
  }

  const link = marcas.find((m) => m.type === 'link');
  const href = link?.attrs?.['href'] as string | undefined;
  if (href) {
    miolo = href === no.text?.trim() ? href : `[${miolo}](${href})`;
  }
  return `${inicio}${miolo}${fim}`;
}

/** Junta os nós de texto vizinhos, devolvendo as linhas (hardBreak = nova linha). */
function linhasInline(conteudo: JSONContent[] = []): string[] {
  const linhas: string[] = [''];
  for (const no of conteudo) {
    if (no.type === 'hardBreak') {
      linhas.push('');
    } else if (no.type === 'text') {
      linhas[linhas.length - 1] += textoComMarcas(no);
    }
  }
  return linhas;
}

function blocoParaLinhas(bloco: JSONContent): string[] {
  switch (bloco.type) {
    case 'paragraph':
      return linhasInline(bloco.content);

    case 'bulletList':
    case 'orderedList': {
      const ordenada = bloco.type === 'orderedList';
      const inicio = Number(bloco.attrs?.['start'] ?? 1);
      return (bloco.content ?? []).map((item, i) => {
        const texto = (item.content ?? [])
          .flatMap((filho) => blocoParaLinhas(filho))
          .filter((l) => l.trim())
          .join(' ');
        return `${ordenada ? `${inicio + i}.` : '-'} ${texto}`;
      });
    }

    case 'blockquote':
      return (bloco.content ?? [])
        .flatMap((filho) => blocoParaLinhas(filho))
        .map((linha) => `> ${linha}`);

    default:
      return linhasInline(bloco.content);
  }
}

export function jsonParaMarcacao(doc: JSONContent | null | undefined): string {
  const blocos = (doc?.content ?? [])
    .map((bloco) => blocoParaLinhas(bloco).join('\n'))
    .filter((texto) => texto.trim());
  return blocos.join('\n\n').trim();
}
