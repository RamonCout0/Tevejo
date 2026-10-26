import { textoRicoParaHtml, textoRicoParaSimples } from './texto-rico';

describe('textoRico', () => {
  it('formata negrito, itálico, sublinhado, grifado e riscado', () => {
    const html = textoRicoParaHtml('**a** _b_ __c__ ==d== ~~e~~');
    expect(html).toBe('<p><strong>a</strong> <em>b</em> <u>c</u> <mark>d</mark> <s>e</s></p>');
  });

  it('escapa HTML digitado pelo usuário', () => {
    const html = textoRicoParaHtml('<img src=x onerror=alert(1)> <script>alert(1)</script>');
    expect(html).not.toContain('<img');
    expect(html).not.toContain('<script');
    expect(html).toContain('&lt;script&gt;');
  });

  it('só aceita links http(s) ou internos', () => {
    expect(textoRicoParaHtml('[ok](https://tevejo.app)')).toContain('href="https://tevejo.app"');
    expect(textoRicoParaHtml('[interno](/comunidades/1)')).toContain('href="/comunidades/1"');
    const perigoso = textoRicoParaHtml('[x](javascript:alert(1))');
    expect(perigoso).not.toContain('<a');
    expect(textoRicoParaHtml('[x](//evil.com)')).not.toContain('<a');
  });

  it('transforma link solto em link sem quebrar underscores da URL', () => {
    const html = textoRicoParaHtml('veja https://site.com/link_quebrado_aqui agora');
    expect(html).toContain('href="https://site.com/link_quebrado_aqui"');
    expect(html).not.toContain('<em>');
  });

  it('monta listas, listas numeradas e citações', () => {
    const html = textoRicoParaHtml('- um\n- dois\n\n1. primeiro\n2. segundo\n\n> citação');
    expect(html).toBe('<ul><li>um</li><li>dois</li></ul><ol><li>primeiro</li><li>segundo</li></ol><blockquote>citação</blockquote>');
  });

  it('mantém quebras de linha dentro do parágrafo', () => {
    expect(textoRicoParaHtml('linha 1\nlinha 2\n\nnovo')).toBe('<p>linha 1<br>linha 2</p><p>novo</p>');
  });

  it('gera texto simples sem marcação para prévias', () => {
    expect(textoRicoParaSimples('**Oi** _tudo_ ==bem==?\n- item\n[link](https://x.com)')).toBe('Oi tudo bem? item link');
  });
});
