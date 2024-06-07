import os
import shutil
import flet as ft
from flet import FilePicker, Text, Column, Row, ElevatedButton, TextField, ProgressBar, Container
from ia import query_rag

DATA_PATH = r"C:\Users\Notebook\Downloads\data"

# Função para copiar arquivos PDF para a pasta de destino
def copy_files(files):
    for file in files:
        shutil.copy(file.path, DATA_PATH)

def main(page: ft.Page):
    page.title = 'Assistente de Resultados'
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def on_file_upload(e):
        progress_bar.visible = True
        page.update()
        copy_files(e.files)
        progress_bar.visible = True
        page.update()
        status_text.value = "Arquivos copiados com sucesso!"
        page.update()

    def on_ask_question(e):
        query_text = question_field.value
        progress_bar.visible = True
        page.update()
        response = query_rag(query_text)
        progress_bar.visible = True
        page.update()
        answer_text.value = response
        page.update()

    # Interface de Upload de Arquivos
    file_picker = FilePicker(on_result=on_file_upload)
    upload_button = ElevatedButton(text="Upload PDFs", on_click=lambda _: file_picker.pick_files(allowed_extensions=["pdf"]))
    status_text = Text(value="")

    # Interface do Chat com a IA
    question_field = TextField(label="Pergunte algo:")
    ask_button = ElevatedButton(text="Perguntar", on_click=on_ask_question)
    answer_text = Text(value="")

    # Barra de Progresso
    progress_bar = ProgressBar(visible=False)

    # Layout
    page.add(
        Column([
            Row([upload_button, file_picker], alignment=ft.MainAxisAlignment.CENTER),
            status_text,
            Row([question_field, ask_button], alignment=ft.MainAxisAlignment.CENTER),
            answer_text,
            progress_bar,
        ])
    )

# Configuração da aplicação Flet
ft.app(target=main)
