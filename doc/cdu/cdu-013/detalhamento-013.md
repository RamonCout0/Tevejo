# CDU013 – Ver Perfil de Outros Usuários

- **Ator principal**: Convivente
- **Atores secundários**: ...	 
- **Resumo**: Esse caso de uso mostra como o convivente pode visualizar o perfil de outro usuário dentro da plataforma. O objetivo é permitir que o convivente conheça mais sobre outros membros, vendo informações como nome, biografia e foto de perfil.
- **Pré-condição**: O convivente deve estar logado no sistema e o outro usuário deve possuir um perfil ativo.
- **Pós-Condição**: O sistema exibe as informações do perfil do usuário selecionado.

## Fluxo Principal
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: | 
| 1 - O convivente acessa a área de busca ou lista de usuários. | |  
| | 2 - O sistema exibe a lista de usuários, mostrando nome, biografia e foto de perfil. |
| 3 - O convivente seleciona o perfil de um usuário específico. | |  
| | 4 - O sistema abre o perfil do usuário e mostra suas informações (nome, biografia e foto).| 
| 5 - O convivente visualiza as informações do outro usuário. | | 

## Fluxo Alternativo I - Perfil inexistente
| Ações do ator | Ações do sistema |
| :-----------------: |:-----------------: | 
| 1.1 - O convivente tenta acessar o perfil de um usuário que não existe ou foi excluído. | |  
| | 1.2 - O sistema exibe a mensagem: “Perfil não encontrado.” |

## Fluxo Alternativo II - Erro ao carregar o perfil
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: | 
| 2.1 - O convivente seleciona um perfil para visualizar. | |  
| | 2.2 - O sistema apresenta falha no carregamento (erro de conexão ou dados incompletos) e mostra a mensagem: “Não foi possível carregar o perfil. Tente novamente mais tarde.” |  

> Obs. as seções a seguir apenas serão utilizadas na segunda unidade do PDSWeb (segundo orientações do gerente do projeto).

## Diagrama de Interação (Sequência ou Comunicação)

> Substituir pela imagem correspondente...

## Diagrama de Classes de Projeto

> Substituir pela imagem contendo as classes (modelo, visão e templates) que implementam o respectivo CDU...