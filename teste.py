import argparse
import os
import shutil
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
#from langchain.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
#from langchain.vectorstores.chroma import Chroma
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.ollama import OllamaEmbeddings
import flet as ft

CHROMA_PATH = "chroma"
DATA_PATH = r"C:\Users\Notebook\Downloads\data"

PROMPT_TEMPLATE = """
Responda à pergunta com base apenas no seguinte contexto:

{context}

---

Responda à pergunta com base no contexto acima: {question}
"""

def get_embedding_function():
    embeddings = OllamaEmbeddings(model='nomic-embed-text:latest', show_progress=True) # ou llama3
    return embeddings

def load_documents():
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()

def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=120,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def add_to_chroma(chunks: list[Document]):
    # Carregando o DB existente.
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )

    # Calculandos os IDs das páginas.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Adicioando ou atualizando o DB.
    existing_items = db.get(include=[])  # IDs inclusos
    existing_ids = set(existing_items["ids"])
    print(f"Números de páginas no DB: {len(existing_ids)}")

    # Adicionando somente documentos que não existem.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"Adicionando: {len(new_chunks)} Documentos")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        db.persist()
    else:
        print("Nada para Atualizar")

def calculate_chunk_ids(chunks):
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # Se o ID for o mesmo do último, incremento no número.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculando o chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Adicionando a página aos dados
        chunk.metadata["id"] = chunk_id

    return chunks

def query_rag(query_text: str):
    # Prepare the DB.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=3)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    model = Ollama(model="llama3")
    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("id", None) for doc, _score in results]

    formatted_response = f"Response: {response_text}\nSources: {sources}"
    return formatted_response

def main():
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)

# Flet interface integration
def flet_main(page: ft.Page):
    page.title = "Chat Flet"
    txt_input = ft.TextField(hint_text="Digite sua pergunta aqui...")
    txt_output = ft.TextField(read_only=True, multiline=True, height=200)
    btn_send = ft.IconButton(ft.icons.SEND)

    def send_click(e):
        # Desativa o botão de enviar
        btn_send.enabled = False
        btn_send.bgcolor = ft.colors.RED
        page.update()

        # Obtém a resposta do modelo
        response = query_rag(txt_input.value)

        # Adiciona a resposta ao campo de saída
        txt_output.value += f'Resposta: {response}\n'

        # Reativa o botão de enviar
        btn_send.enabled = True
        btn_send.bgcolor = ft.colors.GREEN

        # Limpa o campo de entrada
        txt_input.value = ''
        page.update()

    btn_send.on_click = send_click

    page.add(
        ft.Column(
            [
                ft.Row(
                    [
                        txt_input,
                        btn_send,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                txt_output,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

# Run the main function to process documents and add to Chroma
if __name__ == "__main__":
    main()

# Run the Flet application
ft.app(flet_main)
