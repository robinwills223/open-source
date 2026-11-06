"""Management command to create a consistent SQLite backup using sqlite3 backup API.

Cites: docs/05 Section 8 (Minimum Viable Backup Requirements).
Uses Python standard library only.
"""

from datetime import datetime
import os
from pathlib import Path
import sqlite3
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Creates a consistent SQLite snapshot via Python sqlite3 backup API and checks integrity."

    def add_arguments(self, parser):
        parser.add_argument(
            "--backup-dir",
            dest="backup_dir",
            default=None,
            help="Directory to store backup files (overrides BACKUP_DIR env var).",
        )
        parser.add_argument(
            "--keep",
            dest="keep",
            type=int,
            default=None,
            help="Number of snapshots to retain (overrides BACKUP_KEEP env var).",
        )
        parser.add_argument(
            "--source",
            dest="source",
            default=None,
            help="Optional path to source SQLite database file (defaults to DATABASES['default']['NAME']).",
        )

    def handle(self, *args, **options):
        # 1. Determine live DB path
        db_conf = settings.DATABASES.get("default", {})
        engine = db_conf.get("ENGINE", "")
        if "sqlite3" not in engine:
            raise CommandError(f"backup_db only supports SQLite databases. Current engine: {engine}")

        source_arg = options.get("source")
        if source_arg:
            live_db_path = Path(source_arg)
        else:
            live_db_path = Path(db_conf.get("NAME", "db.sqlite3"))

        if not live_db_path.is_file():
            raise CommandError(f"Live SQLite database file does not exist at {live_db_path}. Run migrations first.")

        # 2. Determine backup directory and retention count
        backup_dir_env = options["backup_dir"] or os.environ.get("BACKUP_DIR")
        backup_dir = Path(backup_dir_env) if backup_dir_env else (settings.BASE_DIR / "backups")
        backup_dir.mkdir(parents=True, exist_ok=True)

        keep_count = options["keep"] or int(os.environ.get("BACKUP_KEEP", "14"))

        # 3. Create timestamped snapshot file
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        dest_file = backup_dir / f"backup_{timestamp}.sqlite3"

        self.stdout.write(f"Initiating live backup from {live_db_path} to {dest_file}...")

        # 4. Perform consistent snapshot via sqlite3 backup API
        try:
            # Connect to source file in read-only mode to safely snapshot without locking writers
            src_conn = sqlite3.connect(f"file:{live_db_path.resolve().as_posix()}?mode=ro", uri=True)
            dst_conn = sqlite3.connect(str(dest_file))
            with dst_conn:
                src_conn.backup(dst_conn)
            dst_conn.close()
            src_conn.close()
        except Exception as exc:
            if dest_file.exists():
                dest_file.unlink(missing_ok=True)
            raise CommandError(f"Backup failed during sqlite3 backup operation: {exc}")

        # 5. Run PRAGMA integrity_check on the generated snapshot
        try:
            chk_conn = sqlite3.connect(str(dest_file))
            cursor = chk_conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            results = cursor.fetchall()
            chk_conn.close()

            if results != [("ok",)]:
                dest_file.unlink(missing_ok=True)
                raise CommandError(f"Integrity check failed on snapshot: {results}. Snapshot deleted.")
        except Exception as exc:
            dest_file.unlink(missing_ok=True)
            raise CommandError(f"Failed during snapshot integrity check: {exc}. Snapshot deleted.")

        file_size_kb = dest_file.stat().st_size / 1024
        self.stdout.write(self.style.SUCCESS(f"PASS: Backup created successfully ({file_size_kb:.1f} KB). Integrity verified: OK."))

        # 6. Apply retention policy (keep newest N snapshots)
        self.apply_retention(backup_dir, keep_count)

    def apply_retention(self, backup_dir: Path, keep_count: int):
        """Delete oldest backups beyond keep_count threshold."""
        backups = sorted(
            backup_dir.glob("backup_*.sqlite3"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if len(backups) > keep_count:
            excess = backups[keep_count:]
            for old_file in excess:
                try:
                    old_file.unlink(missing_ok=True)
                    self.stdout.write(f"Pruned old backup beyond retention limit: {old_file.name}")
                except Exception as exc:
                    self.stdout.write(self.style.WARNING(f"Warning: Failed to prune {old_file.name}: {exc}"))
