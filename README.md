# 📄 Desafio MBA --- Ingestão e Busca com IA (RAG)

Este projeto foi desenvolvido como parte do **MBA em Engenharia de
Software com IA --- Full Cycle**.

O objetivo é implementar um pipeline completo de **RAG (Retrieval
Augmented Generation)** que permite:

-   Ingerir documentos **PDF**
-   Gerar **embeddings vetoriais**
-   Armazenar os vetores em **PostgreSQL + PGVector**
-   Recuperar contexto relevante
-   Permitir **perguntas e respostas baseadas no documento**

------------------------------------------------------------------------

# 🧠 Arquitetura da Solução

Fluxo da aplicação:

PDF\
↓\
Ingestão\
↓\
Chunking do documento\
↓\
Geração de embeddings (LangChain)\
↓\
Armazenamento vetorial (PGVector)\
↓\
Retriever\
↓\
LLM (GPT)\
↓\
Resposta ao usuário

Fluxo resumido:

1.  O documento PDF é carregado\
2.  O texto é dividido em **chunks**\
3.  Cada chunk recebe um **embedding vetorial**\
4.  Os embeddings são armazenados no **Postgres + PGVector**\
5.  O usuário faz uma pergunta\
6.  O sistema busca os **chunks mais relevantes**\
7.  O modelo **LLM** gera a resposta baseada no contexto recuperado

------------------------------------------------------------------------

# 🚀 Tecnologias utilizadas

-   Python 3.10+
-   LangChain
-   PostgreSQL
-   PGVector
-   Docker / Docker Compose
-   OpenAI API
-   Python Dotenv

------------------------------------------------------------------------

# 📂 Estrutura do projeto

    mba-ia-desafio-ingestao-busca
    │
    ├── src
    │   ├── ingest.py        # Pipeline de ingestão do PDF
    │   ├── search.py        # Recuperação vetorial
    │   └── chat.py          # Interface de perguntas e respostas
    │
    ├── docker-compose.yml
    ├── requirements.txt
    ├── .env
    └── README.md

------------------------------------------------------------------------

# ⚙️ Instalação e Configuração

## 1️⃣ Clonar o repositório

``` bash
git clone https://github.com/teiabessa2/mba-ia-desafio-ingestao-busca.git
cd mba-ia-desafio-ingestao-busca
```

------------------------------------------------------------------------

## 2️⃣ Criar ambiente virtual

``` bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

``` bash
venv\Scripts\activate
```

------------------------------------------------------------------------

## 3️⃣ Instalar dependências

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

# 🔐 Configuração das Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto.

    OPENAI_API_KEY=chave_api_aqui

    GOOGLE_EMBEDDING_MODEL=models/embedding-001
    OPENAI_EMBEDDING_MODEL=text-embedding-3-small

    PGVECTOR_URL=postgresql://postgres:postgres@localhost:5433/rag
    PG_VECTOR_COLLECTION_NAME=documentos

    PDF_PATH=document.pdf

    MODEL_NAME=gpt-4o-mini

Descrição das variáveis:

  Variável                    Descrição
  --------------------------- -------------------------------------
  OPENAI_API_KEY              Chave da API OpenAI
  OPENAI_EMBEDDING_MODEL      Modelo usado para gerar embeddings
  PGVECTOR_URL                String de conexão com o Postgres
  PG_VECTOR_COLLECTION_NAME   Nome da coleção de embeddings
  PDF_PATH                    Caminho do PDF a ser ingerido
  MODEL_NAME                  Modelo LLM utilizado para respostas

------------------------------------------------------------------------

# 🗄️ Banco de Dados

Este projeto utiliza **PostgreSQL com extensão PGVector** para armazenar
embeddings.

## 1️⃣ Subir o banco com Docker

``` bash
docker-compose up -d
```

## 2️⃣ Acessar o banco

``` bash
psql -h localhost -p 5433 -U postgres -d rag
```

Observação: a porta **5433** foi utilizada pois já havia outro container
PostgreSQL rodando na porta padrão.

## 3️⃣ Criar extensão PGVector

``` sql
CREATE EXTENSION IF NOT EXISTS vector;
```

------------------------------------------------------------------------

# 📥 Ingestão de Documentos

Para carregar o PDF e gerar os embeddings execute:

``` bash
python3 src/ingest.py
```

Saída esperada:

    ✅ Ingestão concluída!
    67 chunks do PDF foram armazenados na coleção 'documentos'

------------------------------------------------------------------------

# 🔎 Recuperação de Contexto

Arquivo:

    src/search.py

Configuração padrão:

``` python
retriever = vector_store.as_retriever(search_kwargs={"k": 10})
```

Isso significa que **10 chunks mais relevantes** são recuperados.

Para documentos maiores pode-se aumentar:

    k = 20 ou 30

------------------------------------------------------------------------

# 💬 Chat de Perguntas e Respostas

Para interagir com os documentos ingeridos:

``` bash
python3 src/chat.py
```

Exemplo:

    Digite sua pergunta (ou 'sair' para encerrar):

    Qual o ano de fundação da Brava Eventos Comércio?

Resposta esperada:

    Brava Eventos Comércio foi fundada em 1943.

------------------------------------------------------------------------

# 🔎 Consultas no PostgreSQL

### Listar coleções

``` sql
SELECT * FROM langchain_pg_collection;
```

### Contar embeddings por coleção

``` sql
SELECT c.name, COUNT(e.id) AS total_chunks
FROM langchain_pg_collection c
LEFT JOIN langchain_pg_embedding e
  ON e.collection_id = c.uuid
GROUP BY c.name;
```

### Visualizar chunks armazenados

``` sql
SELECT document, cmetadata
FROM langchain_pg_embedding
WHERE collection_id = (
    SELECT uuid FROM langchain_pg_collection
    WHERE name = 'documentos'
)
LIMIT 5;
```

------------------------------------------------------------------------

# 🗑️ Remover uma coleção

``` sql
DELETE FROM langchain_pg_embedding
WHERE collection_id = (
    SELECT uuid FROM langchain_pg_collection
    WHERE name = 'documentos'
);

DELETE FROM langchain_pg_collection
WHERE name = 'documentos';
```

------------------------------------------------------------------------

# 📌 Possíveis melhorias futuras

-   Interface Web com **Streamlit**
-   Upload dinâmico de documentos
-   Suporte a múltiplos PDFs
-   Reranking de documentos
-   Cache de embeddings
-   Observabilidade com **LangSmith**

------------------------------------------------------------------------

# 👩‍💻 Autor

Projeto desenvolvido por **Auricélia Bessa Alves**\
MBA em Engenharia de Software com IA --- Full Cycle
