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

