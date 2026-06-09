from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Label, Log, Static
from textual.reactive import reactive
from textual import work

from EV_CP_M.monitor_engine import MonitorEngine


ENGINE_STATES = {
    "disconnected": ("DISCONNECTED", "engine--disconnected"),
    "stopped":      ("STOPPED",      "engine--stopped"),
    "available":    ("ACTIVE",       "engine--available"),
    "supplying":    ("SUPPLYING",    "engine--supplying"),
    "broken":       ("BROKEN DOWN",  "engine--broken"),
}


class EngineStatusPanel(Static):
    state: reactive[str] = reactive("disconnected")

    def render(self) -> str:
        label, _ = ENGINE_STATES.get(self.state, ("UNKNOWN", ""))
        return f"ENGINE  ·  {label}"

    def watch_state(self, new_state: str) -> None:
        for _, css_class in ENGINE_STATES.values():
            self.remove_class(css_class)
        _, css_class = ENGINE_STATES.get(new_state, ("", "engine--disconnected"))
        self.add_class(css_class)


class MonitorApp(App):
    CSS = """
    Screen {
        background: $surface;
    }

    #main-layout {
        height: 1fr;
        padding: 1 2;
    }

    #left-panel {
        width: 28;
        padding: 1;
        border: round $primary;
    }

    #right-panel {
        width: 1fr;
        padding: 1;
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
        border: heavy $primary;
        margin-bottom: 1;
    }

    .engine--disconnected { background: $surface-darken-2; color: $text-muted; }
    .engine--stopped      { background: darkorange;        color: black; }
    .engine--available    { background: darkgreen;         color: white; }
    .engine--supplying    { background: green;             color: white; }
    .engine--broken       { background: darkred;           color: white; }

    #event-log {
        border: round $primary;
        height: 1fr;
    }
    """

    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self) -> None:
        super().__init__()
        self.__engine = MonitorEngine(self)
        self.__registered = self.__engine.is_registered()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="main-layout"):
            with Vertical(id="left-panel"):
                yield Label("REGISTRATION", classes="section-title")
                yield Button("Connect Engine",      id="btn-connect",    variant="primary")
                yield Button("Register CP",         id="btn-register",   variant="primary", disabled=self.__registered)
                yield Button("Unregister",          id="btn-unregister", variant="error",   disabled=True)

                yield Label("CENTRAL", classes="section-title")
                yield Button("Authenticate",        id="btn-auth",       variant="success", disabled=True)

            with Vertical(id="right-panel"):
                yield EngineStatusPanel(id="engine-status", classes="engine--disconnected")
                yield Label("EVENT LOG", classes="section-title")
                yield Log(id="event-log", highlight=True)

        yield Footer()

    # ── Public methods called by MonitorEngine from polling thread ──────────

    def log_event(self, msg: str) -> None:
        """Thread-safe log. Can be called from any thread."""
        self.call_from_thread(self.query_one("#event-log", Log).write_line, msg)

    def set_engine_state(self, state: str) -> None:
        """Must be called via call_from_thread from outside the UI thread."""
        panel = self.query_one("#engine-status", EngineStatusPanel)
        panel.state = state

        # Unregister only allowed when engine is stopped
        can_unregister = self.__registered and state == "stopped"
        self.query_one("#btn-unregister", Button).disabled = not can_unregister

    # ── Button handlers ─────────────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        handlers = {
            "btn-connect":    self._handle_connect,
            "btn-register":   self._handle_register,
            "btn-unregister": self._handle_unregister,
            "btn-auth":       self._handle_auth,
        }
        handler = handlers.get(event.button.id)
        if handler:
            handler()

    @work(thread=True)
    def _handle_connect(self) -> None:
        if self.__engine.connect_engine():
            self.call_from_thread(self._post_connect_ui)

    def _post_connect_ui(self) -> None:
        self.query_one("#btn-connect", Button).disabled = True
        self.query_one("#btn-auth",    Button).disabled = False

    @work(thread=True)
    def _handle_register(self) -> None:
        if self.__engine.register():
            self.call_from_thread(self._post_register_ui)

    def _post_register_ui(self) -> None:
        self.__registered = True
        self.query_one("#btn-register", Button).disabled = True

    @work(thread=True)
    def _handle_unregister(self) -> None:
        self.__engine.unregister()
        self.call_from_thread(self._post_unregister_ui)

    def _post_unregister_ui(self) -> None:
        self.__registered = False
        self.query_one("#btn-connect",    Button).disabled = False
        self.query_one("#btn-register",   Button).disabled = False
        self.query_one("#btn-unregister", Button).disabled = True
        self.query_one("#btn-auth",       Button).disabled = True

    @work(thread=True)
    def _handle_auth(self) -> None:
        self.__engine.authenticate()