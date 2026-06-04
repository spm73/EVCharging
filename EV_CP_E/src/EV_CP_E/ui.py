import sys
from io import StringIO
from typing import TextIO

from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Button, Header, Label, RichLog
from textual.reactive import reactive
from textual.screen import Screen

from EV_CP_E.CPEngine import CPEngine
from EV_CP_E.Event import Event
from EV_CP_E.EventType import EventType

class StdoutRedirector(StringIO):
    def __init__(self, log_widget: RichLog, original_stdout: TextIO):
        super().__init__()
        self.log_widget = log_widget
        self.original_stdout = original_stdout

    def write(self, s: str) -> int:
        if s.strip():
            # Enviamos el log al UI thread
            try:
                self.log_widget.app.call_from_thread(self.log_widget.write, s.strip())
            except Exception:
                pass
        return len(s)

    def flush(self):
        pass


class EngineApp(App):
    CSS = """
    Screen {
        background: $surface;
    }

    .state-panel {
        height: 1fr;
        align: center middle;
        padding: 2;
    }

    #log-panel {
        height: 10;
        border-top: solid $primary;
        background: $surface-darken-1;
    }

    .title-label {
        text-style: bold;
        margin-bottom: 2;
        content-align: center middle;
    }
    
    .data-label {
        text-style: bold;
        margin-bottom: 1;
        content-align: center middle;
    }

    Button {
        width: 50%;
        margin-bottom: 1;
    }

    #btn-start-supply {
        width: 100%;
        height: 100%;
        border: heavy $success;
        background: $success;
        color: auto;
        text-style: bold;
        content-align: center middle;
    }
    """

    BINDINGS = [("q", "request_quit", "Salir")]
    
    current_view = reactive("None")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Vertical(id="dynamic-content"):
            yield Vertical(id="view-WaitingForConfigState", classes="state-panel")
            yield Vertical(id="view-IdleState", classes="state-panel")
            yield Vertical(id="view-PendingPlugState", classes="state-panel")
            yield Vertical(id="view-SupplyingState", classes="state-panel")
            yield Vertical(id="view-BrokenState", classes="state-panel")
            yield Vertical(id="view-StoppedState", classes="state-panel")
            
        yield RichLog(id="log-panel", highlight=True, markup=True)

    def on_mount(self) -> None:
        self.log_widget = self.query_one(RichLog)
        
        # Inyectamos el redireccionador de stdout
        self.original_stdout = sys.stdout
        sys.stdout = StdoutRedirector(self.log_widget, sys.stdout)
        
        self._build_views()
        
        # Fuerzo la vista inicial para asegurar que todo se oculta
        for v in self.query(".state-panel"):
            v.display = False

        self.set_interval(0.5, self.update_engine_status)

    def on_unmount(self) -> None:
        if hasattr(self, 'original_stdout'):
            sys.stdout = self.original_stdout

    def _build_views(self):
        # WaitingForConfigState
        view = self.query_one("#view-WaitingForConfigState")
        view.mount(Label("Waiting for configuration", classes="title-label"))

        # IdleState
        view = self.query_one("#view-IdleState")
        view.mount(Label("ACTIVO / DISPONIBLE", classes="title-label"))
        view.mount(Button("Request Supply", id="btn-request-supply", variant="primary"))
        view.mount(Button("Simulate Fault", id="btn-fault", variant="error"))

        # PendingPlugState (Autorización pendiente)
        view = self.query_one("#view-PendingPlugState")
        view.mount(Button("START SUPPLY", id="btn-start-supply", variant="success"))

        # SupplyingState
        view = self.query_one("#view-SupplyingState")
        view.mount(Label("SUMINISTRANDO", classes="title-label"))
        view.mount(Label("kWh: 0", id="lbl-consumption", classes="data-label"))
        view.mount(Label("€: 0.00", id="lbl-price", classes="data-label"))
        view.mount(Button("Stop Supply", id="btn-stop-supply", variant="warning"))

        # BrokenState
        view = self.query_one("#view-BrokenState")
        view.mount(Label("CP BROKEN", classes="title-label"))
        view.mount(Button("Repair Fault", id="btn-resolve", variant="success"))

        # StoppedState
        view = self.query_one("#view-StoppedState")
        view.mount(Label("OUT OF SERVICE", classes="title-label"))

    def action_request_quit(self) -> None:
        engine = CPEngine()
        engine.put_event(Event(EventType.SHUTDOWN))
        self.exit()

    def update_engine_status(self) -> None:
        engine = CPEngine()
        state_name = type(engine.current_state).__name__
        
        bg_color = "$surface"
        view_name = state_name
        
        if state_name == "WaitingForConfigState":
            bg_color = "gray"
        elif state_name == "IdleState":
            if getattr(engine, 'authorization_pending', False):
                view_name = "PendingPlugState"
                bg_color = "green"
            else:
                bg_color = "green"
        elif state_name == "SupplyingState":
            bg_color = "green"
            try:
                lbl_cons = self.query_one("#lbl-consumption", Label)
                lbl_price = self.query_one("#lbl-price", Label)
                with engine.supply_lock:
                    if engine.current_supply:
                        lbl_cons.update(f"kWh: {engine.current_supply.kwh_accumulated}")
                        lbl_price.update(f"€: {engine.current_supply.amount_accumulated:.2f}")
            except Exception:
                pass
        elif state_name == "BrokenState":
            bg_color = "red"
        elif state_name == "StoppedState":
            bg_color = "orange"

        self.screen.styles.background = bg_color
        
        if self.current_view != view_name:
            if self.current_view != "None":
                try:
                    old = self.query_one(f"#view-{self.current_view}")
                    old.display = False
                except Exception:
                    pass
            
            try:
                new = self.query_one(f"#view-{view_name}")
                new.display = True
                self.current_view = view_name
            except Exception:
                pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        engine = CPEngine()
        btn_id = event.button.id
        
        if btn_id == "btn-request-supply":
            engine.put_event(Event(EventType.SUPPLY_STARTED))
        elif btn_id == "btn-stop-supply":
            engine.put_event(Event(EventType.SUPPLY_ENDED))
        elif btn_id == "btn-fault":
            engine.put_event(Event(EventType.FAULT_SIMULATED))
        elif btn_id == "btn-resolve":
            engine.put_event(Event(EventType.FAULT_RESOLVED))
        elif btn_id == "btn-start-supply":
            engine.put_event(Event(EventType.VEHICLE_PLUGGED))

if __name__ == "__main__":
    EngineApp().run()
