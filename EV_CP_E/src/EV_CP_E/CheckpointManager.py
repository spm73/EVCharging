import json
from pathlib import Path

class CheckpointManager:
    """
    Gestiona la persistencia a disco (Singleton).
    Responsabilidad separada del CPEngine.
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, checkpoint_path: str = "/data/checkpoint.json"):
        if getattr(self, '_initialized', False):
            return
        self._initialized = True
        self.checkpoint_path = Path(checkpoint_path)
        self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, data: dict) -> None:
        """Guarda un diccionario en disco."""
        try:
            self.checkpoint_path.write_text(json.dumps(data, indent=2))
        except OSError as e:
            print(f"[CheckpointManager] Error saving checkpoint: {e}")

    def load(self) -> dict | None:
        """Carga el diccionario del disco si existe, None en caso contrario."""
        if not self.checkpoint_path.exists():
            return None
            
        try:
            return json.loads(self.checkpoint_path.read_text())
        except (OSError, json.JSONDecodeError) as e:
            print(f"[CheckpointManager] Error reading checkpoint: {e}")
            return None

    def clear(self) -> None:
        """Elimina el archivo de checkpoint."""
        try:
            self.checkpoint_path.unlink(missing_ok=True)
        except OSError as e:
            print(f"[CheckpointManager] Error deleting checkpoint: {e}")
