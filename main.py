import flet as ft
import socket
from front import query_rag


def main(page: ft.Page):
    page.title = "Chat Flet"
    #txt_input = ft.TextField(hint_text="Digite sua mensagem aqui...")
    txt_input = ft.TextField(hint_text="Digite sua mensagem aqui...")
    txt_output = ft.TextField(read_only=True, multiline=True, height=200)
    btn_send = ft.IconButton(ft.icons.SEND)

    def send_click(e):
        # Desativa o botão de enviar
        btn_send.enabled = False
        btn_send.bgcolor = ft.colors.RED
        page.update()

        # Cria um socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Conecta ao servidor
            s.connect(('192.168.174.80', 12345))

            # Envia a mensagem para o servidor
            s.sendall(txt_input.value.encode())

            # Recebe a resposta do servidor
            data = s.recv(1024)

            # Adiciona a resposta do servidor ao campo de saída
            txt_output.value += f'Servidor: {data.decode()}\n'

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

ft.app(main)