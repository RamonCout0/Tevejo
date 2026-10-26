/**
 * Limites de tamanho dos textos (maxlength e contadores dos campos).
 * Espelho de `src/backend_django/config/limites.py` — ao mudar um, mude o outro.
 */
export const LIMITES = {
  comunidadeNome: 80,
  comunidadeDescricao: 500,
  comunidadeCategoria: 40,
  comunidadeRegras: 2000,

  postagemTitulo: 50,
  postagemConteudo: 5000,
  comentario: 1000,
  denunciaDetalhe: 500,

  encontroTitulo: 100,
  encontroDescricao: 2000,
  encontroEndereco: 200,
  encontroTags: 120,

  justificativa: 500,

  usuarioNome: 80,
  usuarioBiografia: 500,

  conteudoTitulo: 150,
  conteudoFonte: 150,
  conteudoDescricao: 10000,
  tagNome: 40,
} as const;
