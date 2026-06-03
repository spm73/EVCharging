from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Label, Static
from textual.reactive import reactive

from .CPEngine import CPEngine
from .Event import Event
from .EventType import EventType


class EngineStatusPanel(Static):
    state_str: reactive[str] = reactive("Starting...")

    def render(self) -> str:
        return f"ESTADO DEL MOTOR: {self.state_str}"


class EngineApp(App):
    CSS = """
    Screen {
        background: $surface;
    }

    #main-layout {
        height: 1fr;
        padding: 1 2;
    }

    #left-panel {
        width: 35;
        padding: 1;
        border: round $primary;
    }

    #right-panel {
        width: 1fr;
        padding: 1;
        align: center middle;
    }

    .section-title {
        text-style: bold;
        color: $text-muted;
        margin-bottom: 1;
    }

    Button {
        width: 100%;
        margin-bottom: 1;
    }

    EngineStatusPanel {
        height: 5;
        content-align: center middle;
        text-align: center;
        text-style: bold;
        border: heavy $success;
        background: $surface-light;
        color: $text;
    }
    """

    BINDINGS = [("q", "quit", "Salir")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="main-layout"):
            with Vertical(id="left-panel"):
                yield Label("SIMULACIÓN FÍSICA", classes="section-title")
                yield Button("Pasar Tarjeta (Pedir Carga)", id="btn-request-supply", variant="primary")
                yield Button("Desenchufar Vehículo", id="btn-unplug", variant="warning")
                
                yield Label("SIMULACIÓN DE HARDWARE", classes="section-title")
                yield Button("Simular Avería", id="btn-fault", variant="error")
                yield Button("Reparar Avería", id="btn-resolve", variant="success")

            with Vertical(id="right-panel"):
                yield EngineStatusPanel(id="engine-status")

        yield Footer()

    def on_mount(self) -> None:
        # Actualizar el estado en la UI cada 500ms
        self.set_interval(0.5, self.update_engine_status)

    def update_engine_status(self) -> None:
        try:
            engine = CPEngine()
            state_name = str(engine.current_state)
            
            # Formateo amigable
            if "WaitingForConfig" in state_name:
                display = "ESPERANDO CONFIGURACIÓN"
            elif "Broken" in state_name:
                display = "AVERIADO (ROJO)"
            elif "Supplying" in state_name:
                display = "SUMINISTRANDO (VERDE)"
            elif "Stopped" in state_name:
                display = "PARADO POR CENTRAL (NARANJA)"
            elif "Idle" in state_name:
                display = "ACTIVO / DISPONIBLE (VERDE)"
            else:
                display = state_name

            panel = self.query_one("#engine-status", EngineStatusPanel)
            panel.state_str = display
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        engine = CPEngine()
        if event.button.id == "btn-request-supply":
            engine.put_event(Event(EventType.SUPPLY_STARTED))
        elif event.button.id == "btn-unplug":
            engine.put_event(Event(EventType.SUPPLY_ENDED))
        elif event.button.id == "btn-fault":
            engine.put_event(Event(EventType.FAULT_SIMULATED))
        elif event.button.id == "btn-resolve":
            engine.put_event(Event(EventType.FAULT_RESOLVED))
