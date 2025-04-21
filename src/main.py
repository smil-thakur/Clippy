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
from components.aiResponseContainer import *
from agentTools.agentTools import *


def adjust_window_height(mainColumn: ft.Column, page: ft.Page):
    match len(mainColumn.controls):
        case 1:
            page.window.height = 70
        case 2:
            if contains_element(mainColumn, "search_result_container"):
                page.window.height = 450
            if contains_element(mainColumn, "response"):
                page.window.height = 350
        case 3:
            page.window.height = 650


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
        remove_control_by_key(
            key="search_result_container", container=mainColumn)
        remove_control_by_key(mainColumn, "response")
        adjust_window_height(mainColumn, page)
        debouncer.callback = lambda: debounced_search(
            query, latest_query, page, mainColumn
        )
        debouncer.call()
        page.update()
        return
    else:
        if len(query) > 4:
            debouncer.callback = lambda: debounced_search(
                query, latest_query, page, mainColumn
            )
            debouncer.call()


async def searchBarEntered(e: ft.ControlEvent, agent: Agent, mainColumn: ft.Column, page: ft.Page):

    remove_control_by_key(mainColumn, "response")
    mainColumn.controls.insert(1, AIResponseContainer(
        ft.Text("I am thinking...."), width=page.width, key="response", page=page))
    adjust_window_height(mainColumn, page)
    page.update()
    res = (await agent.arun(e.data)).content

    remove_control_by_key(mainColumn, "response")
    mainColumn.controls.insert(1, AIResponseContainer(
        ft.Markdown(value=res, selectable=True,
                    shrink_wrap=True,
                    extension_set=ft.MarkdownExtensionSet.GITHUB_WEB, code_theme=ft.MarkdownCodeTheme.DARCULA),
        width=page.width, key="response", res=res, page=page))
    adjust_window_height(mainColumn, page)

    page.update()


load_dotenv()


def createAgent() -> Agent:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing in your .env file")
    return Agent(
        model=Gemini("gemini-2.0-flash", api_key=api_key),
        tools=[AgentTools.searchWeb()],
        description=(
            "You are an intelligent assistant embedded in a search interface. "
            "In addition to helping with searches, you can summarize information, define words, and write small, precise code snippets. "
            "Keep all responses brief and focused, as this assistant is designed for quick, lightweight tasks."
        ),
        markdown=True
    )


async def main(page: ft.Page):
    page.window.width = 620
    page.window.max_width = 620
    page.window.min_width = 620
    page.window.min_height = 70
    page.window.height = 100
    page.window.resizable = True
    page.window.frameless = True
    page.bgcolor = "#1a1f2c"

    agent = createAgent()
    debouncer = Debouncer(1, None)
    mainColumn = ft.Column()

    async def on_submit(e: ft.ControlEvent):
        await searchBarEntered(e, agent, mainColumn, page)

    search = ft.TextField(
        hint_text="Search something...",
        on_submit=on_submit,
        border_color="#403e43",
        bgcolor="#1d1f2a",
        on_change=lambda e: expand_window(e, debouncer, page, mainColumn),
        border_radius=12,
        hint_style=ft.TextStyle(color="#9b87f5"),
        suffix_icon=ft.Icon(ft.Icons.SEARCH, size=30, color="#9b87f5"),

    )
    mainColumn.controls.append(search)

    page.add(mainColumn)

ft.app(target=main)
