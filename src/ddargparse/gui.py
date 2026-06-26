from typing import TYPE_CHECKING
from typing import Callable
from dataclasses import dataclass
from asyncio import Task
import asyncio
import flet as ft

if TYPE_CHECKING:
    from ddargparse import OptionsBase


@dataclass
class State:
    progress: float | None
    progress_msg: str | None
    options: bool = False
    results: Callable[["ft.Container"], None] | None = None


class Gui[O: "OptionsBase"]:
    def __init__(self, options_cls: type[O]) -> None:
        self._app_closed_event = asyncio.Event()
        self._state_queue: asyncio.Queue[State] = asyncio.Queue()
        self._app_runner: Task
        self._page: "ft.Page"
        self._options_cls = options_cls

    async def run(self) -> None:
        self._app_runner = asyncio.ensure_future(ft.run_async(self._app))

    async def _app(self, page: "ft.Page") -> None:
        self._page = page
        page.on_close = self._app_closed_event.set

        await self._update(State(options=True))
        asyncio.create_task(self._watch_state())

    async def _update(self, state: State) -> None:
        def view(content):
            self.page.controls.append(
                ft.SafeArea(
                    expand=True,
                    content=content
                )
            )

        self.page.controls.clear()
        if state.options:
            view(
                content=self._options_view(),
            )
        elif state.progress is not None:
            view(
                content=ft.Row(
                    controls=[
                        ft.ProgressBar(state.progress)
                    ]
                ),
            )
        self.page.update_async()

    async def _watch_state(self) -> None:
        while True:
            await self._update(await self._state_queue.get())
            self._state_queue.task_done()

    def set_state(self, state: State) -> None:
        self._state_queue.put_nowait(state)

    def _options_view(self) -> "ft.Row":
        def render_control(interpreted_field):
            field_type = interpreted_field.field_type
            name = interpreted_field.name
            if field_type is bool:
                return ft.Checkbox(label=name)
            elif field_type is str:
                return ft.TextField(label=name)
            elif field_type is int:
                return ft.TextField(label=name)
            elif field_type is float:
                return ft.TextField(label=name)
            elif field_type

        return ft.Row(
            controls=[
                control
                for interpreted_field in
                self._options_cls.interpret_fields(ignore_subcommand_fields=True)
                for control in render_control(interpreted_field)
            ]
        )

    def is_closed(self) -> bool:
        return self._app_closed_event.is_set()

    def get_options(self) -> O:


    def show_progress(self, progress: float, progress_msg: str | None) -> None:
        self.set_state(State(progress=progress, progress_msg=progress_msg))

    def show_results(self, results: Callable[["ft.Container"], None]) -> None:
        self.set_state(State(results=results))