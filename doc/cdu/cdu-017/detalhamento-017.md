# CDU017 - Gerenciar Conviventes

- **Ator principal**: Administrador
- **Atores secundários**: ...	 
- **Resumo**: Esse caso de uso descreve como o administrador pode gerenciar os conviventes da plataforma. Isso inclui ações como visualizar perfis, ativar, desativar ou excluir usuários quando necessário. O objetivo é manter o controle e a organização dos usuários cadastrados no sistema.
- **Pré-condição**: O administrador deve estar logado no sistema e possuir permissão para gerenciar conviventes.
- **Pós-Condição**: As alterações realizadas pelo administrador (como ativar, desativar ou excluir um convivente) são salvas e aplicadas no sistema.

## Fluxo Principal
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: | 
| 1 - O administrador acessa a área de “Gerenciar Conviventes”. | |  
| | 2 - O sistema mostra uma lista com todos os conviventes cadastrados, incluindo nome, e-mail e status da conta. |
| 3 - O administrador seleciona um convivente específico. | |  
| | 4 - O sistema exibe os detalhes do convivente e as opções de gerenciamento (ativar, desativar, excluir).| 
| 5 - O administrador escolhe a ação desejada. | |
| | 6 - O sistema executa a ação selecionada e atualiza o status do convivente.|  

## Fluxo Alternativo I - Nenhum convivente cadastrado
| Ações do ator | Ações do sistema |
| :-----------------: |:-----------------: | 
| 1.1 - O administrador acessa a área de gerenciamento. | |  
| | 1.2 - O sistema identifica que não há conviventes cadastrados e mostra a mensagem: “Nenhum convivente encontrado.” |

## Fluxo Alternativo II - Erro ao atualizar status
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: | 
| 2.1 - O administrador seleciona uma ação (ativar, desativar ou excluir). | |  
| | 2.2 - O sistema encontra um erro ao tentar atualizar os dados e mostra a mensagem: “Erro ao atualizar convivente. Tente novamente.” | 

> Obs. as seções a seguir apenas serão utilizadas na segunda unidade do PDSWeb (segundo orientações do gerente do projeto).

## Diagrama de Interação (Sequência ou Comunicação)

> Substituir pela imagem correspondente...

## Diagrama de Classes de Projeto

> Substituir pela imagem contendo as classes (modelo, visão e templates) que implementam o respectivo CDU...