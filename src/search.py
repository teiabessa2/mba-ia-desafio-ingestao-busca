import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Carrega variáveis de ambiente do arquivo .env
# Isso permite configurar credenciais e parâmetros sem precisar alterar o código
load_dotenv()

# Template que define como o modelo deve responder
# {context} será preenchido com os chunks recuperados do banco
# {pergunta} será preenchido com a pergunta feita pelo usuário
PROMPT_TEMPLATE = """
CONTEXTO:
{context}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

PERGUNTA DO USUÁRIO:
{question}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

def search_prompt():
    # 1. Ler variáveis do .env
    # MODEL_NAME → qual modelo da OpenAI será usado (ex.: gpt-4o-mini)
    # PGVECTOR_URL → string de conexão com o Postgres
    # COLLECTION_NAME → nome da coleção onde os embeddings foram armazenados
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
    PGVECTOR_URL = os.getenv("PGVECTOR_URL")
    COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")

    # 2. Conectar ao banco vetorial (Postgres com extensão pgvector)
    # Aqui usamos PGVector como "armazenamento vetorial"
    # Ele sabe como buscar embeddings semelhantes no banco
    vector_store = PGVector(
        embeddings=OpenAIEmbeddings(),   # Função que gera embeddings para novas consultas
        collection_name=COLLECTION_NAME, # Nome da coleção criada na ingestão
        connection=PGVECTOR_URL,         # URL de conexão com o banco
        use_jsonb=True                   # Armazena metadados em formato JSONB
    )
    # O retriever é o componente que sabe "buscar os chunks mais relevantes"
    
    retriever = vector_store.as_retriever(search_kwargs={"k": 10}) #Busca apenas 10 chunks, mas para testar pode ser interessante aumentar para 30 ou 50 para ver mais contexto


    # 3. Configurar o modelo de linguagem
    # Esse é o LLM que vai receber o contexto e a pergunta
    llm = ChatOpenAI(model=MODEL_NAME)

    # 4. Criar o prompt template
    # Aqui definimos como o modelo deve estruturar a resposta
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )

    # 5. Montar a cadeia de QA (Pergunta e Resposta)
    # RetrievalQA combina:
    # - o modelo (llm)
    # - o retriever (que busca os chunks)
    # - o prompt (que define as regras de resposta)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",                 # "stuff" = junta os chunks em um único contexto
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True  # Faz com que, além da resposta final, o objeto retornado também traga os documentos recuperados.
    )

    # Retorna a cadeia pronta para ser usada no chat.py
    return qa_chain
