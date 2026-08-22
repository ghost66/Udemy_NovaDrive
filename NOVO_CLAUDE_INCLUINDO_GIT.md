#  Instruções do Projeto para o Claude Code

## Sobre o Projeto

Painel (dashboard) somente leitura sobre o banco  PostgreSQL de uma rede de concessionárias

## Regras não-negociáveis

- Acesso ao banco é **somente leitura**. Nunca escrever, gerar ou sugerir código que insira, atualize ou apague dados.
- Banco: **PostgreSQL**. Driver: `psycopg2` via SQLAlchemy.
- Interface obrigatória com **Python + Streamlit**. Plotly ou Altair para gráficos.
- Credenciais de banco **nunca** no código. Usar variáveis de ambiente
`.env`  ou `st.secrets`.
-Sempre filtrar por período **na propria query**, nunca carregar a tabela inteira para filtrar depois.
- Cache (`st.cache_data`) : ~1 min para agregações simples: 15~20 min para consultas com muitos joins.
- Sem autenticação/login nesta versão (uso interno).

### Como trabalhar neste repositório

1. Antes de imprimir , leia a spec em `specs/<funcionalidade>`
(requirements.md, desifn.md, tasks.md) e o diagrama em `docs/diagrama-banco-dados.png`. Confirme nomes exatos de tabelas, colunas, tipos e chaves antes de escrever qualquer SQL.
2. Não implemente nada fora da spec. Se algo estiver ambiguo ou uma coluna nao existir no diagrama, pare e pergunte, não invente.
3. Siga a ordem numérica das pastas em `specs/`  (acesso a a dados é a fundação das demais).
4. Código fonte em `src/` , Testes em `tests/` . Crie `requirements.txt` com as dependências usadas.

## Git e GitHub CLI (gh)

Este projeto usa o `gh` (GitHub CLI) para todas as interações com o GitHub. 
Antes de qualquer operação abaixo, verifique se o `gh` está autenticado:

```
gh auth status
```

Se não estiver, pare e me avise — não tente autenticar sozinho.

### Commits

- Rode `git status` antes de iniciar qualquer trabalho para checar o estado atual
- Crie commits em pontos lógicos e funcionais, nunca deixe mudanças grandes acumulando
- Mensagens de commit curtas, descrevendo o "porquê" e não só o "o quê"
- Antes de commitar, rode `git diff --staged` e confirme que **nenhum segredo** 
  (`.env`, string de conexão, senha do banco) está incluído
- NUNCA adicione `.env` a um commit, mesmo que peçam explicitamente — avise antes

### Repositório remoto

- Se o repositório remoto ainda não existir, crie com:
  ```
  gh repo create <nome-do-repo> --private --source=. --remote=origin
  ```
- Use `--private` por padrão neste projeto (dados de concessionárias), a menos 
  que eu peça explicitamente `--public`
- Após criar/commitar, faça push com `git push -u origin <branch>` só quando eu pedir

### Branches e Pull Requests

- Para novas funcionalidades descritas em `specs/`, crie uma branch dedicada:
  ```
  git checkout -b feature/<nome-da-spec>
  ```
- Ao concluir a funcionalidade e os testes, abra um PR com:
  ```
  gh pr create --title "<título curto>" --body "<resumo do que foi feito e testes realizados>"
  ```
- Não faça merge do PR sozinho — apenas crie e me avise o link para revisão
- Não use `gh pr merge`, `git push --force` ou `git reset --hard` sem confirmação 
  explícita minha

### Issues (opcional, se formos usar)

- Se eu pedir para abrir uma issue para um bug ou tarefa pendente, use:
  ```
  gh issue create --title "<título>" --body "<descrição>"
  ```
- Ao corrigir algo relacionado a uma issue, referencie o número no commit 
  (ex: `Corrige carregamento de filtro de período (#12)`)

## O que NÃO fazer

- Não commitar arquivos temporários, caches, artefatos de build, ou o `.env`
- Não fazer commit, push, PR ou merge automaticamente sem pedido explícito
- Não deletar arquivos fora de `specs/`, `src/`, `tests/` ou pastas de 
  build/cache sem confirmação
- Não rodar comandos `gh` ou `git` destrutivos (force push, delete de branch 
  remota, merge) sem autorização explícita
