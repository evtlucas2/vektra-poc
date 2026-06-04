import os
import sys
from pathlib import Path

from dotenv import load_dotenv

_ENV_FILE = Path(__file__).parent.parent / "config" / ".env"

from src.etl.extract import extract_transactions
from src.etl.load import create_table_if_not_exists, db_connect, insert_transactions
from src.etl.scan import scan
from src.etl.transform import transform_transactions


def _resolve_directory(raw_path: str) -> Path:
    data_root = os.environ.get("DATA_ROOT", "")
    if data_root and not Path(raw_path).is_absolute():
        return Path(data_root) / raw_path
    return Path(raw_path)


def _process_files(conn, files: list[Path]) -> tuple[int, int, int]:
    total_inserted = total_skipped = file_errors = 0
    for path in files:
        try:
            raw = extract_transactions(path)
            txns = transform_transactions(raw)
            skipped = len(raw) - len(txns)
            inserted = insert_transactions(conn, txns)
            print(f"[INFO] {path.name} → {inserted} inserted, {skipped} skipped (filtered), 0 errors")
            total_inserted += inserted
            total_skipped += skipped
        except Exception as exc:
            print(f"[ERROR] Skipped file: {path.name} — {exc}", file=sys.stderr)
            file_errors += 1
    return total_inserted, total_skipped, file_errors


def main(argv: list[str] | None = None) -> int:
    load_dotenv(_ENV_FILE)
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("[ERROR] Usage: python -m src.cli <ofx-directory>", file=sys.stderr)
        return 1
    directory = _resolve_directory(args[0])
    if not directory.is_dir():
        print(f"[ERROR] Directory not found: {directory}", file=sys.stderr)
        return 1
    files = scan(directory)
    if not files:
        print(f"[INFO] No OFX files found in {directory}. Nothing to do.")
        return 0
    conn = db_connect()
    create_table_if_not_exists(conn)
    inserted, skipped, errors = _process_files(conn, files)
    conn.close()
    print(f"[INFO] Total: {inserted} inserted, {skipped} skipped, {errors} file error(s) across {len(files)} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
