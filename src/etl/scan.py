from pathlib import Path


def scan(directory: Path) -> list[Path]:
    """Return a sorted list of .ofx files in directory (case-insensitive)."""
    files = [p for p in directory.iterdir() if p.is_file() and p.suffix.lower() == ".ofx"]
    return sorted(files, key=lambda p: p.name)
