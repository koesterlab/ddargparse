import sys
import asyncio
import flet as ft

app_closed_event = asyncio.Event()

async def main(page):
    # Pass our global event into the page session if needed, 
    # or handle it via a closure like we do here:
    def on_disconnect(e):
        print("Flet window closed by user.")
        app_closed_event.set()  # Signal that the app is done

    page.on_close = on_disconnect

    def button_click(e):
        page.controls.append(ft.Text("Clicked!"))
        # no need to call page.update() — it happens automatically

    page.controls.append(ft.Button("Click me", on_click=button_click))

async def app():
    _ = asyncio.ensure_future(ft.run_async(main))
    print("app started")
    await asyncio.sleep(5)
    print("app still running, I can do other stuff here")
    while not app_closed_event.is_set():
        print("still running")
        await asyncio.sleep(5)
    print("done, closing")
    sys.exit(0)

asyncio.run(app())