# CDU014. Gerenciar adminstradores

- **Ator principal**: Adminstrador.
- **Atores secundários**: Não existe.
- **Resumo**: Administradores podem gerenciar outros administradores de hierarquia inferior.
- **Pré-condição**: Ser adminstrador do sistema.
- **Pós-Condição**: Gerenciar outros adminstradores.

## Fluxo Principal
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: | 
| 1 - Acessar a lista de adminstradores | |  
| | 2 - Exibir opções: adicionar ou remover adminstrador |
| 3 - Selecionar ação desejada | |
| | 4 - Executar ação selecionada |

## Fluxo Alternativo I - Tentar remover adminstrador de uma hieraquia superior
| Ações do ator | Ações do sistema |
| :-----------------: |:-----------------: | 
| 2.1 - Selecionar opção de remover adminstrador | |  
| | 2.2 - Exibir pop-up informado que não é possível realizar essa ação |

## Fluxo Alternativo II - ...
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: | 
| 2.1 - ... | |  
| | 2.2 - ... |  

> Obs. as seções a seguir apenas serão utilizadas na segunda unidade do PDSWeb (segundo orientações do gerente do projeto).

## Diagrama de Interação (Sequência ou Comunicação)

> Substituir pela imagem correspondente...

## Diagrama de Classes de Projeto

> Substituir pela imagem contendo as classes (modelo, visão e templates) que implementam o respectivo CDU...