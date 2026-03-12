from search import search_prompt

def main():
    chain = search_prompt() # chama o arquivo search.py para montar a cadeia de busca e resposta
    print("=== Chat de Perguntas sobre o PDF ===")
    while True:
        pergunta = input("\nDigite sua pergunta (ou 'sair' para encerrar): ")
        if pergunta.lower() == "sair":
            break

        result = chain.invoke({"query": pergunta}) #executa a cadeia passando a pergunta do usuário
        print("\nResposta:", result["result"])

        # Mostrar também os chunks de contexto usados
        print("\n--- Contexto usado ---")
        for i, doc in enumerate(result["source_documents"], start=1):
            print(f"Chunk {i}:")
            print(doc.page_content.strip())
            print("Metadados:", doc.metadata)
            print("-"*50)

if __name__ == "__main__":
    main()
