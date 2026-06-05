from pathlib import Path

from yoyo import get_backend, read_migrations

_MIGRATIONS_DIR = Path(__file__).parent.parent.parent / "migrations"


def apply_migrations(database_url: str) -> None:
    backend = get_backend(database_url)
    migrations = read_migrations(str(_MIGRATIONS_DIR))
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))
