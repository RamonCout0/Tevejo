"""Categorias fixas das comunidades.

A categoria era texto livre e cada pessoa escrevia de um jeito, o que deixava
o filtro da tela de Comunidades confuso. Agora a pessoa escolhe uma da lista.

O mesmo conteúdo está em `src/frontend-angular/src/app/shared/categorias.ts`
(com ícone e cor). Ao mudar um, mude o outro.

Comunidades antigas com categorias fora da lista continuam funcionando; no
filtro elas aparecem em "Outros" e, ao editar, o moderador escolhe uma nova.
"""

CATEGORIAS = [
    'Apoio familiar',
    'Diagnóstico',
    'Educação e escola',
    'Saúde e terapias',
    'Direitos e benefícios',
    'Adultos autistas',
    'Trabalho e inclusão',
    'Lazer e convivência',
    'Outros',
]
