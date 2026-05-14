from sqlalchemy.orm import Session
from ..state.Database import Database
from ..models.Event import Event

def audit(ip: str, action: str, description: str | None = None) -> None:
    """
    Registra un evento en la base de datos de forma segura.
    """
    # Usamos un bloque try-except. Es vital que si la base de datos falla
    # (por ejemplo, se cae la red), esto no rompa tu servidor de sockets.
    try:
        # El context manager 'with' se encarga de cerrar la sesión automáticamente
        with Session(Database().get_engine()) as session:
            nuevo_evento = Event(
                ip=ip,
                action=action,
                description=description
            )
            session.add(nuevo_evento)
            session.commit()
    except Exception as e:
        # Si el log falla, al menos lo imprimimos en consola para depurar
        print(f"[LOGGING ERROR] Could not save event '{action}' from {ip}: {e}")