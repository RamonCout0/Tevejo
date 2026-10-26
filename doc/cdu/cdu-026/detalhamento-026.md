# CDU026. Guia Condutor

- **Autor**: Aaron Goldberg
- **Ator principal**: Convivente
- **Atores secundários**: Curador
- **Resumo**: Esse caso de uso descreve o guia condutor do TeVejo: no primeiro acesso, o sistema convida o usuário a fazer um tour guiado pelo site. O guia, apresentado pelo personagem **Gui**, escurece a tela, destaca cada área com uma seta e explica para que ela serve, incluindo o passo a passo de como criar uma comunidade. O objetivo é que pessoas com pouca familiaridade com tecnologia (principalmente as mais velhas) consigam usar a plataforma com autonomia.
- **Pré-condição**: O usuário deve estar autenticado e ter aceitado o Termo de Consentimento (CDU019). Para o convite automático, o usuário ainda não pode ter respondido ao convite do guia.
- **Pós-Condição**: O sistema registra que o usuário respondeu ao convite (aceitando ou recusando) e não volta a exibi-lo. O guia continua disponível a qualquer momento pelo botão de ajuda (CDU027).

## Fluxo Principal - Aceitar e concluir o guia
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 1 - O usuário entra no TeVejo pela primeira vez. | |
| | 2 - O sistema exibe o convite: "Quer que eu te mostre o site?", com as opções "Sim, me mostra!" e "Agora não". |
| 3 - O usuário escolhe "Sim, me mostra!". | |
| | 4 - O sistema registra a resposta ao convite e inicia o guia, escurecendo a tela e mostrando o balão de boas-vindas do Gui. |
| 5 - O usuário toca em "Próximo". | |
| | 6 - O sistema destaca a próxima área (Discussões públicas, Conteúdos, Comunidades, busca de comunidades, Encontros, perfil e botão de ajuda), com seta e explicação, abrindo a tela correspondente quando necessário. |
| 7 - O usuário avança até o último passo e toca em "Concluir". | |
| | 8 - O sistema encerra o guia e devolve a tela ao normal. |

## Fluxo Alternativo I - Recusar o convite
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 1.1 - No convite, o usuário escolhe "Agora não". | |
| | 1.2 - O sistema registra a resposta ao convite, fecha o convite e destaca o botão de ajuda no canto inferior direito com a mensagem: "Tudo bem! Quando quiser, é só tocar aqui." |

## Fluxo Alternativo II - Passo a passo de criação de comunidade (Convivente)
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 2.1 - Durante o guia, o convivente chega ao passo "Como criar uma comunidade". | |
| | 2.2 - O sistema abre a tela de criação de comunidade e destaca, em sequência: nome e descrição, escolha da categoria, ícone e banner (com recorte) e o botão "Criar comunidade", explicando que quem cria vira moderador(a). |
| | 2.3 - O sistema não cria nenhuma comunidade durante o guia; apenas demonstra os campos. |

## Fluxo Alternativo III - Guia para curador
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 3.1 - Um curador inicia o guia. | |
| | 3.2 - O sistema substitui os passos de criação de comunidade pelo passo "Publique conteúdos", destacando o botão "Publicar conteúdo" na tela de Conteúdos educacionais. |

## Fluxo Alternativo IV - Sair do guia antes do fim
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 4.1 - O usuário toca em "Pular guia" ou pressiona a tecla Esc. | |
| | 4.2 - O sistema encerra o guia imediatamente, sem perder o que o usuário estava fazendo. |

## Fluxo Alternativo V - Refazer o guia
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 5.1 - O usuário toca no botão de ajuda e escolhe "Fazer o guia" (ou no botão "Fazer o guia" da Central de ajuda). | |
| | 5.2 - O sistema inicia o guia do primeiro passo, mesmo que o convite já tenha sido respondido. |
