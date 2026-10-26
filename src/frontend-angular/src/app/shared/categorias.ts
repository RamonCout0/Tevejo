/**
 * Categorias fixas das comunidades, com ícone para os botões de escolha.
 * Espelho de `src/backend_django/comunidades/categorias.py` — ao mudar um, mude o outro.
 */
export interface CategoriaComunidade {
  nome: string;
  icone: string;
  descricao: string;
}

export const CATEGORIAS: CategoriaComunidade[] = [
  { nome: 'Apoio familiar', icone: 'fa-hand-holding-heart', descricao: 'Famílias e cuidadores' },
  { nome: 'Diagnóstico', icone: 'fa-magnifying-glass', descricao: 'Primeiros passos e dúvidas' },
  { nome: 'Educação e escola', icone: 'fa-school', descricao: 'Inclusão escolar e aprendizagem' },
  { nome: 'Saúde e terapias', icone: 'fa-heart-pulse', descricao: 'Terapias, médicos e bem-estar' },
  { nome: 'Direitos e benefícios', icone: 'fa-scale-balanced', descricao: 'Leis, BPC, carteirinha' },
  { nome: 'Adultos autistas', icone: 'fa-user', descricao: 'Vivências na vida adulta' },
  { nome: 'Trabalho e inclusão', icone: 'fa-briefcase', descricao: 'Emprego e mercado de trabalho' },
  { nome: 'Lazer e convivência', icone: 'fa-face-smile', descricao: 'Passeios, brincadeiras e amizades' },
  { nome: 'Outros', icone: 'fa-ellipsis', descricao: 'Outros assuntos' },
];

const NOMES = new Set(CATEGORIAS.map((c) => c.nome));

/** Comunidades antigas (categoria livre) entram em "Outros" no filtro. */
export function categoriaDoFiltro(categoria: string | null | undefined): string {
  const nome = (categoria ?? '').trim();
  return NOMES.has(nome) ? nome : 'Outros';
}

export function iconeDaCategoria(categoria: string | null | undefined): string {
  return CATEGORIAS.find((c) => c.nome === categoria)?.icone ?? 'fa-tag';
}
