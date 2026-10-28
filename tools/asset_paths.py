"""Local asset paths shared by explicitly selected, reviewed ROM targets."""
from pathlib import Path

TARGETS = frozenset(('us-v1.5', 'us-v1.4', 'us-v1.3', 'us-v1.2', 'us-v1.1', 'us-unversioned'))


def asset_path(target: str, name: str) -> Path:
    if (not isinstance(target, str) or target not in TARGETS or not isinstance(name, str)
            or not name or Path(name).name != name or not name.endswith('.json')):
        raise ValueError('invalid target asset path')
    return Path('extracted') / target / name
