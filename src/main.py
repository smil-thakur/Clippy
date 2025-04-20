import asyncio
import flet as ft
from utilities.debouncer import *
from utilities.fileUtils import *
from utilities.openApp import *
from utilities.listSorter import *
from utilities.searchUtils import *
from components.resultSection import *
from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import os
from components.glowingContainer import *
import random


def adjust_window_height(mainColumn: ft.Column, page: ft.Page):
    match len(mainColumn.controls):
        case 1:
            page.window.height = 70
        case 2:
            if contains_element(mainColumn, "search_result_container"):
                page.window.height = 450
            if contains_element(mainColumn, "response"):
                page.window.height = 300
        case 3:
            page.window.height = 650


# ✅ Helper: Remove a control by its unique key
def remove_control_by_key(container: ft.Column, key: str):
    container.controls = [
        c for c in container.controls if getattr(c, "key", None) != key]


def contains_element(mainColumn: ft.Column, key: str):
    for c in mainColumn.controls:
        if getattr(c, "key") == key:
            return True
    return False


def debounced_search(query: str, latest_query: dict, page: ft.Page, mainColum: ft.Column):
    print(query, latest_query["value"])
    if not query.strip():
        remove_control_by_key(
            key="search_result_container", container=mainColum)
        adjust_window_height(mainColum, page)
        remove_control_by_key(
            key="response", container=mainColum)
        return
    if query != latest_query["value"]:
        return

    results = SearchUtils.search_files(query)
    sortedRes = ListSorter.sortListToDict(results)

    print(len(results))

    if results:
        remove_control_by_key(
            key="search_result_container", container=mainColum)
        results_container = resultSection(sortedRes, page)
        result_main_container = ft.Container(
            key="search_result_container",
            height=370,
            content=results_container
        )
        mainColum.controls.append(result_main_container)
    else:
        remove_control_by_key(
            key="search_result_container", container=mainColum)

    adjust_window_height(mainColum, page)
    page.update()


def expand_window(e: ft.ControlEvent, debouncer: Debouncer, page: ft.Page, mainColumn: ft.Column):
    query = e.control.value.strip()
    latest_query = {"value": ""}
    latest_query["value"] = query

    if not query:
        adjust_window_height(mainColumn, page)
        debouncer.callback = lambda: debounced_search(
            query, latest_query, page, mainColumn
        )
        debouncer.call()
        remove_control_by_key(
            key="search_result_container", container=mainColumn)
        remove_control_by_key(mainColumn, "response")
        page.update()
        return
    else:
        if len(query) > 4:
            debouncer.callback = lambda: debounced_search(
                query, latest_query, page, mainColumn
            )
            debouncer.call()


# ✅ Updated: No index-based popping. All by key!
async def searchBarEntered(e: ft.ControlEvent, agent: Agent, mainColumn: ft.Column, page: ft.Page):

    print("loading......")

    glowContainer, task, glowContent = GlowingBorderContainer(
        content=ft.Text("Loading..."),  # Initial placeholder
        height=200,
        width=page.width,
        padding=4,
        key="response"
    )
    asyncio.create_task(task())

    # Add once
    remove_control_by_key(mainColumn, "response")
    mainColumn.controls.insert(1, glowContainer)
    adjust_window_height(mainColumn, page)
    page.update()

    try:
        result = await agent.arun(e.data)
        print(result.content)

        # 🔄 Just update the glowContent, not recreate the glowContainer
        glowContent.content = ft.Column(
            scroll=ft.ScrollMode.ALWAYS,
            controls=[
                ft.Markdown(value=result.content, selectable=True,
                            shrink_wrap=True,
                            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB, code_theme=ft.MarkdownCodeTheme.DARCULA)
            ]
        )
        glowContent.update()
        adjust_window_height(mainColumn, page)

    except Exception as ex:
        glowContent.content = ft.Text(f"Error: {ex}")
        glowContent.update()
        adjust_window_height(mainColumn, page)

    page.update()


load_dotenv()  # Automatically loads .env file


def createAgent() -> Agent:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing in your .env file")
    return Agent(
        model=Gemini("gemini-2.0-flash", api_key=api_key),
        description=(
            "You are an intelligent assistant embedded in a search interface. "
            "In addition to helping with searches, you can summarize information, define words, and write small, precise code snippets. "
            "Keep all responses brief and focused, as this assistant is designed for quick, lightweight tasks."
        ),
        markdown=True
    )


def giveRotation():
    return random.randint(1, 180)


async def main(page: ft.Page):
    page.window.width = 620
    page.window.max_width = 620
    page.window.min_width = 620
    page.window.min_height = 70
    page.window.height = 100
    page.window.resizable = True
    page.window.frameless = True

    agent = createAgent()
    debouncer = Debouncer(1, None)
    mainColumn = ft.Column()

    async def on_submit(e: ft.ControlEvent):
        await searchBarEntered(e, agent, mainColumn, page)

    search = ft.TextField(
        hint_text="Search something...",
        on_submit=on_submit,
        on_change=lambda e: expand_window(e, debouncer, page, mainColumn)
    )
    mainColumn.controls.append(search)

    page.add(mainColumn)
    print(page.window.height)

ft.app(target=main)
