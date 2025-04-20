import flet as ft
from utilities.fileUtils import *


def ResultSectionContainer(section: str, paths: list[str], page: ft.Page) -> ft.Container:
    file_items = []

    for index, path in enumerate(paths):
        file_items.append(
            ft.Container(
                padding=ft.padding.symmetric(vertical=6, horizontal=10),
                content=ft.Column(
                    expand=False,
                    spacing=2,
                    controls=[
                        ft.Text(FileUtils.getFilename(path), style=ft.TextStyle(
                            weight=ft.FontWeight.BOLD, size=14)),
                        ft.Text(path, style=ft.TextStyle(
                            size=10, color=ft.Colors.GREY))
                    ]
                )
            )
        )

        if index < len(paths) - 1:
            file_items.append(
                ft.Divider(height=1, thickness=0.5, color=ft.Colors.GREY_300)
            )

    return ft.Container(
        padding=ft.padding.all(10),
        width=page.width,
        border=ft.border.all(width=1, color=ft.Colors.BLUE_200),
        border_radius=ft.border_radius.all(12),
        content=ft.Column(
            expand=False,
            spacing=10,
            controls=[
                ft.Text(section, style=ft.TextStyle(
                    size=20, weight=ft.FontWeight.W_600))
            ] + file_items
        )
    )
