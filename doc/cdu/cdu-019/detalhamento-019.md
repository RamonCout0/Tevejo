# CDU019 - Termo de Consentimento e Responsabilidade

- **Ator principal**: Convivente
- **Atores secundários**: Não existe.	 
- **Resumo**: Este caso de uso descreve como o convivente visualiza e aceita o Termo de Consentimento e Responsabilidade. A aceitação é obrigatória para garantir que o usuário tenha ciência das regras da comunidade e proteção de dados antes de interagir na plataforma.
- **Pré-condição**: O convivente deve estar acessando o sistema pela primeira vez ou ainda não ter aceitado o termo de consentimento.
- **Pós-Condição**: O sistema registra a aceitação do termo e libera o acesso do Convivente à plataforma.

## Fluxo Principal
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: | 
| 1 - O convivente acessa a plataforma para cadastro. | |  
| | 2 - O sistema verifica se o convivente já aceitou o termo de consentimento. |
| | 3 - O sistema exibe o texto integral do termo com as opções “Concordo” e “Não concordo”. | 
| 4 - O convivente lê o conteúdo e seleciona “Concordo”.| | 
| | 5 - O sistema registra o aceite e libera o acesso à plataforma. |

## Fluxo Alternativo I - O convivente não aceita o termo
| Ações do ator | Ações do sistema |
| :-----------------: |:-----------------: | 
| 1.1 - O convivente lê o termo e escolhe “Não concordo”. | |  
| | 1.2 - O sistema exibe mensagem: “O aceite é obrigatório para utilizar a plataforma TeVejo.” |.
| |1.3 - O sistema impede a progressão para as telas internas e mantém o usuário na tela de boas-vindas/login.|

## Fluxo Alternativo II - Erro ao registrar aceitação
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: | 
| 2.1 - O convivente seleciona “Concordo”. | |  
| | 2.2 - O sistema tenta registrar a aceitação, mas ocorre uma falha (como erro de conexão ou banco de dados) e exibe a mensagem: “Não foi possível registrar sua aceitação. Tente novamente.” |  

## Fluxo Alternativo III - Termo atualizado
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: | 
| 3.1 - O convivente acessa a plataforma após o termo ser atualizado. | |  
| | 3.2 - O sistema detecta a nova versão do termo e solicita uma nova leitura e aceitação antes de liberar o acesso. |

> Obs. as seções a seguir apenas serão utilizadas na segunda unidade do PDSWeb (segundo orientações do gerente do projeto).

## Diagrama de Interação (Sequência ou Comunicação)

> Substituir pela imagem correspondente...

## Diagrama de Classes de Projeto

> Substituir pela imagem contendo as classes (modelo, visão e templates) que implementam o respectivo CDU...