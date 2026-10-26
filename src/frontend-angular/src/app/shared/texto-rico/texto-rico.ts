import { Pipe, PipeTransform } from '@angular/core';

/**
 * Marcação de texto rico do TeVejo (a mesma que o `app-editor-texto` gera):
 *
 *   **negrito**   _itálico_   __sublinhado__   ==grifado==   ~~riscado~~
 *   [texto](https://link)  ou um link solto https://...
 *   - item de lista        1. item numerado        > citação
 *
 * Todo HTML digitado pelo usuário é escapado antes da formatação; só as tags
 * geradas aqui chegam à tela (e ainda passam pelo sanitizer do Angular no
 * [innerHTML]). Links só aceitam http(s) ou caminhos internos ("/...").
 */

const URL_PERMITIDA = /^(https?:\/\/|\/(?!\/))/i;

function escaparHtml(valor: string): string {
  return valor
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function linkHtml(url: string, texto: string): string {
  const externo = /^https?:\/\//i.test(url);
  const alvo = externo ? ' target="_blank" rel="noopener noreferrer"' : '';
  return `<a href="${escaparHtml(url)}"${alvo}>${texto}</a>`;
}

/** Aplica a formatação de uma linha (sem quebras). */
function formatarInline(linha: string): string {
  // 1) Separa os links para a formatação não mexer dentro das URLs.
  const links: string[] = [];
  const guardar = (html: string) => `\u0000${links.push(html) - 1}\u0000`;

  let texto = linha.replace(/\[([^\]\n]{1,200})\]\(([^)\s]{1,500})\)/g, (todo, rotulo: string, url: string) =>
    URL_PERMITIDA.test(url) ? guardar(linkHtml(url, escaparHtml(rotulo))) : todo,
  );
  texto = texto.replace(/\bhttps?:\/\/[^\s<>()]+[^\s<>().,;:!?'"]/gi, (url) =>
    guardar(linkHtml(url, escaparHtml(url.length > 60 ? `${url.slice(0, 57)}…` : url))),
  );

  // 2) Escapa o restante e aplica os estilos (do mais longo para o mais curto).
  texto = escaparHtml(texto)
    .replace(/\*\*(?=\S)([^*]+?)\*\*/g, '<strong>$1</strong>')
    .replace(/__(?=\S)([^_]+?)__/g, '<u>$1</u>')
    .replace(/==(?=\S)([^=]+?)==/g, '<mark>$1</mark>')
    .replace(/~~(?=\S)([^~]+?)~~/g, '<s>$1</s>')
    .replace(/(^|[\s(>])_(?=\S)([^_]+?)_(?=$|[\s).,!?:;<])/g, '$1<em>$2</em>')
    .replace(/(^|[\s(>])\*(?=\S)([^*]+?)\*(?=$|[\s).,!?:;<])/g, '$1<em>$2</em>');

  // 3) Devolve os links.
  return texto.replace(/\u0000(\d+)\u0000/g, (_, i: string) => links[Number(i)]);
}

/** Converte a marcação em HTML (blocos: parágrafos, listas e citações). */
export function textoRicoParaHtml(valor: string | null | undefined): string {
  if (!valor) return '';
  const linhas = valor.replace(/\r\n?/g, '\n').split('\n');
  const blocos: string[] = [];
  let paragrafo: string[] = [];
  let lista: { tipo: 'ul' | 'ol'; itens: string[] } | null = null;
  let citacao: string[] = [];

  const fecharParagrafo = () => {
    if (paragrafo.length) blocos.push(`<p>${paragrafo.map(formatarInline).join('<br>')}</p>`);
    paragrafo = [];
  };
  const fecharLista = () => {
    if (lista) blocos.push(`<${lista.tipo}>${lista.itens.map((i) => `<li>${formatarInline(i)}</li>`).join('')}</${lista.tipo}>`);
    lista = null;
  };
  const fecharCitacao = () => {
    if (citacao.length) blocos.push(`<blockquote>${citacao.map(formatarInline).join('<br>')}</blockquote>`);
    citacao = [];
  };
  const fecharTudo = () => {
    fecharParagrafo();
    fecharLista();
    fecharCitacao();
  };

  for (const bruta of linhas) {
    const linha = bruta.trimEnd();
    const marcador = linha.match(/^\s*[-*•]\s+(.*)$/);
    const numero = linha.match(/^\s*\d{1,3}[.)]\s+(.*)$/);
    const cita = linha.match(/^\s*>\s?(.*)$/);

    if (!linha.trim()) {
      fecharTudo();
    } else if (marcador || numero) {
      fecharParagrafo();
      fecharCitacao();
      const tipo = marcador ? 'ul' : 'ol';
      if (lista && lista.tipo !== tipo) fecharLista();
      lista ??= { tipo, itens: [] };
      lista.itens.push((marcador ?? numero)![1]);
    } else if (cita) {
      fecharParagrafo();
      fecharLista();
      citacao.push(cita[1]);
    } else {
      fecharLista();
      fecharCitacao();
      paragrafo.push(linha);
    }
  }
  fecharTudo();
  return blocos.join('');
}

/** Remove a marcação, para prévias curtas em cards (sem HTML). */
export function textoRicoParaSimples(valor: string | null | undefined): string {
  if (!valor) return '';
  return valor
    .replace(/\[([^\]\n]+)\]\([^)\s]+\)/g, '$1')
    .replace(/(\*\*|__|==|~~)(?=\S)(.+?)\1/g, '$2')
    .replace(/(^|\s)[_*](?=\S)([^_*]+?)[_*](?=$|[\s.,!?:;])/g, '$1$2')
    .replace(/^\s*([-*•]|\d{1,3}[.)]|>)\s+/gm, '')
    .replace(/\s*\n+\s*/g, ' ')
    .trim();
}

@Pipe({ name: 'textoRico', standalone: true })
export class TextoRicoPipe implements PipeTransform {
  transform(valor: string | null | undefined): string {
    return textoRicoParaHtml(valor);
  }
}

@Pipe({ name: 'textoSimples', standalone: true })
export class TextoSimplesPipe implements PipeTransform {
  transform(valor: string | null | undefined): string {
    return textoRicoParaSimples(valor);
  }
}
