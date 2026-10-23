# Sistema Escolar — Projeto de 1º ano

Sistema básico de cadastros com Python, Flask, MySQL, HTML e CSS manual, inspirado na organização do Projeto Guiado do 1º ano.

## Tabelas utilizadas
Somente tabelas que não possuem declarações de chave estrangeira (FK) no SQL fornecido:
- `usuarios`
- `permissoes`
- `disciplinas`
- `turmas`

Não são utilizadas `usuario_permissao`, `alunos`, `professores`, `aluno_turma`, `professor_disciplina`, `notas`, `frequencia`, `materiais`, `recomendacoes` ou `atividades`.

## Preparação
1. Abra a pasta no VS Code.
2. Crie e ative o ambiente virtual:
   - Windows: `python -m venv venv` e `venv\\Scripts\\activate`
   - Linux/macOS: `python3 -m venv venv` e `source venv/bin/activate`
3. Instale as dependências: `pip install -r requirements.txt`
4. No arquivo `config.py`, coloque a senha correta do seu MySQL.
5. Execute o SQL original para criar o banco `sistema_escolar` e suas tabelas. Se já criou o banco, não precisa recriá-lo.
6. Inicie: `python app.py`
7. Acesse `http://127.0.0.1:5000`.

## Funcionalidades
- Listar, cadastrar, editar e excluir registros das quatro tabelas selecionadas.
- Layout responsivo com CSS próprio, sem Bootstrap, para seguir a etapa inicial do documento de exemplo.
- A senha de usuário é armazenada como hash quando cadastrada ou alterada; a coluna de senha não é exibida na listagem.

## Observações
- O projeto pressupõe que as tabelas do banco já existem com a estrutura do arquivo SQL enviado.
- Em `usuarios`, o e-mail deve ser único. Em `permissoes`, o nome deve ser único.
- Para um projeto real, altere `app.secret_key` para uma chave privada e não publique credenciais do banco.
