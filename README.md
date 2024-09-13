# API_Biblioteca

## Situação do Projeto
![Status](https://img.shields.io/badge/status-Em%20Progresso-yellow)

![Etapa](https://img.shields.io/badge/Etapa-N1-Green)![Etapa](https://img.shields.io/badge/N2-000000)![Etapa](https://img.shields.io/badge/N3-000000)

## Instruções da Avaliação:
Você deverá implementar:
### Tabela no banco de dados (o initdb deverá criar a tabela de usuários):
- A tabela de usuários deverá ter os seguintes campos: id, login (deverá ser
o e-mail), senha, nome real, data de criação do usuário, status
(ativo/bloqueado), data de última atualização do usuário.

### Criar endpoints para fazer as operações CRUD na tabela:
- Ao criar o usuário, a senha deverá ser encriptada utilizando o método
algum método de sentido único (não deve ser possível desencriptar a
senha);
- NÃO deve ser permitido criar usuários com mesmo login. Ao cadastrar,
deverá ocorrer validação dos dados. Esta validação pode ocorrer no
momento de envio dos dados, não é necessário fazer validação ao sair do
campo;
- Ao cadastrar o usuário, deverá ocorrer validação do login para garantir que
o login escolhido é um e-mail;
- Ao criar o usuário, a data de criação do usuário deve ser preenchida com
a data atual;
- Ao efetuar qualquer alteração no usuário, a data da última atualização
deverá ser preenchida com a data da alteração do registro (a data de
criação deverá permanecer inalterada);
- Usuários NÃO poderão ser excluídos, somente bloqueados;

### Criar template para gerenciamento do usuário (as operações do CRUD acima
deverão ser feitas por interface gráfica):
- Lembre-se de que a “deleção” somente irá marcar o usuário como
bloqueado.

### Criar um template para a tela de login, para que o usuário acesse o sistema. Esta
deve estar em um endpoint /login, e deve estar acessível na barra de menus
superior do serviço:
- Se o usuário estiver bloqueado, não deve ser permitido o login. Deve ser
apresentada uma mensagem na tela informando o usuário do fato;
- Se o usuário for autenticado com sucesso (login e senha OK), o usuário
deve ser redirecionado à uma página inicial (à sua escolha);
- Por enquanto, os demais endpoints poderão ser acessados diretamente,
não protegeremos rotas neste ponto do trabalho;

### Entregar o trabalho em um repositório do GitHub/GitLab para avaliação. O
arquivo README.md deve conter todas as instruções necessárias para rodar o
sistema (instalação de pacotes, configurações especiais, etc).

## Guia de Instalação:
- !Apresentar os Pontos necessários!

<div align="center">
<h3 align="center">Autor</h3>
<table>
  <tr>
    <td align="center"><a href="https://github.com/AoiteFoca"><img loading="lazy" src="https://avatars.githubusercontent.com/u/141975272?v=4" width="115"><br><sub>Nathan Cielusinski</sub></a></td>
  </tr>
</table>