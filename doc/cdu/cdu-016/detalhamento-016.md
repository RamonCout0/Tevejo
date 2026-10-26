# CDU016. Gerenciar Curadores

- **Ator principal**: Administrador  
- **Atores secundários**: Curador  
- **Resumo**: O Administrador pode adicionar, alterar ou remover Curadores da plataforma TeVejo, permitindo o gerenciamento do acesso e das permissões de curadoria.  
- **Pré-condição**: Ser Administrador autenticado no sistema.  
- **Pós-condição**: Determinado curador é adicionado, alterado ou removido do sistema.  

---

## Fluxo Principal - Adicionar Curador
| **Ações do ator** | **Ações do sistema** |
| :----------------- | :----------------- |
| 1 - O Administrador acessa a área de "Gerenciar Curadores" | |  
| | 2 - O sistema exibe a lista de curadores cadastrados e as opções de “Adicionar Curador”, “Editar” e “Remover” |
| 3 - O Administrador seleciona a opção “Adicionar Curador” | |  
| | 4 - O sistema exibe um formulário de cadastro contendo: nome*, e-mail*, senha temporária*, e status (ativo/inativo) – *campos obrigatórios |
| 5 - O Administrador preenche o formulário e confirma o cadastro | |  
| | 6 - O sistema valida as informações, cria o novo usuário com perfil de Curador e exibe mensagem de sucesso “Curador cadastrado com sucesso” |

---

## Fluxo Alternativo I – Edição de dados de um curador
| **Ações do ator** | **Ações do sistema** |
| :----------------- | :----------------- |
| 3.1 - O Administrador seleciona a opção “Editar” em um curador existente | |  
| | 3.2 - O sistema exibe o formulário de edição preenchido com os dados atuais do curador |
| 3.3 - O Administrador atualiza as informações desejadas e confirma a alteração | |  
| | 3.4 - O sistema valida as informações e exibe mensagem “Dados do curador atualizados com sucesso” |

---

## Fluxo Alternativo II – Remoção de um curador
| **Ações do ator** | **Ações do sistema** |
| :----------------- | :----------------- |
| 3.1 - O Administrador seleciona a opção “Remover” de um curador | |  
| | 3.2 - O sistema solicita uma confirmação da ação (“Deseja realmente remover este curador?”) |
| 3.3 - O Administrador confirma a remoção | |  
| | 3.4 - O sistema remove o curador e apresenta mensagem “Curador removido com sucesso” |

---


## Diagrama de Interação (Sequência ou Comunicação)

> Substituir pela imagem correspondente...

---

## Diagrama de Classes de Projeto

> Substituir pela imagem contendo as classes (modelo, visão e templates) que implementam o respectivo CDU...
