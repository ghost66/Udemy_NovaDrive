# Requeriments - Acesso a Dados (camada base , somente leitura)

**Stakeholder** CIO - Bruno Tavares

## Objetivo

Garantir uma camada de acesso ao banco de dados PostgreSQL de produção que seja somente de leitura e siga as regras técnicas do CIO, servindo de fundação para as demais specs(`02-dashboard-executivo`e `03-analise-comercial`)

## Contexto do Pedido

Bruno definiu regras não negociáveis antes de qualquer acesso ao banco: leitura apenas, interface em Streamlit, credenciais fora do código, filtro de período sempre no SQL, cache adequado ao peso da consulta.

## Perguntas de esclarecimento e Respostas

Pergunta : Qual intervalo de cache é aceitável ? Resposta: Consulta agregada simples : ~1 min. Consulta pesada com muitos joins: 15-20 min. 
Pergunta : Precisa de autentificação/login no dashboard? Resposta: Não nesta versão, uso interno.
Pergunta: Pode usar outra lib além do Streamlit? Resposta: sim, para gráficos Plotly e Altair, a camada interface deve ser Streamlit.
Pergunta: Qual o cuidado com o volume de dados? Resposta: Banco de dados cresce rápido, nunca trazer a tabela inteira, sempre filtrar por período na query 

## User stories

- O sistema deve conectar ao banco PostgreSQL usando credenciais lidas de variável de ambiente quando a aplicação iniciar.
- O sistema deve impedir qualquer instrução de escrita em qualquer consulta executada.
- O sistema deve aplicar filtro de período diretamente na cláusula SQL
quando uma consulta envolver a tabela `vendas`.
- O sistema deve cachear o resultado de cada consulta `st.cache_data`
quando a consulta for executada, com TTL de 1 min (agregação simples)
ou 15-20 min (consulta com multiplos joins).
- O sistema deve exibir uma mensagem de erro amigável, sem expor credenciais quando aconexão com o banco e dados falhar.

## Fora do Escopo / decisões negociadas

- Autenticação/login: fora do escopo nesta versão, uso interno.
- Escrita/Alteração de dados: nunca é implementado; regra fixa, não item de negociação.

## Critérios de Aceite
- [] Nenhuma credencial aparece no código-fonte ou é exposta em mensagens de erro.
- [] Toda consulta na tabela`vendas` recebe filtro de período no SQL.
- [] Cache aplicado em todas as consultas usadas pelos dashboards, com TTL correto por peso da consulta
- [] Conexão via variável de ambiente (`.env`) ou `st.secrets`, nunca hardcoded no código.



