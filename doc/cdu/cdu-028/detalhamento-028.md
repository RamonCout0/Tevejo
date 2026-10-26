# CDU028. Visualizar Página Inicial

- **Autor**: Ramon Couto
- **Ator principal**: Usuário (visitante, convivente ou curador)
- **Atores secundários**: Não existe.
- **Resumo**: Esse caso de uso descreve a página inicial do TeVejo. Ela dá as boas-vindas ao usuário e pergunta o que ele está procurando, mostrando cartões com os caminhos da plataforma (aprender sobre o TEA, conversar em comunidades, ver as discussões, participar de encontros e tirar dúvidas). Para o visitante, a página também convida a criar uma conta ou entrar.
- **Pré-condição**: Nenhuma. A página inicial é pública. Um convivente que ainda não aceitou o termo vigente é levado antes ao termo de consentimento (CDU019).
- **Pós-Condição**: O usuário é levado à tela do cartão que escolheu.

## Fluxo Principal - Escolher o que procura
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 1 - O usuário acessa o endereço do TeVejo ou toca no logotipo ou em "Início" no menu lateral. | |
| | 2 - O sistema exibe a página inicial com a saudação "Bem-vindo(a), visitante!" e a pergunta "O que você está procurando?". |
| | 3 - O sistema exibe os cartões: "Aprender sobre o TEA" (Conteúdos), "Conversar com quem vive o mesmo" (Comunidades), "Ver o que estão conversando" (Discussões públicas), "Participar de encontros" (Encontros) e "Tirar uma dúvida sobre o site" (Ajuda). |
| 4 - O usuário toca em um cartão. | |
| | 5 - O sistema abre a tela correspondente ao cartão. |

## Fluxo Alternativo I - Usuário autenticado
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| | 2.1 - O sistema troca a saudação por "Olá, <primeiro nome>!" e não exibe os botões "Criar conta" e "Entrar". |
| | 3.1 - Para o convivente, o sistema troca o cartão de cadastro por "Criar minha comunidade" (CDU008). |

## Fluxo Alternativo II - Visitante quer participar
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 4.1 - O visitante toca em "Criar conta" (no topo ou no cartão "Quero fazer parte"). | |
| | 4.2 - O sistema abre o formulário de autocadastro (CDU002). |
| 4.3 - O visitante toca em "Entrar". | |
| | 4.4 - O sistema abre a tela de login (CDU001). |

## Fluxo Alternativo III - Cartão que exige conta
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 4.5 - O visitante toca em "Participar de encontros". | |
| | 4.6 - Como a lista de encontros exige login, o sistema leva o visitante à tela de login (CDU001). O cartão já avisa "Entre para ver" antes do toque. |

## Fluxo Alternativo IV - Endereço inexistente
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 1.1 - O usuário acessa um endereço que não existe no TeVejo. | |
| | 1.2 - O sistema redireciona para a página inicial (passo 2 do fluxo principal). |
