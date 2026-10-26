# CDU009. Visualizar Mapa de serviços de saúde

* **Ator principal**: Convivente
* **Atores secundários**: Não existe.
* **Resumo**: O convivente visualiza um mapa interativo com pontos de serviços de saúde parceiros ou recomendados, podendo filtrar e ver detalhes do local.
* **Pré-condição**: Estar autenticado na plataforma como Convivente.
* **Pós-Condição**: O convivente localiza os serviços de saúde disponíveis e obtém as informações de contato/atendimento.

## Fluxo Principal - Visualizar Pontos e Aplicar Filtros

| Ações do ator | Ações do sistema |
| --- | --- |
| 1 - Clicar em "Mapa de Serviços" no menu principal |  |
|  | 2 - Carregar o mapa interativo, identificar a localização do usuário (se permitido) e exibir os marcadores dos serviços de saúde cadastrados |
| 3 - Selecionar um filtro por categoria (Ex: Psicologia, Ginecologia, Redução de Danos) |  |
|  | 4 - Atualizar o mapa exibindo apenas os marcadores que correspondem à categoria selecionada |

## Fluxo Alternativo I - Visualizar Detalhes de um Serviço de Saúde

| Ações do ator | Ações do sistema |
| --- | --- |
| 1.1 - Clicar em um marcador específico no mapa |  |
|  | 1.2 - Exibir um card/modal com as informações detalhadas do local (Nome, Endereço completo, Telefone/WhatsApp, Horário de funcionamento e especialidades oferecidas) |

## Diagrama de Interação (Sequência ou Comunicação)

> Substituir pela imagem correspondente...

## Diagrama de Classes de Projeto

> Substituir pela imagem contendo as classes (modelo, visão e templates) que implementam o respectivo CDU...