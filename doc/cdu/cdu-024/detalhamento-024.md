# CDU024. Moderar Conviventes

- **Ator principal**: Moderador
- **Atores secundários**: Convivente
- **Resumo**: Esse caso de uso descreve como o moderador aplica ações de convivência em membros da comunidade, como restringir ou banir conviventes que violem as diretrizes. O objetivo é preservar um ambiente acolhedor e seguro.
- **Pré-condição**: O moderador deve estar autenticado, possuir permissão de moderação na comunidade e existir ao menos um convivente com comportamento inadequado.
- **Pós-Condição**: A ação de moderação escolhida é registrada e aplicada ao convivente na comunidade.

## Fluxo Principal - Restringir convivente
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 1 - O moderador acessa a área de moderação da comunidade. | |
| | 2 - O sistema exibe a lista de conviventes e os registros de comportamento/denúncias vinculados. |
| 3 - O moderador seleciona um convivente para avaliar. | |
| | 4 - O sistema apresenta o histórico resumido e as ações possíveis (advertir, restringir, banir). |
| 5 - O moderador escolhe “Restringir”, define duração e confirma a ação. | |
| | 6 - O sistema aplica a restrição, registra a decisão e notifica o convivente sobre a medida adotada. |

## Fluxo Alternativo I - Banir convivente
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 1.1 - O moderador seleciona um convivente com violação grave ou recorrente. | |
| | 1.2 - O sistema exibe confirmação de banimento e solicita justificativa obrigatória. |
| 1.3 - O moderador informa a justificativa e confirma o banimento. | |
| | 1.4 - O sistema remove o convivente da comunidade, bloqueia novo acesso e registra a ação no histórico de moderação. |

## Fluxo Alternativo II - Cancelar moderação
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 2.1 - O moderador inicia uma ação de moderação, mas decide cancelar antes da confirmação. | |
| | 2.2 - O sistema cancela a operação e mantém o status atual do convivente sem alterações. |

## Fluxo Alternativo III - Erro ao aplicar ação
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 3.1 - O moderador confirma uma ação de moderação. | |
| | 3.2 - O sistema encontra falha técnica ao persistir a decisão e exibe a mensagem: “Não foi possível concluir a moderação. Tente novamente.” |

## Diagrama de Interação (Sequência ou Comunicação)

> Substituir pela imagem correspondente...

## Diagrama de Classes de Projeto

> Substituir pela imagem contendo as classes (modelo, visão e templates) que implementam o respectivo CDU...