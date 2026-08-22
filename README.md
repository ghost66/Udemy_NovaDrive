# Dashboard de Concessionárias

Painel somente de leitura sobre o banco de dados PostgreSQL de uma rede de concessionárias, construído em Python + Streamlit. Projeto utilizando técnicas de Spec-Driven Development (SDD) com Claude Code.

## Status

Todas as specs planejadas estão implementadas e testadas:

| Spec | Descrição | Status |
|---|---|---|
| `01-acesso-dados` | Camada base de conexão/consulta somente leitura | Concluída |
| `02-dashboard-executivo` | Visão executiva: faturamento, evolução, comparação entre concessionárias/estado/cidade, projeção do mês | Concluída |
| `03-analise-comercial` | Ranking de vendedores, modelos mais vendidos, desconto médio, comparação comercial entre concessionárias | Concluída |

## Tecnologias

- **Python 3.12+**
- **Streamlit** — interface
- **SQLAlchemy + psycopg2** — acesso ao PostgreSQL
- **Plotly** — gráficos
- **pandas** — manipulação dos resultados das queries
- **python-dotenv** — leitura de credenciais do `.env`
- **pytest** — testes automatizados

## Estrutura

```
CLAUDE.md              regras não-negociáveis do projeto (leitura obrigatória)
specs/<pasta>/          requirements.md, design.md, tasks.md — uma pasta por spec
docs/                   diagrama-banco-dados.png e outros artefatos de referência
prompts.md              prompts prontos usados para implementar cada spec

src/
  database.py           engine SQLAlchemy/psycopg2 (somente leitura) + execução segura de query
  queries.py             todas as consultas SQL parametrizadas por período, cacheadas
  projecao.py            cálculo de projeção (run-rate) do dashboard executivo
  app.py                 página Streamlit principal (Dashboard Executivo)
  pages/
    1_Analise_Comercial.py  segunda página Streamlit (Análise Comercial)

tests/                  testes automatizados (pytest) — não dependem de banco real
requirements.txt        dependências do projeto
.env                    credenciais do banco (não versionado, ver abaixo)
```

## Regras não-negociáveis

- Acesso ao banco é **somente leitura** — nunca há SQL de escrita (garantido por validação em `database.py` e testado em `tests/`).
- Toda consulta que toca `vendas` filtra por período diretamente no SQL.
- Cache (`st.cache_data`) com TTL de 1 min para agregações simples e 15 min para consultas com múltiplos joins.
- Credenciais nunca ficam no código: são lidas de `.env` (via `python-dotenv`) ou `st.secrets`.

Detalhes completos em [CLAUDE.md](CLAUDE.md).

## Como rodar

### 1. Pré-requisitos
- Python 3.12+
- Acesso de rede ao PostgreSQL da rede de concessionárias, com um usuário **somente leitura**

### 2. Criar ambiente virtual e instalar dependências

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
```

### 3. Configurar credenciais

Crie um arquivo `.env` na raiz do projeto (já está no `.gitignore`, não é versionado):

```
DB_HOSTS = <host_do_postgres>
DB_PORT = 5432
DB_NAME = novadrive
DB_USER = <usuario_somente_leitura>
DB_PASSWORD = <senha>
```

Alternativamente, use `st.secrets` criando `.streamlit/secrets.toml` (sintaxe TOML, valores entre aspas):

```toml
DB_HOSTS = "<host_do_postgres>"
DB_PORT = "5432"
DB_NAME = "novadrive"
DB_USER = "<usuario_somente_leitura>"
DB_PASSWORD = "<senha>"
```

### 4. Rodar o aplicativo

```bash
streamlit run src/app.py
```

Abre em `http://localhost:8501`. O menu lateral do Streamlit lista dois links: **app** (`app.py`, o Dashboard Executivo) e **Analise Comercial** (`pages/1_Analise_Comercial.py`).

### 5. Rodar os testes

```bash
pytest tests/ -v
```

Os testes validam que nenhuma consulta gera SQL de escrita, que os filtros de período estão presentes, e a lógica de projeção — sem depender de conexão real com o banco.

## Solução de problemas

- **`connection timed out`** ao conectar: normalmente é rede/firewall — confirme se é necessária VPN ou liberação de IP para alcançar `DB_HOSTS:DB_PORT` a partir da sua máquina.
- **`no pg_hba.conf entry for host "..."`**: o Postgres recebeu a conexão mas recusou por regra de acesso. O administrador do banco precisa liberar o IP de origem no `pg_hba.conf` para o usuário/banco em uso e recarregar a configuração (`SELECT pg_reload_conf();`).
- **Mensagem genérica "Não foi possível conectar ao banco de dados"** na tela: é o erro amigável padrão de `database.py` — os detalhes reais (sem credenciais) só aparecem no terminal onde o `streamlit run` está rodando.
- **Aviso "No secrets found"**: só ocorre se `st.secrets` for acessado sem existir `.streamlit/secrets.toml`; o código atual evita isso automaticamente quando só o `.env` é usado.

## Como implementar novas specs

Abra o Claude Code na raiz desta pasta e use os prompts de `prompts.md`, um por spec, na ordem numérica das pastas em `specs/`.
