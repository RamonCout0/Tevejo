# CDU018. Editar dados pessoais

- **Ator principal**: Usuário autenticado (Convivente, Curador, Moderador ou Administrador)
- **Atores secundários**: Não existem.
- **Resumo**: Este caso de uso descreve como um usuário autenticado pode alterar seus próprios dados pessoais (foto de perfil, nome, e-mail e biografia), corrigindo informações incorretas ou mantendo seu perfil atualizado.
- **Pré-condição**: O usuário deve estar autenticado no sistema.
- **Pós-Condição**: Os dados pessoais do usuário são validados e persistidos no sistema, refletindo as alterações no perfil.

## Fluxo Principal
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 1 - O usuário acessa seu perfil e seleciona a opção "Editar dados pessoais". | |
| | 2 - O sistema exibe um formulário com os dados pessoais atuais do usuário (foto de perfil, nome, e-mail, biografia) preenchidos e editáveis, além da opção "Alterar foto". |
| 3 - O usuário altera um ou mais campos do formulário (incluindo, opcionalmente, a foto de perfil). | |
| 4 - O usuário confirma a edição clicando em "Salvar". | |
| | 5 - O sistema valida os dados informados. |
| | 6 - O sistema persiste as alterações e exibe a mensagem: "Dados atualizados com sucesso." |
| | 7 - O sistema retorna o usuário para a tela de perfil com os dados atualizados. |

## Fluxo Alternativo I - Dados inválidos
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 1.1 - O usuário confirma a edição com algum campo inválido (ex.: nome com menos de 3 caracteres ou e-mail em formato incorreto). | |
| | 1.2 - O sistema identifica o(s) erro(s) de validação, mantém o formulário preenchido e exibe a(s) mensagem(ns) correspondente(s) ao(s) campo(s) inválido(s). |
| | 1.3 - O fluxo retorna ao passo 3 do fluxo principal. |

## Fluxo Alternativo II - E-mail já cadastrado
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 2.1 - O usuário informa um e-mail que já está em uso por outro usuário e confirma a edição. | |
| | 2.2 - O sistema identifica a duplicidade e exibe a mensagem: "Este e-mail já está em uso." |
| | 2.3 - O fluxo retorna ao passo 3 do fluxo principal. |

## Fluxo Alternativo III - Alterar foto de perfil
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 3.1 - O usuário seleciona a opção "Alterar foto" e escolhe um arquivo de imagem. | |
| | 3.2 - O sistema valida o arquivo quanto a formato (JPG/PNG) e tamanho máximo de 5 MB. |
| | 3.3 - O sistema exibe a pré-visualização da nova foto no formulário e, ao salvar, persiste o arquivo no armazenamento de mídia do servidor. |
| | 3.4 - **Exceção 3.2a**: Se o arquivo for inválido (formato ou tamanho acima de 5 MB), o sistema exibe a mensagem: "Arquivo de imagem inválido." e mantém a foto anterior. |

## Fluxo Alternativo IV - Cancelar edição
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 4.1 - O usuário seleciona a opção "Cancelar" durante a edição. | |
| | 4.2 - O sistema descarta as alterações não salvas e retorna o usuário para a tela de perfil com os dados originais. |

## Fluxo Alternativo V - Falha ao salvar
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 5.1 - O usuário confirma a edição com dados válidos. | |
| | 5.2 - O sistema encontra uma falha ao persistir as alterações e exibe a mensagem: "Erro ao atualizar os dados. Tente novamente." |
| | 5.3 - O fluxo retorna ao passo 3 do fluxo principal, mantendo o formulário preenchido. |

> Obs. as seções a seguir apenas serão utilizadas na segunda unidade do PDSWeb (segundo orientações do gerente do projeto).

## Diagrama de Interação (Sequência ou Comunicação)

> Substituir pela imagem correspondente...

## Diagrama de Classes de Projeto

> Substituir pela imagem contendo as classes (modelo, visão e templates) que implementam o respectivo CDU...
