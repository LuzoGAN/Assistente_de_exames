import flet as ft
import os
import shutil

usuario = os.getlogin()

def main(page: ft.Page):
    def pick_files_result(e: ft.FilePickerResultEvent):
        selected_files.value = (
            ", \n".join(map(lambda f: f.name, e.files)) if e.files else "Cancelado!"
        )

        #Criação da pasta de não existir
        destinaion_folder = r"C:\\assistente_resultados"
        if not  os.path.exists(destinaion_folder):
            os.makedirs(destinaion_folder)

        # Mover os arquivos
        for file in e.files:
            shutil.copy(file.path, os.path.join(destinaion_folder, file.name))
        else:
            selected_files.value = selected_files.value

        selected_files.update()

    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    selected_files = ft.Text()

    page.overlay.append(pick_files_dialog)

    page.add(
        ft.Row(
            [
                ft.ElevatedButton(
                    "Escolha os arquivos: ",
                    icon=ft.icons.UPLOAD_FILE,
                    on_click=lambda _:pick_files_dialog.pick_files(
                        allow_multiple=True
                    ),
                ),
                selected_files,
            ]
        )
    )

ft.app(target=main)