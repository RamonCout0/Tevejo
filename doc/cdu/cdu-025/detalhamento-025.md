# CDU025. Analisar Denúncias
- **Ator principal**: Moderador  
- **Atores secundários**: Convivente  
- **Resumo**: O moderador analisa denúncias realizadas pelos conviventes em publicações, podendo aprová-las ou reprová-las de acordo com as informações apresentadas.  
- **Pré-condição**: Convivente ter realizado uma denúncia em um post e a denúncia estar pendente de análise.  
- **Pós-Condição**: Denúncia analisada, status atualizado e ação aplicada sobre o post conforme a decisão tomada.  

## Fluxo Principal - Aprovar Denúncia

| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 1 - Clica no botão **Moderar** | |
| | 2 - Apresenta interface de moderação exibindo as denúncias pendentes |
| 3 - Seleciona uma denúncia | |
| | 4 - Exibe as informações da denúncia (motivo, denunciante, post e data) |
| 5 - Analisa as informações apresentadas | |
| 6 - Aprova a denúncia | |
| | 7 - Atualiza o status da denúncia para **Aprovada** |
| | 8 - Remove o post denunciado |
| | 9 - Registra a ação realizada |
| | 10 - Exibe mensagem de confirmação da aprovação |

## Fluxo Alternativo I - Reprovar Denúncia

| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 1 - Clica no botão **Moderar** | |
| | 2 - Apresenta interface de moderação exibindo as denúncias pendentes |
| 3 - Seleciona uma denúncia | |
| | 4 - Exibe as informações da denúncia |
| 5 - Analisa as informações apresentadas | |
| 6 - Reprova a denúncia | |
| | 7 - Atualiza o status da denúncia para **Reprovada** |
| | 8 - Mantém o post disponível |
| | 9 - Registra a decisão realizada |
| | 10 - Exibe mensagem de confirmação da reprovação |

## Fluxo Alternativo II - Não existem denúncias pendentes

| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 1 - Clica no botão **Moderar** | |
| | 2 - Apresenta interface de moderação |
| | 3 - Exibe mensagem informando que não existem denúncias pendentes |

## Diagrama de Interação (Sequência ou Comunicação)

> Substituir pela imagem correspondente...

## Diagrama de Classes de Projeto

> Substituir pela imagem contendo as classes (modelo, visão e templates) que implementam o respectivo CDU...