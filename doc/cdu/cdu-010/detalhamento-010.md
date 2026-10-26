# CDU010 – Criar Encontro
- **Ator principal**: Moderador
- **Atores secundários**: Nenhum	 
- **Resumo**: Esse caso de uso descreve como o moderador cria um novo encontro dentro de uma comunidade, informando os dados necessários, como título, descrição, data, horário e endereço. O objetivo é disponibilizar o encontro para que os conviventes possam visualizá-lo e participar.
- **Pré-condição**: Ser Moderador de uma comunidade.
- **Pós-Condição**: O novo encontro é salvo e exibido na listagem de encontros disponíveis.

## Fluxo Principal
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: | 
| 1 - O moderador acessa a área de “Encontros” dentro da tela inicial da comunidade. | |  
| | 2 - O sistema mostra a lista dos encontros já criados e mostra as opções disponíveis para o moderador: "novo encontro", editar e excluir um encontro. |
| 3 - O moderador seleciona a opção “Criar Encontro”. | |
|  | 4 - O sistema exibe um novo espaço na lista de encontros para o moderador preencher com os dados do novo encontro. |
| 5 - O moderador preenche os campos obrigatórios (título, descrição, data, horário e endereço). | | 
| 6 - O moderador confirma o cadastro clicando em “Salvar” ou “Criar”. | | 
|  | 7 - O sistema faz a validação dos dados, salva o novo encontro e exibe a mensagem: “Encontro criado com sucesso.” |

## Fluxo Alternativo I - Cancelamento da criação
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: | 
| 2.3 - O moderador decide cancelar o cadastro antes de concluir. | |  
| | 2.4 - O sistema fecha o formulário e retorna à página de listagem de encontros, sem salvar as informações. | 

## Fluxo de Exceção I - Campos obrigatórios não preenchidos
| Ações do ator | Ações do sistema |
| :-----------------: |:-----------------: | 
| 1.1 - O moderador tenta salvar o encontro sem preencher todos os campos obrigatórios. |
| | 1.2 - O sistema exibe uma mensagem de erro informando os campos que precisam ser preenchidos: “Preencha todos os campos obrigatórios antes de continuar.” |

## Fluxo de Exceção II - Erro ao salvar o encontro
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: | 
| 2.1 - O moderador clica em “Salvar”, mas ocorre uma falha na conexão ou no banco de dados. | |  
| | 2.2 - O sistema mostra a mensagem: “Erro ao salvar o encontro. Tente novamente mais tarde.” |  


> Obs. as seções a seguir apenas serão utilizadas na segunda unidade do PDSWeb (segundo orientações do gerente do projeto).

## Diagrama de Interação (Sequência ou Comunicação)

> Substituir pela imagem correspondente...

## Diagrama de Classes de Projeto

> Substituir pela imagem contendo as classes (modelo, visão e templates) que implementam o respectivo CDU...
