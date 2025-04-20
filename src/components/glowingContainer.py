import flet as ft
import math
import asyncio


def GlowingBorderContainer(content: ft.Control, height=200, width=200, padding=5, key=None):
    angle = 0.0

    gradient_container = ft.Container(
        width=width,
        height=height,
        border_radius=12,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[  # Pastel/Siri style colors
                "0xffff6ec4", "0xffffa3a5", "0xffffd6e8", "0xfff6c0ec",
                "0xffe0b3ff", "0xffda9fff", "0xfffcb1ff", "0xffffd5ec",
                "0xffffe4b3", "0xffffb677", "0xfffcbf49", "0xfffacccc",
                "0xfffaffd1", "0xffcafffb", "0xffb8f3ff", "0xffd6e6ff", "0xffe7dfff"
            ],
            tile_mode=ft.GradientTileMode.MIRROR,
            rotation=angle
        ),
    )

    blurred_glass = ft.Container(
        width=width,
        height=height,
        blur=ft.Blur(10, 0, ft.BlurTileMode.MIRROR),
        bgcolor=ft.Colors.TRANSPARENT,
        border_radius=12
    )

    centered_content = ft.Container(
        width=width - 2 * (padding + 10),
        height=height - 2 * padding,
        content=content,
        alignment=ft.alignment.center,
        bgcolor=ft.Colors.BLACK,
        padding=10,
        border_radius=12,
    )

    async def animate_rotation():
        nonlocal angle
        # counter = 0
        # while True:
        #     angle += 0.01
        #     if angle > 2 * math.pi:
        #         angle = 0.0

        #     gradient_container.gradient.rotation = angle

        #     # Only update every 5 ticks
        #     if counter % 5 == 0:
        #         gradient_container.update()

        #     counter += 1
        #     await asyncio.sleep(0.01)

    stack = ft.Stack(
        controls=[gradient_container, blurred_glass, centered_content],
        alignment=ft.alignment.center,
        key=key
    )

    # ⬅️ Return the content for dynamic updates
    return stack, animate_rotation, centered_content
