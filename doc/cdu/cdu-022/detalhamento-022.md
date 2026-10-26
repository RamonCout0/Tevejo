# CDU022. Denunciar Conteúdo Educacional

- **Ator principal**: Convivente
- **Atores secundários**: Curador
- **Resumo**: Esse caso de uso descreve como o convivente, ao identificar problemas em um conteúdo educacional (informações desatualizadas, incorretas segundo novos estudos, links quebrados, entre outros), registra uma denúncia sobre o conteúdo. A denúncia fica disponível para análise do curador responsável.
- **Pré-condição**: O convivente deve estar autenticado e estar visualizando um conteúdo educacional já publicado.
- **Pós-Condição**: A denúncia é registrada no sistema, vinculada ao conteúdo, ao convivente e ao motivo selecionado, e fica disponível para o curador responsável avaliar.

## Fluxo Principal
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 1 - O convivente acessa a tela de detalhe de um conteúdo educacional. | |
| | 2 - O sistema exibe o conteúdo com a opção "Denunciar". |
| 3 - O convivente clica em "Denunciar". | |
| | 4 - O sistema apresenta o formulário de denúncia com motivos pré-definidos (conteúdo desatualizado, conteúdo incorreto segundo novos estudos, link quebrado, outro) e campo de descrição opcional. |
| 5 - O convivente seleciona o motivo, opcionalmente preenche a descrição e confirma. | |
| | 6 - O sistema registra a denúncia, vinculando-a ao conteúdo, ao convivente e ao motivo, e exibe mensagem de confirmação. |

## Fluxo Alternativo I - Convivente já denunciou esse conteúdo
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 1.1 - O convivente tenta denunciar um conteúdo no qual já possui uma denúncia pendente. | |
| | 1.2 - O sistema bloqueia a ação e exibe a mensagem: "Você já denunciou esse conteúdo. Aguarde a análise do curador." |

## Fluxo Alternativo II - Cancelar denúncia
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 2.1 - O convivente abre o formulário de denúncia mas decide cancelar antes de confirmar. | |
| | 2.2 - O sistema cancela a operação e mantém o conteúdo sem alterações. |

## Fluxo Alternativo III - Usuário não autenticado tenta denunciar
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 3.1 - Um visitante (não autenticado) clica em "Denunciar". | |
| | 3.2 - O sistema redireciona o visitante para a tela de autenticação. |

## Fluxo Alternativo IV - Erro ao registrar denúncia
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 4.1 - O convivente confirma uma denúncia. | |
| | 4.2 - O sistema encontra falha técnica ao persistir a decisão e exibe a mensagem: "Não foi possível registrar a denúncia. Tente novamente." |

> Obs. as seções a seguir apenas serão utilizadas na segunda unidade do PDSWeb (segundo orientações do gerente do projeto).

## Diagrama de Interação (Sequência ou Comunicação)

> Substituir pela imagem correspondente...

## Diagrama de Classes de Projeto

> Substituir pela imagem contendo as classes (modelo, visão e templates) que implementam o respectivo CDU...
