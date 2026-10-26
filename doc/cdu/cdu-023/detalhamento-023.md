# CDU023. Interação em Postagens

- **Ator principal**: Convivente
- **Atores secundários**: Moderador
- **Resumo**: Esse caso de uso descreve como o convivente interage com uma postagem dentro de uma comunidade por meio de curtidas, comentários e denúncias. O objetivo é incentivar a participação saudável e permitir a interação entre os conviventes. O conteúdo inadequado terá sua devida moderação conforme alguma denúncia.
- **Pré-condição**: O convivente deve estar autenticado, ser membro da comunidade e a postagem deve estar disponível no feed.
- **Pós-Condição**: A interação escolhida (curtir, comentar ou denunciar) é registrada e refletida na postagem.

## Fluxo Principal - Comentar uma postagem
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 1 - O convivente acessa uma comunidade e seleciona uma postagem. | |
| | 2 - O sistema exibe a postagem com as opções de interação (curtir, comentar e denunciar). |
| 3 - O convivente seleciona a opção de comentar. | |
| | 4 - O sistema exibe todos os comentários associados à postagem e disponibiliza o campo para novo comentário. |
| 5 - O convivente escreve um comentário e confirma o envio. | |
| | 6 - O sistema valida a ação e registra o comentário na postagem. |
| | 7 - O sistema atualiza a interface, exibindo o comentário publicado. |

## Fluxo Alternativo I - Curtir uma postagem
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 1.1 - O convivente seleciona a opção “Curtir” em uma postagem. | |
| | 1.2 - O sistema valida a ação e registra a curtida na postagem. |
| | 1.3 - O sistema atualiza a interface, exibindo a nova quantidade de curtidas. |

## Fluxo Alternativo II - Denunciar postagem
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 2.1 - O convivente seleciona a opção “Denunciar” em uma postagem. | |
| | 2.2 - O sistema exibe as opções de motivo da denúncia e um campo complementar opcional. |
| 2.3 - O convivente informa o motivo e confirma a denúncia. | |
| | 2.4 - O sistema registra a denúncia, envia para análise de moderação e exibe a mensagem: “Denúncia enviada com sucesso.” |

## Fluxo Alternativo III - Comentário inválido
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 3.1 - O convivente tenta enviar um comentário vazio. | |
| | 3.2 - O sistema bloqueia o envio e exibe a mensagem: “Não foi possível publicar seu comentário. Verifique o conteúdo e tente novamente.” |

## Fluxo Alternativo IV - Remover curtida de uma postagem
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 4.1 - O convivente seleciona novamente a opção “Curtir” em uma postagem já curtida. | |
| | 4.2 - O sistema identifica que a postagem já possui uma curtida do convivente. |
| | 4.3 - O sistema remove a curtida registrada anteriormente. |
| | 4.4 - O sistema atualiza a interface, exibindo a nova quantidade de curtidas. |

> Obs. as seções a seguir apenas serão utilizadas na segunda unidade do PDSWeb (segundo orientações do gerente do projeto).

## Diagrama de Interação (Sequência ou Comunicação)

> Substituir pela imagem correspondente...

## Diagrama de Classes de Projeto

> Substituir pela imagem contendo as classes (modelo, visão e templates) que implementam o respectivo CDU...