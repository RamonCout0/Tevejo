# CDU027. Consultar Ajuda e Perguntas Frequentes

- **Autor**: Aaron Goldberg
- **Ator principal**: Usuário (visitante, convivente ou curador)
- **Atores secundários**: Não existe.
- **Resumo**: Esse caso de uso descreve como o usuário obtém ajuda no TeVejo. Um botão fixo no canto inferior direito, com o personagem Gui, dá acesso ao guia condutor (CDU026) e à Central de ajuda, uma página de perguntas frequentes com respostas curtas e ilustrações vetoriais que mostram como usar a plataforma.
- **Pré-condição**: Nenhuma. A Central de ajuda é pública; a opção "Fazer o guia" aparece apenas para usuários autenticados.
- **Pós-Condição**: O sistema exibe a resposta escolhida pelo usuário, com ilustração e, quando houver, um atalho para a tela relacionada.

## Fluxo Principal - Consultar uma dúvida
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 1 - O usuário toca no botão de ajuda (canto inferior direito). | |
| | 2 - O sistema abre o menu de ajuda com as opções "Fazer o guia" e "Dúvidas frequentes". |
| 3 - O usuário escolhe "Dúvidas frequentes". | |
| | 4 - O sistema abre a Central de ajuda com as perguntas agrupadas em: Primeiros passos, Conteúdos e encontros, Escrevendo e perfil e Segurança e convivência. |
| 5 - O usuário toca em uma pergunta. | |
| | 6 - O sistema expande a resposta, mostrando a ilustração do assunto e um botão de atalho (ex.: "Criar comunidade", "Ver encontros"). |

## Fluxo Alternativo I - Buscar uma dúvida
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 1.1 - O usuário digita uma palavra no campo de busca (ex.: "foto"). | |
| | 1.2 - O sistema filtra as perguntas e respostas que contêm a palavra, sem diferenciar acentos e maiúsculas. |

## Fluxo Alternativo II - Nenhuma resposta encontrada
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 2.1 - O usuário busca um termo que não aparece em nenhuma pergunta. | |
| | 2.2 - O sistema exibe a mensagem: "Não achei nada com '<termo>'. Tente outra palavra ou faça o guia passo a passo." |

## Fluxo Alternativo III - Iniciar o guia pela ajuda
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 3.1 - O usuário autenticado escolhe "Fazer o guia" no menu de ajuda ou na Central de ajuda. | |
| | 3.2 - O sistema inicia o guia condutor (CDU026, Fluxo Alternativo V). |

## Fluxo Alternativo IV - Acesso pelo menu
| Ações do ator | Ações do sistema |
| :-----------------: | :-----------------: |
| 4.1 - O usuário toca em "Ajuda e dúvidas" no menu lateral. | |
| | 4.2 - O sistema abre a Central de ajuda (passo 4 do fluxo principal). |
