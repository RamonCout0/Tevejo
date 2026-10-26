# Relatório Final de Avaliação por Inspeção de Interface
**Projeto:** Tevejo  
**Instrumento Utilizado:** Lista EURECA (Diretrizes de design para criação e avaliação de interfaces)  
**Avaliadores (Equipe):** Aaron, Fernando Yuri, João Pedro Dantas, Lorrany Fagundes, Manoel Pinto Junior e Ramon Couto.  
**Telas Avaliadas:** Dashboard (Discussões Públicas), Criação de Postagens, Explorar/Criar Comunidades, Visão de Visitante/Membro de Comunidade, Moderação e Fluxo de Autenticação.

---

## 1. Visão Geral
Este documento consolida os resultados da avaliação heurística realizada individualmente pelos 6 integrantes do grupo. A inspeção teve como objetivo identificar violações de usabilidade e acessibilidade na interface do sistema **Tevejo**, propondo correções para aprimorar a experiência dos conviventes, especialmente o público-alvo (neurodivergentes e pessoas ligadas ao TEA).

---

## 2. Totalização Geral de Problemas

Ao todo, o grupo identificou **133 incidências de problemas** na interface do sistema, levantados ao longo dos fluxos principais da aplicação. 

### 2.1. Totalização por Gravidade (Severidade)
A maioria dos problemas concentra-se na gravidade "Média", indicando atritos que causam dúvidas ou erros contornáveis, mas há um volume significativo de problemas "Altos/Críticos" que impedem tarefas fundamentais (como moderação, navegação e segurança de dados).

| Gravidade | Quantidade de Problemas | Impacto na Experiência |
| :--- | :---: | :--- |
| **Alta / Crítica** | **29** | Impede o usuário de concluir uma tarefa principal, compromete a segurança/dados ou causa perda de informações. |
| **Média** | **70** | Causa confusão, exige esforço cognitivo extra ou gera erros que o usuário consegue contornar com dificuldade. |
| **Baixa** | **34** | Problema estético ou de usabilidade que incomoda, mas não impede a continuidade do fluxo. |
| **TOTAL GERAL** | **133** | - |

### 2.2. Totalização por Categoria (Tipo / Diretrizes EURECA)
Os problemas foram classificados de acordo com os grupos de diretrizes da Lista EURECA. Os principais ofensores do sistema atual estão em **Formatação** (contraste, hierarquia visual) e **Aspectos Funcionais** (falta de validação, perda de dados).

| Categoria EURECA | Quantidade | Principais Diretrizes Violadas |
| :--- | :---: | :--- |
| **Formatação (FM)** | 37 | FM11 (Contraste), FM1 (Visibilidade), FM2 (Hierarquia), FM4 (Ordenação). |
| **Aspectos Funcionais (AF)** | 31 | AF1 (Funcionalidade), AF8 (Cancelamento), AF9 (Prevenção de Erros). |
| **Comunicação (CO)** | 23 | CO3 (Affordance/Dicas), CO2 (Feedback adequado), CO5 (Confiabilidade). |
| **Acessibilidade (AC)** | 17 | AC4 (Contraste de cor), AC1 (Texto alternativo), AC6 (Configurações). |
| **Navegação (NA)** | 10 | NA2 (Caminhos de navegação), NA4 (Migalhas de pão), NA3 (Continuidade). |
| **Particularidades do Usuário (PU)** | 6 | PU2 (Personalização), PU4 (Redução do esforço cognitivo). |
| **Privacidade e Segurança (PS)** | 5 | PS1 (Privacidade de dados pessoais), PS2 (Responsabilidade LGPD). |
| **Particularidades do Disp. (PD)** | 4 | PD4 (Densidade informacional), PD5 (Áreas clicáveis maiores). |
| **TOTAL GERAL** | **133** | |

---

## 3. Síntese dos Principais Problemas Encontrados

Em vez de listar individualmente as 133 violações, agrupamos os problemas mais críticos e recorrentes apontados pelos avaliadores que demandam correção prioritária:

### A. Acessibilidade e Formatação Visual (Crítico para o público TEA)
* **Baixo Contraste (FM11/AC4):** Campos de input, barras de pesquisa, placeholders e botões secundários possuem contraste baixíssimo (tons de cinza/bege sobre fundo bege). Dificulta severamente o uso por pessoas com baixa visão ou hipersensibilidade visual.
* **Ausência de Ajustes de Acessibilidade (AC5/AC6/AC8):** O sistema não possui configurações de acessibilidade essenciais, como modo de alto contraste, redimensionamento de fonte ou controle de animações.
* **Falta de Textos Alternativos (AC1):** Ícones interativos (balões de comentários, bandeiras de denúncia) estão sem rótulos (aria-labels), sendo lidos apenas como "botão" por leitores de tela.

### B. Prevenção de Erros e Perda de Dados (AF4/AF8/AF9)
* **Ausência de Rascunhos e Confirmação de Saída:** Ao clicar em "Cancelar" ou fechar modais acidentalmente (como na "Nova Postagem" ou "Criar Comunidade"), todo o texto digitado é perdido sem nenhum aviso prévio.
* **Validação Inexistente:** O sistema permite submeter postagens vazias e permite o cadastro de comunidades sem verificação prévia de campos obrigatórios preenchidos.
* **Ações Irreversíveis (Moderação):** Moderadores podem "Remover postagem" ou banir conviventes em um único clique acidental, sem modais de confirmação.

### C. Navegação, Busca e Filtragem (NA2/FM3/FM4)
* **Navegação Limitada no Feed:** A tela principal (Dashboard) não possui campo de busca global, abas ("Recentes/Populares") nem a possibilidade de ordenar postagens. Quando houver muitas comunidades, o usuário não conseguirá encontrar conteúdos.
* **Falta de Migalhas de Pão (NA4):** Usuários perdem a localização de onde estão no sistema ("Início > Comunidades > Nome da Comunidade").

### D. Segurança, Privacidade e LGPD (PS1/PS2)
* **Falta de Clareza na Visibilidade:** O formulário de criar comunidade não deixa claro se a comunidade será pública, privada ou restrita, nem quem terá acesso às postagens.
* **Consentimento de Dados Automático:** Os termos de aceite de privacidade são sutis no rodapé e automáticos ao fazer login, o que enfraquece o consentimento informado da LGPD, especialmente lidando com dados sensíveis de saúde/neurodivergência.
* **Denúncias:** Não é informado se as denúncias de moderação são anônimas, causando potencial medo de represália nos conviventes.

### E. Feedbacks de Interface (CO2/CO3)
* **Comandos de Texto "Crus":** Ações de Negrito e Itálico inserem sintaxe Markdown (ex: `**texto**`) visível ao usuário no Feed, quebrando a confiabilidade e imersão.
* **Botões Inoperantes/Mudos:** Botões que deveriam dar feedback imediato ("Participar" de comunidade, enviar postagem, favoritar) falham em avisar o estado do sistema (sem mensagens de "Postagem criada com sucesso!" ou modais de espera).

---

## 4. Contribuição por Avaliador

O trabalho de inspeção foi dividido de forma a garantir que diferentes bagagens identificassem problemas variados nas mesmas telas:

* **Aaron:** 30 violações (Foco forte em ausência de estados de navegação, segurança de denúncias e acessibilidade por teclado/leitor de tela).
* **Fernando Yuri:** 15 violações (Foco na falha do renderizador de texto, ausência de feedback na listagem e regras de privacidade).
* **João Pedro Dantas:** 34 violações (Foco aprofundado na quebra de contraste [WCAG], leiturabilidade, controle de fluxo de moderação e breadcrumbs).
* **Lorrany Fagundes:** 18 violações (Foco em particularidades do usuário, personalização, ausência de guias condutores e restrições temporais de dados).
* **Manoel Pinto Junior:** 6 violações (Foco direto em quebras de continuidade, botões "fantasmas" inoperantes e atalhos de teclado).
* **Ramon Couto:** 30 violações (Foco na falta de busca estruturada, densidade informacional de imagens/banners e prevenção massiva de erros nos formulários).

---

## 5. Recomendações e Próximos Passos
1. **Curto Prazo (Hotfixes):** Ajustar imediatamente a paleta de cores para atingir o contraste mínimo da WCAG (4.5:1), acionar o renderizador de texto rico (WYSIWYG/Markdown) nos cards de visualização e implementar alertas de confirmação (modais) em todos os botões de "Cancelar" e "Excluir".
2. **Médio Prazo (Sprints seguintes):** Desenvolver um mecanismo global de busca, ordenação e filtragem de conteúdo para suportar o crescimento das comunidades, além de adicionar políticas explícitas de visibilidade (LGPD/Privacidade) nos formulários de criação.
3. **Longo Prazo:** Implementar um painel robusto de acessibilidade no menu principal (modo alto contraste, ajustes de leitura para público TEA) e refinar o fluxo para moderação de conteúdo (denúncias anônimas e travas de ações destrutivas).
