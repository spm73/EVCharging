from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.widgets import Button, Footer, Header, Label, Log, Static
from textual.reactive import reactive

from .api_consumer import register, unregister

ENGINE_STATES = {
    "disconnected": ("DISCONNECTED",  "engine--disconnected"),
    "stopped":      ("STOPPED",       "engine--stopped"),
    "available":    ("AVAILABLE",     "engine--available"),
    "supplying":    ("SUPPLYING",     "engine--supplying"),
    "broken":       ("BROKEN",        "engine--broken"),
}


class EngineStatusPanel(Static):
    """Central panel showing the Engine status with the corresponding color."""

    state: reactive[str] = reactive("disconnected")

    def render(self) -> str:
        label, _ = ENGINE_STATES.get(self.state, ("UNKNOWN", ""))
        return f"ENGINE  ·  {label}"

    def watch_state(self, new_state: str) -> None:
        # Remove all previous state classes and apply the new one
        for _, css_class in ENGINE_STATES.values():
            self.remove_class(css_class)
        _, css_class = ENGINE_STATES.get(new_state, ("", "engine--disconnected"))
        self.add_class(css_class)


class SupplyInfo(Static):
    """Real-time data when the Engine is supplying."""

    def compose(self) -> ComposeResult:
        yield Label("Consumption: -- kW",  id="lbl-power")
        yield Label("Amount:      -- €",   id="lbl-amount")
        yield Label("Driver ID:   --",     id="lbl-driver")


class MonitorApp(App):
    """Main application for the EV_M Monitor."""

    CSS = """
    /* ── Layout ─────────────────────────────── */
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

    /* ── Left panel sections ────────────────── */
    .section-title {
        text-style: bold;
        color: $text-muted;
        margin-bottom: 1;
    }

    Button {
        width: 100%;
        margin-bottom: 1;
    }

    /* ── Engine status panel ────────────────── */
    EngineStatusPanel {
        height: 5;
        content-align: center middle;
        text-align: center;
        text-style: bold;
        border: heavy $primary;
        margin-bottom: 1;
    }

    /* Colors per state */
    .engine--disconnected { background: $surface-darken-2; color: $text-muted; }
    .engine--stopped      { background: darkorange;        color: black; }
    .engine--available    { background: darkgreen;         color: white; }
    .engine--supplying    { background: green;             color: white; }
    .engine--broken       { background: darkred;           color: white; }

    /* ── Supply data ────────────────────────── */
    SupplyInfo {
        border: round $accent;
        padding: 1;
        margin-bottom: 1;
        display: none;          /* hidden except when supplying */
    }

    SupplyInfo.visible {
        display: block;
    }

    /* ── Event log ──────────────────────────── */
    #event-log {
        border: round $primary;
        height: 1fr;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    # ── Internal state ──────────────────────────
    _registered:    bool = False
    _authenticated: bool = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="main-layout"):

            # ── Left panel: controls ────────────
            with Vertical(id="left-panel"):

                yield Label("REGISTRATION", classes="section-title")
                yield Button("Register",   id="btn-register",   variant="primary")
                yield Button("Unregister", id="btn-unregister", variant="error",   disabled=True)

                yield Label("CENTRAL", classes="section-title")
                yield Button("Authenticate", id="btn-auth",     variant="success", disabled=True)

            # ── Right panel: status + log ───────
            with Vertical(id="right-panel"):

                yield EngineStatusPanel(id="engine-status", classes="engine--disconnected")
                yield SupplyInfo(id="supply-info")

                yield Label("EVENT LOG", classes="section-title")
                yield Log(id="event-log", highlight=True)

        yield Footer()

    # ── Helpers ─────────────────────────────────

    def _log(self, msg: str) -> None:
        self.query_one("#event-log", Log).write_line(msg)

    def _set_engine_state(self, state: str) -> None:
        panel = self.query_one("#engine-status", EngineStatusPanel)
        panel.state = state

        supply_info = self.query_one("#supply-info", SupplyInfo)
        if state == "supplying":
            supply_info.add_class("visible")
        else:
            supply_info.remove_class("visible")

    # ── Button handlers ─────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id

        if btn_id == "btn-register":
            self._handle_register()
        elif btn_id == "btn-unregister":
            self._handle_unregister()
        elif btn_id == "btn-auth":
            self._handle_auth()

    def _handle_register(self) -> None:
        """Register in EV_Registry via REST API."""
        # TODO: real call → requests.put(REGISTRY_URL + "/cp", json={...}, verify=False)
        self._log("[bold yellow]→ Requesting registration in EV_Registry…[/]")

        # Simulation of successful response
        self._registered = True
        self._log("[green]✓ Registration completed. Credentials received.[/]")

        self.query_one("#btn-register",   Button).disabled = True
        self.query_one("#btn-unregister", Button).disabled = False
        self.query_one("#btn-auth",       Button).disabled = False

        self._set_engine_state("stopped")

    def _handle_unregister(self) -> None:
        """Unregister from EV_Registry via REST API."""
        # TODO: real call → requests.delete(REGISTRY_URL + "/cp/{id}", verify=False)
        self._log("[bold red]→ Requesting unregistration from EV_Registry…[/]")

        self._registered    = False
        self._authenticated = False
        self._log("[red]✓ Unregistration completed.[/]")

        self.query_one("#btn-register",   Button).disabled = False
        self.query_one("#btn-unregister", Button).disabled = True
        self.query_one("#btn-auth",       Button).disabled = True

        self._set_engine_state("disconnected")

    def _handle_auth(self) -> None:
        """Authentication in EV_Central. Receives symmetric encryption key."""
        if not self._registered:
            self._log("[red]✗ You must register before authenticating.[/]")
            return

        # TODO: real call to Central with Registry credentials
        self._log("[bold cyan]→ Authenticating in EV_Central…[/]")

        self._authenticated = True
        self._log("[green]✓ Authentication successful. Encryption key received.[/]")

        self._set_engine_state("available")


if __name__ == "__main__":
    MonitorApp().run()