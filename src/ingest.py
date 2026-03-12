import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document

# 1. Carregar variáveis do .env
load_dotenv()

def ingest_pdf():        

    # 2. Validar variáveis essenciais
    for k in ("OPENAI_API_KEY", "PGVECTOR_URL", "PG_VECTOR_COLLECTION_NAME"):
        if not os.getenv(k):
            raise RuntimeError(f"❌ Variável de ambiente {k} não está definida no .env")

    # 3. Definir caminho do PDF a partir do .env
    pdf_path = Path(os.getenv("PDF_PATH"))
    if not pdf_path.exists():
        raise FileNotFoundError(f"❌ PDF não encontrado em {pdf_path}")

    # 4. Carregar o PDF
    docs = PyPDFLoader(str(pdf_path)).load()

    # 5. Dividir em chunks (pedaços menores de texto)
    splits = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        add_start_index=False
    ).split_documents(docs)

    if not splits:
        raise SystemExit("❌ Nenhum texto foi extraído do PDF.")

    # 6. Enriquecer os documentos (limpar metadados vazios)
    enriched = [
        Document(
            page_content=d.page_content,
            metadata={k: v for k, v in d.metadata.items() if v not in ("", None)}
        )
        for d in splits
    ]

    # 7. Criar IDs únicos para cada chunk
    ids = [f"doc-{i}" for i in range(len(enriched))]

    # 8. Configurar embeddings (modelo definido no .env)
    embeddings = OpenAIEmbeddings(
        model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    )

    # 9. Conectar ao Postgres com JSONB para metadados
    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
        connection=os.getenv("PGVECTOR_URL"),
        use_jsonb=True,  # salva metadados em formato JSONB
    )

    # 10. Adicionar documentos ao banco
    store.add_documents(documents=enriched, ids=ids)

    print(f"✅ Ingestão concluída! {len(enriched)} chunks do PDF foram armazenados na coleção '{os.getenv('PG_VECTOR_COLLECTION_NAME')}'.")

if __name__ == "__main__":
    ingest_pdf()