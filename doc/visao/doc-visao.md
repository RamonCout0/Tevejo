# Documento de Visão

## Histórico de Revisões

| Data | Versão | Descrição | Autores |
| :--: | :----: | :-------: | :-----: |
| 29/09/25 | 1 | Versão inicial | Aaron, Fernando, Lorrany, Ramon |
| 04/10/25 | 1.1 | Alterações em Requisos funcionais, usuários, regras de negócios | Aaron, Fernando, Lorrany, Ramon |
| 29/03/26 | 1.2 | Alterações em Requisos funcionais, usuários, regras de negócios | Aaron, Fernando, Lorrany, Ramon, João Pedro, Wilson |
<!-- | - | - | - |  - | !-->

## 1. Visão Geral do Sistema Proposto

O Tevejo será uma plataforma web para acolher, informar e
conectar pessoas que convivem com autistas.
- Informatizar: disponibilizar informações confiáveis sobre TEA
(Transtorno do Espectro Autista).
- Apoiar: oferecer um espaço seguro para desabafos, trocas de
experiências e suporte emocional.
- Conscientizar: reduzir preconceitos e julgamentos, promovendo
empatia.


## 2. Descrição do Problema
| | |
| :-: | :-: |
| **Problema** |  Falta de apoio para pessoas que convivem com autistas. As pessoas que convivem com autistas podem sofrer com a falta de apoio, orientação e espaço seguro para compartilhar experiências. |
| **Afeta** | Pessoas que convivem com autistas. |  
| **Impacta** | A falta de apoio a quem convive com autistas gera sobrecarga emocional, dificuldades financeiras e isolamento, além de prejudicar a inclusão e reforçar preconceitos. |
| **Solução** | O TeVejo é uma plataforma web que serve como rede de apoio — Um lugar seguro para troca de experiências e informações — e contará com conteúdos verificados por curadores. | 

## 3. Descrição dos Usuários 

| Usuário | Descrição | Responsabilidades |
| :-----: | :-------: | :--------------: |
| Conviventes | Pessoas que convivem com autistas, podem ser: familiares, amigos, educadores etc. | Usuário com acesso às funcionalidades básicas do sistema - conteúdo educacional e comunidades.|
| Curador | Profissional da Psicologia | Usuário responsável por realizar postagem e edição dos conteúdos educacionais. |
| Moderador |  Criador de uma comunidade ou qualquer pessoa convidada pelo criador que se comprometa com a responsabilidade de moderação. | Usuário que revisa postagens e denúncias em uma comunidade, tendo poder de excluir postagens e aprovar denúncias, permitindo a exclusão da postagem por parte do sistema. Além de conseguir restringir ou banir conviventes de uma comunidade. |
| Administrador | Usuário de maior hierarquia na plataforma. | Usuário que pode cadastrar e gerenciar conviventes, moderadores, curadores e os outros administradores. Além de poder gerir conteúdos educacionais e comunidades já criados.


## 4. Descrição do Ambiente dos Usuários

| Usuário | Ambiente operacional |
| :-----: | :------------------: |
| Qualquer usuário | Celular, computadores, tablets, notebooks.|


## 5. Principais Necessidades dos Usuários



1. **Conviventes**
   -Conteúdos educacionais e Comunidade com ambiente acolhedor para possibilitar conversa, troca de experiências e informações sobre como lidar com as mais diversas características do TEA.

2. **Curador**
   -Interface que permita a postagem e edição de conteúdos educacionais. 
   
3. **Moderador**
   -Disponibilização de uma interface que forneça autorização para analisar denuncias e postagens em uma comunidade, além de restringir e banir usuários que violem as diretrizes de uma comunidade. Também uma interface para criação de encontros em uma comunidade.
   
4. **Administrador**
   -Interface que permita gerência de comunidades e conteúdos educacionais, cadastros de outros usuários como conviventes, administradores e curadores.

## 6. Alternativas Concorrentes

1. **CearáTEAcolhe**
   - Apoio psicossocial gratuito;
   - Integração com serviços públicos;
1. **Tismoo**
   - Medicina personalizada baseada em genética;
   - Centro de referência em autismo no Brasil;
1. **ianacare**
   - Organizador de cuidadores familiares;
   - Suporte emocional e recursos personalizados;
1. **Caregiver Action Network (CAN)**
   - Advocacia e políticas públicas;
   - Rede de apoio e recursos educacionais;


## 7. Regras de Negócio

| ID  | Regra | Descrição |
| :-: | :---: | :-------: |
| RN01 | Conteúdo revisado | Todo conteúdo educativo deve ter sido previamente verificado pelos curadores da plataforma antes da postagem. |
| RN02 | Moderação obrigatória| Toda postagem em comunidades está sujeito a análise de moderadores. Afim evitar discursos preconceituosos, discurso de ódio, fake news etc.|
| RN03 | Privacidade do usuário | Nenhuma informação sensível de usuários (como relatos nas comunidades) pode ser compartilhada com terceiros sem consentimento explícito do titular. |
| RN04 | Acesso limitado para usuários não cadastrados |Usuários não cadastrados não poderão interagir nas comunidades, apenas visualizar. |
| RN05 | Denúncia de conteúdo | Todo conteúdo denunciado deve ser automaticamente ocultado até ser feita uma análise por um moderador. |
| RN06 | Responsabilidade dos encontros presenciais | A plataforma não se responsabiliza por encontros organizados pelos usuários. |

## 8. Requisitos Funcionais

| Código | Nome | Descrição | Prioridade |
| :----: | :--: | :-------: | :--------: |
| RF01 | Autenticação | O site deve permitir login apenas com conta já registrada | Alta|
| RF02 | Posts em formato de Fórum | O site deve permitir a postagem de discussões, que deve possibilitar a abordagem de dúvidas e relatos pelos usuários, permitindo comentários, curtidas e denúncias de conteúdo inadequado. | Alta |
| RF03 | Conteúdo Educacional | A plataforma deve possibilizar o gereciamento de conteúdo educacional feito pelos curadores, permitindo inserção ou remoção de conteúdos. | Alta |
| RF04 | Organização dos conteúdos | Os conteúdos serão organizados por tags, possibilitando que os usuários filtrem e naveguem pelos conteúdos com facilidade. | Média |
| RF05 | Criação de Comunidades | O site deve possibilitar que os usuários, além de poderem entrar nos comunidades existentes, possam criar suas próprias comunidades. | Média |
| RF06 | Agendamento dos Encontros presenciais |O site deve conter um espaço para Encontros (presenciais), com opções de 'criação de encontro'e visualização dos encontros agendados/marcados ou já disponíveis. Os encontros também podem ser denunciáveis.| Média |
| RF07 | Gerenciamento de Curadoria | A plataforma deve gerenciar o cadastro dos curadores, tarefa realizada pelos adminstradores da plataforma | Alta |
| RF08 | Gerenciamento de Administradores | A plataforma deve gerenciar o cadastro dos Administradores | Alta |
| RF09 | Gerenciamento de Dados pessoais | A plataforma deve permitir a alteração dos dados pessoais dos conviventes | Alta |

> **Prioridade**: alta, média ou baixa

## 9. Requisitos Não-funcionais

| Código | Nome | Descrição | Categoria | Classificação |
| :----: | :--: | :-------: | :-------: | :-----------: |
| RNF01 | Segurança da autenticação | O sistema deve utilizar protocolos seguros (ex.: HTTPS, criptografia de senhas) para proteger os dados de login dos usuários. | Segurança | Obrigatório |
| RNF02 | Disponibilidade da Platarforma | A plataforma deve estar disponível 99% do tempo, com mecanismos de recuperação em caso de falhas. | Confiabilidade | Obrigatório |
| RNF03 | Escalabilidade da plataforma | O sistema deve suportar crescimento no número de categorias, grupos, garantindo boa performance mesmo com aumento de usuários ativos.| Desempenho | Desejável |
| RNF04 | Confiabilidade dos encontros presenciais | O módulo de agendamento deve evitar conflitos de horário e enviar notificações de confirmação e lembrete aos usuários. | Confiabilidade | Desejável |
| RNF05 | Privacidade e confidencialidade | Todos os dados dos usuários, incluindo interações nas comunidades, devem ser tratados de acordo com a LGPD, garantindo confidencialidade e anonimato quando solicitado. | Segurança/Confiabilidade | Obrigatório |

> **Categoria**: usabilidade, confiabilidade, performance, suportabilidade, restrição de projeto, implementação, interface e requisito físico - segundo classificação [FURP+](https://pt.wikipedia.org/wiki/FURPS).

> **Classificação**: desejável ou obrigatório.