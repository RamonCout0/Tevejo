# CDU005 – Visualizar Encontros Públicos 

- **Ator principal**: Convivente
- **Atores secundários**: Moderador	 
- **Resumo**: Esse caso de uso descreve como o convivente acessa a área de encontros públicos da plataforma para ver os eventos disponíveis, com informações como data, local, descrição e imagem. O objetivo é permitir que o convivente conheça os encontros abertos organizados pelas comunidades.
- **Pré-condição**: O convivente deve estar logado no sistema e devem existir encontros públicos ativos.
- **Pós-Condição**: O sistema exibe as informações dos encontros públicos para o convivente.

## Fluxo Principal
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: | 
| 1 - O convivente acessa a área de “Encontros Públicos”. | |  
| | 2 - O sistema mostra uma lista com os encontros públicos disponíveis, contendo título, descrição, data, local e imagem. |
| 3 - O convivente seleciona um encontro para visualizar os detalhes. | |  
| | 4 - O sistema exibe as informações completas do encontro selecionado.| 
| 5 - O convivente lê as informações e decide se deseja participar ou não. | | 

## Fluxo Alternativo I - Nenhum encontro público disponível
| Ações do ator | Ações do sistema |
| :-----------------: |:-----------------: | 
| 1.1 - O convivente acessa a área de encontros públicos. | |  
| | 1.2 - O sistema verifica que não existem encontros cadastrados ou ativos e mostra a mensagem: “Nenhum encontro público disponível no momento.” |

## Fluxo Alternativo II - Erro ao carregar informações
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: | 
| 2.1 - O convivente tenta abrir um encontro público. | |  
| | 2.2 - O sistema encontra um erro (dados incompletos ou falha de conexão) e mostra a mensagem: “Não foi possível carregar as informações do encontro. Tente novamente mais tarde.” |  

> Obs. as seções a seguir apenas serão utilizadas na segunda unidade do PDSWeb (segundo orientações do gerente do projeto).

## Diagrama de Interação (Sequência ou Comunicação)

> Substituir pela imagem correspondente...

## Diagrama de Classes de Projeto

> Substituir pela imagem contendo as classes (modelo, visão e templates) que implementam o respectivo CDU...