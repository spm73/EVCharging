import threading
import time
from os import getenv, path, makedirs, remove
from typing import TYPE_CHECKING
from decimal import Decimal

from EV_CP_M.engine_client import EngineClient
from EV_CP_M.central_client import CentralClient
from EV_CP_M.api_consumer import register as registry_register, unregister as registry_unregister

if TYPE_CHECKING:
    from EV_CP_M.ui import MonitorApp

POLLING_INTERVAL = 1.0
JWT_FILE_PATH = "data/jwt.token"

class MonitorEngine:
    def __init__(self, app: "MonitorApp") -> None:
        self.__app = app

        cp_id   = getenv("CP_ID")
        cp_loc  = getenv("CP_LOCATION")
        eng_host = getenv("ENGINE_HOST")
        eng_port = int(getenv("ENGINE_PORT"))
        cen_host = getenv("CENTRAL_HOST")
        cen_port = int(getenv("CENTRAL_PORT"))
        price = Decimal(getenv("PRICE_PER_KWH", "0.0"))

        self.__cp_id    = cp_id
        self.__location = cp_loc
        self.__price    = price
        self.__jwt: str | None = None

        self.__engine  = EngineClient(eng_host, eng_port)
        self.__central = CentralClient(cen_host, cen_port)

        self.__polling_thread: threading.Thread | None = None
        self.__running = False

        # Estado conocido del engine
        self.__engine_status: str | None = None
        self.__engine_connected  = False
        self.__central_connected = False
        
        if path.exists(JWT_FILE_PATH):
            try:
                with open(JWT_FILE_PATH, 'r') as f:
                    self.__jwt = f.read().strip()
                self.__app.log_event("[green]✓ JWT loaded from disk.[/]")
            except Exception as e:
                self.__app.log_event(f"[red]✗ Error loading saved JWT: {e}[/]")

    # ── API pública (llamada desde la UI) ───────────────────────────────────

    def connect_engine(self) -> bool:
        """Connect to the engine. First step before any other action."""
        if self.__engine.connect():
            self.__engine_connected = True
            self.__app.log_event("[green]✓ Connected to engine.[/]")
            return True
        self.__app.log_event("[red]✗ Could not connect to engine.[/]")
        return False

    def register(self) -> bool:
        """Register in EV_Registry and obtain JWT."""
        self.__app.log_event("[yellow]→ Registering in EV_Registry…[/]")
        try:
            self.__jwt = registry_register(self.__cp_id, self.__location, self.__price)
            makedirs(path.dirname(JWT_FILE_PATH), exist_ok=True)
            with open(JWT_FILE_PATH, "w") as f:
                f.write(self.__jwt)
            self.__app.log_event("[green]✓ Registration successful.[/]")
            return True
        except Exception as e:
            self.__app.log_event(f"[red]✗ Registration failed: {e}[/]")
            return False

    def authenticate(self) -> bool:
        """
        Authenticate in EV_Central. Connects if not already connected.
        Sends the received key to the engine.
        Can be called at any time to re-authenticate.
        """
        self.__app.log_event("[cyan]→ Authenticating in EV_Central…[/]")

        if not self.__central_connected:
            if not self.__central.connect():
                self.__app.log_event("[red]✗ Could not connect to Central.[/]")
                return False
            self.__central_connected = True

        cp_key = self.__central.authenticate(self.__cp_id, self.__jwt)
        if cp_key is None:
            self.__app.log_event("[red]✗ Authentication denied by Central.[/]")
            self.__central_connected = False
            return False

        self.__app.log_event("[green]✓ Authentication successful. Sending config to engine…[/]")

        if not self.__engine.send_config(self.__cp_id, cp_key, self.__price):
            self.__app.log_event("[red]✗ Could not send config to engine.[/]")
            return False

        self.__app.log_event("[green]✓ Config delivered to engine.[/]")

        if not self.__running:
            self.__start_polling()

        return True

    def unregister(self) -> None:
        """
        Unregister from EV_Registry. Only allowed when engine is Stopped.
        Stops polling and disconnects both clients.
        """
        self.__stop_polling()

        self.__app.log_event("[red]→ Unregistering from EV_Registry…[/]")

        self.__central.disconnect()
        self.__central_connected = False

        self.__engine.disconnect()
        self.__engine_connected = False

        try:
            registry_unregister(self.__cp_id)
            if path.exists(JWT_FILE_PATH):
                remove(JWT_FILE_PATH)
            self.__jwt = None
            self.__app.log_event("[green]✓ Unregistration successful.[/]")
        except Exception as e:
            self.__app.log_event(f"[red]✗ Unregistration failed: {e}[/]")

        self.__app.call_from_thread(self.__app.set_engine_state, "disconnected")

    # ── Polling ─────────────────────────────────────────────────────────────

    def __start_polling(self) -> None:
        self.__running = True
        self.__polling_thread = threading.Thread(
            target=self.__poll_loop, daemon=True
        )
        self.__polling_thread.start()
        self.__app.log_event("[green]✓ Polling started.[/]")

    def __stop_polling(self) -> None:
        self.__running = False
        if self.__polling_thread:
            self.__polling_thread.join(timeout=3)
            self.__polling_thread = None

    def __poll_loop(self) -> None:
        while self.__running:
            self.__poll_once()
            time.sleep(POLLING_INTERVAL)

    def __poll_once(self) -> None:
        # ── 1. Consultar estado del engine ──────────────────────────────────
        status = self.__engine.get_status()

        if status is None:
            # Engine caído
            if self.__engine_connected:
                self.__engine_connected = False
                self.__app.log_event("[red]✗ Lost connection to engine.[/]")
                self.__app.call_from_thread(self.__app.set_engine_state, "broken")
                self.__try_report_broken()
            self.__try_reconnect_engine()
            return

        self.__engine_connected = True
        self.__engine_status = status
        self.__app.call_from_thread(self.__app.set_engine_state, self.__status_to_ui(status))

        # ── 2. Reportar estado a Central ─────────────────────────────────────
        ok = self.__central.send_status(status)

        if not ok:
            # Central caída
            if self.__central_connected:
                self.__central_connected = False
                self.__app.log_event("[red]✗ Lost connection to Central.[/]")

            # Si el engine está suministrando, ordenarle que pase a Stopped al acabar
            if status == "Supplying":
                self.__app.log_event("[yellow]→ Engine supplying — sending OUT_OF_SERVICE.[/]")
                self.__engine.send_out_of_service()

            self.__try_reconnect_central()
        else:
            self.__central_connected = True

    # ── Reconexiones ────────────────────────────────────────────────────────

    def __try_reconnect_engine(self) -> None:
        self.__app.log_event("[yellow]→ Trying to reconnect to engine…[/]")
        if self.__engine.connect():
            self.__engine_connected = True
            self.__app.log_event("[green]✓ Reconnected to engine.[/]")

    def __try_reconnect_central(self) -> None:
        self.__app.log_event("[yellow]→ Trying to reconnect to Central…[/]")
        if not self.__central.connect():
            return

        cp_key = self.__central.authenticate(self.__cp_id, self.__jwt)
        if cp_key is None:
            self.__app.log_event("[red]✗ Re-authentication denied.[/]")
            return

        self.__central_connected = True
        self.__app.log_event("[green]✓ Reconnected and re-authenticated with Central.[/]")

        if not self.__engine.send_config(self.__cp_id, cp_key, self.__price):
            self.__app.log_event("[red]✗ Could not resend config to engine.[/]")

    def __try_report_broken(self) -> None:
        """Report BROKEN_DOWN to Central if connected."""
        if self.__central_connected:
            self.__central.send_status("Broken Down")

    # ── Helpers ─────────────────────────────────────────────────────────────

    @staticmethod
    def __status_to_ui(status: str) -> str:
        return {
            "Stopped":     "stopped",
            "Active":      "available",
            "Supplying":   "supplying",
            "Broken Down": "broken",
        }.get(status, "disconnected")