# CDU007. Postar nas Comunidades

- **Atores principais**: Convivente, Moderador.
- **Atores secundários**: Nenhum.	 
- **Resumo**: Postar é o processo de criação e publicação de postagens dentro das comunidades do TeVejo, permitindo que conviventes e moderadores compartilhem experiências, informações, dúvidas, conteúdos educacionais e mensagens de apoio.
- **Pré-condição**: O usuário deve estar autenticado e ser membro da comunidade onde deseja realizar a postagem.
- **Pós-Condição**: O post é salvo na base de dados e exibido no feed da comunidade, ficando disponível para interações dos demais usuários.

## Fluxo Principal - Credenciais Válidas
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: | 
| 1 - O usuário acessa a comunidade desejada. | |  
| | 2 - O sistema exibe o feed da comunidade e o botão “Postar”. | 
| 3 - O usuário seleciona a opção “Postar”. | |
| | 4 - O sistema exibe o formulário de criação de postagem. |
| 5 - O usuário informa o título e o conteúdo textual da postagem. | |
| 6 - O usuário pode, opcionalmente, adicionar links para conteúdos educacionais ou encontros relacionados. | |
| 7 - O usuário confirma a publicação clicando em “Postar”. | |
| | 8 - O sistema valida os campos obrigatórios da postagem. |
| | 9 - O sistema salva o post na base de dados. |

## Fluxo Alternativo I - Conteúdo vazio
| Ações do ator | Ações do sistema |
| :-----------------: |:-----------------: | 
| | 8.1 - O sistema identifica que o convivente tentou realizar uma postagem com conteúdo vazio ou inválido. |
| | 8.2 - O sistema exibe a mensagem de erro “O conteúdo da postagem não pode estar vazio”. |
| 8.3 - O usuário corrige as informações da postagem. | |
| | 8.4 - O sistema retorna ao formulário de criação da postagem. |

## Fluxo Alternativo II - Convivente não pertence à comunidade
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 1.1 - O convivente tenta acessar a funcionalidade de postagem da comunidade. | |
| | 1.2 - O sistema verifica que o usuário não é membro da comunidade. |
| | 1.3 - O sistema exibe a mensagem “Você precisa participar da comunidade para publicar conteúdos”. |

## Fluxo Alternativo III - Usuário não autenticado
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 1.1 - O usuário tenta acessar uma comunidade sem estar autenticado. | |
| | 1.2 - O sistema identifica que não existe uma sessão ativa. |
| | 1.3 - O sistema redireciona o usuário para a tela de login. |

> Obs. as seções a seguir apenas serão utilizadas na segunda unidade do PDSWeb (segundo orientações do gerente do projeto).

## Diagrama de Interação (Sequência ou Comunicação)

> Substituir pela imagem correspondente...

## Diagrama de Classes de Projeto

> Substituir pela imagem contendo as classes (modelo, visão e templates) que implementam o respectivo CDU...
