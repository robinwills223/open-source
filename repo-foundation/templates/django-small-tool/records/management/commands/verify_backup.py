"""Management command to verify a backup snapshot in an isolated temporary database.

Cites: docs/05 Section 8 (Minimum Viable Backup Requirements).
Uses Python standard library only. Never modifies the live database.
"""

from pathlib import Path
import sqlite3
import tempfile
import time
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Restores a backup snapshot into an isolated temporary database, checks integrity, and counts rows."

    def add_arguments(self, parser):
        parser.add_argument(
            "backup_file",
            type=str,
            help="Path to the backup .sqlite3 snapshot file to verify.",
        )

    def handle(self, *args, **options):
        backup_path = Path(options["backup_file"]).resolve()
        if not backup_path.is_file():
            raise CommandError(f"Backup file does not exist: {backup_path}")

        t_start = time.perf_counter()
        self.stdout.write(f"Initiating verification of snapshot: {backup_path.name}...")

        # 1. Restore snapshot into an isolated temporary database directory
        with tempfile.TemporaryDirectory(prefix="backup_verify_") as tmp_dir:
            temp_db = Path(tmp_dir) / "restored.sqlite3"
            src_conn = None
            dst_conn = None
            try:
                try:
                    src_conn = sqlite3.connect(str(backup_path))
                    dst_conn = sqlite3.connect(str(temp_db))
                    with dst_conn:
                        src_conn.backup(dst_conn)
                except Exception as exc:
                    raise CommandError(f"Failed to restore snapshot into temporary database: {exc}")
                finally:
                    if src_conn:
                        src_conn.close()

                # 2. Run PRAGMA integrity_check on the restored database
                cursor = dst_conn.cursor()
                cursor.execute("PRAGMA integrity_check;")
                results = cursor.fetchall()

                if results != [("ok",)]:
                    raise CommandError(f"Integrity check failed on restored database: {results}")

                self.stdout.write(self.style.SUCCESS("Integrity check on restored database: OK."))

                # 3. Print table summary and row counts
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
                )
                tables = [r[0] for r in cursor.fetchall()]

                self.stdout.write(f"\nRestored Table Row Counts ({len(tables)} tables found):")
                self.stdout.write("-" * 45)
                total_rows = 0
                for table in tables:
                    try:
                        cursor.execute(f'SELECT COUNT(*) FROM "{table}";')
                        count = cursor.fetchone()[0]
                        total_rows += count
                        self.stdout.write(f"  {table:<32} : {count:>8} rows")
                    except Exception as exc:
                        self.stdout.write(self.style.WARNING(f"  {table:<32} : ERROR ({exc})"))

                self.stdout.write("-" * 45)
                self.stdout.write(f"Total rows verified across all tables: {total_rows}")
            except Exception as exc:
                if isinstance(exc, CommandError):
                    raise
                raise CommandError(f"Verification error while inspecting tables: {exc}")
            finally:
                if dst_conn:
                    dst_conn.close()

        # 4. Report elapsed verification time
        elapsed = time.perf_counter() - t_start
        self.stdout.write(self.style.SUCCESS(f"\nPASS: Backup verification completed successfully. Elapsed time: {elapsed:.3f} seconds."))
