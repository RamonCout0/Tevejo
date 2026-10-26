# Lista de Riscos do TeVejo

## Histórico de Revisões

| Data | Versão | Descrição | Autores |
| :--: | :----: | :-------: | :-----: |
| 30/03/26 | 1 | Versão inicial | Aaron, Fernando, Lorrany, Ramon, João Pedro, Wilson |

<!-- | - | - | - |  - | !-->

## Objetivo
Este documento consolida os riscos mais relevantes do TeVejo.

## Escala usada
- **Probabilidade**: Baixa / Média / Alta
- **Impacto**: Baixo / Médio / Alto / Crítico
- **Prioridade**: resultado qualitativo da combinação Probabilidade x Impacto

## Riscos Prioritários

| ID  | Risco | Probabilidade | Impacto | Prioridade |
|-----|------|--------------|---------|------------|
| R01 | Falta de testes automatizados | Alta | Média | Média |
| R02 | Problemas com dados sensíveis (LGPD) | Média | Crítico | Alta |
| R03 | Falta de monitoramento | Média | Alto | Média |
| R04 | Inconsistência de papéis | Média | Alto | Alta |
| R05 | Moderação insuficiente | Média | Crítico | Alta |
| R06 | Risco em encontros presenciais | Média | Alto | Alta |
| R07 | Problemas de performance | Média | Médio | Média |
| R08 | Problemas de UX/acessibilidade | Média | Alto | Alta |

## Detalhamentos

- **R01:** O projeto não possui testes automatizados no momento, o que pode causar erros sem serem percebidos.
  
- **R02:** O sistema lida com dados sensíveis (como relatos, desabafos, comentários etc.), exigindo cuidado com privacidade e conformidade com a LGPD.

- **R03:** Não há monitoramento do sistema em funcionamento, o que dificulta identificar falhas ou quedas rapidamente.

- **R04:** Existem diferentes tipos de usuários (papéis), e erros na definição de permissões podem permitir acessos indevidos.

- **R05:** A moderação de conteúdo ainda não está implementada, o que pode permitir conteúdos inadequados na plataforma.

- **R06:** A realização de encontros presenciais pode gerar riscos de segurança ou responsabilidade para os participantes.

- **R07:** Com o aumento de usuários e conteúdo, o sistema pode ficar lento se não houver otimização.

- **R08:** Se a interface não for acessível ou acolhedora, pode dificultar o uso pelo público-alvo.