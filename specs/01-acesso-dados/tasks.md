# Tasks - Acesso a Dados (camada base , somente leitura)

- [] Criar leitura de variáveis de ambiente / `st.secrets`
- [] Criar engine de conexão SQLAlchemy + psycopg2
- [] Criar função utilitária de execução de query parametrizada por período.
- [] Criar consultas agregadas base  (faturamento, quantidade vendida, etc) reutilizáveis pelas specs seguintes.
- [] Aplicar `st.cache_data` com TTL correto por tipo de consulta
- [] Tratar erro de conexão sem expor credenciais.
- [] Criar testes simples que garanta que nenhuma função gera SQL de escrita.

## Dependências

Specs `02-dasboard-executivo` e `03-analise-comercial` dependem desta