from pathlib import Path

MIGRATIONS_DIR = Path(__file__).parent.parent.parent / "migrations"


def test_migrations_directory_exists():
    assert MIGRATIONS_DIR.is_dir()


def test_baseline_migration_exists():
    baseline = MIGRATIONS_DIR / "0001_create_transactions.sql"
    assert baseline.exists()
    content = baseline.read_text()
    assert "CREATE TABLE" in content
    assert "transactions" in content
    assert "transaction_hash" in content


def test_account_label_migration_exists():
    migration = MIGRATIONS_DIR / "0002_add_account_label.sql"
    assert migration.exists()
    content = migration.read_text()
    assert "account_label" in content
    assert "ALTER TABLE" in content
