# CDU003 – Visualizar Conteúdo Educacional

- **Ator principal**: Convivente
- **Atores secundários**: Curador	 
- **Resumo**: Esse caso de uso mostra como o convivente acessa e visualiza os conteúdos educacionais que estão disponíveis na plataforma. Esses conteúdos foram enviados e aprovados por curadores. O objetivo é que o convivente possa aprender e se informar dentro da comunidade.
- **Pré-condição**: O convivente precisa estar logado no sistema e deve haver conteúdo educacional disponível.
- **Pós-Condição**: O conteúdo educacional é exibido corretamente para o convivente.

## Fluxo Principal
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: | 
| 1 - O convivente entra na área de “Conteúdos Educacionais”. | |  
| | 2 - O sistema mostra a lista de conteúdos disponíveis, com título, tipo e o nome do curador. |
| 3 - O convivente escolhe um conteúdo para ver. | |  
| | 4 - O sistema abre o conteúdo completo (texto, imagem, vídeo, link ou arquivo). |
| 5 - O convivente lê ou interage com o conteúdo. | |

## Fluxo de Exceção  I - Nenhum conteúdo disponível
| Ações do ator | Ações do sistema |
| :-----------------: |:-----------------: | 
| 1.1 - O convivente acessa a área de conteúdos educacionais. | |  
| | 1.2 - O sistema verifica que não há conteúdos cadastrados e mostra a mensagem: “Nenhum conteúdo educacional disponível no momento.” |

## Fluxo de Exceção II - Erro ao carregar o conteúdo
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: | 
| 2.1- O convivente escolhe um conteúdo para visualizar. | |  
| | 2.2 - O sistema encontra um erro (arquivo corrompido, link inválido ou falha de conexão) e mostra a mensagem: “Não foi possível carregar o conteúdo. Tente novamente mais tarde.” |  

> Obs. as seções a seguir apenas serão utilizadas na segunda unidade do PDSWeb (segundo orientações do gerente do projeto).

## Diagrama de Interação (Sequência ou Comunicação)

> Substituir pela imagem correspondente...

## Diagrama de Classes de Projeto

> Substituir pela imagem contendo as classes (modelo, visão e templates) que implementam o respectivo CDU...
