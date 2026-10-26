# CDU015 – Gerenciar Moderadores

- **Ator principal**: Administrador
- **Atores secundários**: Não existe.
- **Resumo**: Esse caso de uso descreve como o administrador gerencia os moderadores da plataforma. Ele pode visualizar a lista de moderadores, adicionar novos, editar informações e remover aqueles que não fazem mais parte da equipe. O objetivo é manter o controle e a organização dos usuários que possuem funções de moderação.
- **Pré-condição**: Ser Adminstrador do tevejo.
- **Pós-Condição**: O sistema atualiza a lista de moderadores conforme as ações realizadas (adição, edição ou remoção).

## Fluxo Principal
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: | 
| 1 - O administrador acessa a área de “Gerenciar Moderadores”.| |  
| | 2 - O sistema exibe a lista de moderadores cadastrados, mostrando nome e e-mail. |
| 3 - O administrador escolhe uma das opções: adicionar, editar ou remover um moderador.| | 
| | 4 - O sistema abre a tela correspondente à ação escolhida. |
| 5 - O administrador realiza a ação desejada (preenche dados, confirma alteração ou exclusão).| | 
| | 6 - O sistema processa a solicitação e exibe a mensagem de sucesso correspondente. |

## Fluxo Alternativo I - Nenhum moderador cadastrado
| Ações do ator | Ações do sistema |
| :-----------------: |:-----------------: | 
| 1.1 - O administrador acessa a área de gerenciamento. | |  
| | 1.2 - O sistema verifica que não existem moderadores cadastrados e mostra a mensagem: “Nenhum moderador encontrado.” |

## Fluxo Alternativo II - Dados inválidos no cadastro
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: | 
| 2.1 - O administrador tenta cadastrar ou editar um moderador com dados incompletos ou inválidos. | |  
| | 2.2 - O sistema exibe a mensagem: “Verifique os dados informados e tente novamente.” |  

## Fluxo Alternativo III – Erro ao atualizar informações
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: | 
| 3.1 - O administrador confirma a ação (adicionar, editar ou remover).| |  
| | 3.2 - O sistema encontra um erro (como falha de conexão ou erro interno) e mostra a mensagem: “Não foi possível concluir a operação. Tente novamente mais tarde.” | 

## Fluxo Alternativo IV – Ação cancelada
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: | 
| 4.1 - O administrador inicia uma ação, mas decide cancelar antes de confirmar.| |  
| | 4.2 - O sistema cancela a operação e mantém a lista de moderadores inalterada. |

> Obs. as seções a seguir apenas serão utilizadas na segunda unidade do PDSWeb (segundo orientações do gerente do projeto).

## Diagrama de Interação (Sequência ou Comunicação)

> Substituir pela imagem correspondente...

## Diagrama de Classes de Projeto

> Substituir pela imagem contendo as classes (modelo, visão e templates) que implementam o respectivo CDU...