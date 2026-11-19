"""Resolve and verify the bundled, versioned AttentiveFP checkpoint."""
from pathlib import Path
import hashlib
import os

CHECKPOINT_SHA256 = 'b0ce3c93834d03578d094f7f7b7dc2429fb35892d6dd4d36478c8f27f909d5ba'

def checkpoint_path():
    base = Path(__file__).resolve().parent
    configured = os.environ.get('TLC_CHECKPOINT')
    path = Path(configured).expanduser() if configured else base / 'models' / 'best_model.pt'
    if not path.is_absolute():
        path = base / path
    if not path.is_file():
        raise FileNotFoundError('The bundled model is missing. Check the Bundle checkpoint GitHub Actions run.')
    if not configured:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != CHECKPOINT_SHA256:
            raise ValueError('The bundled checkpoint checksum does not match the released model.')
    return path
