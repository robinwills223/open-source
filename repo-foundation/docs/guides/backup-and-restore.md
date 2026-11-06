# Guide: Minimum Viable Backup & Restore

This guide explains how to protect your application's data using the built-in backup and verification commands, how to safely copy backups off your server, and how to practice restoring your data.

> [!IMPORTANT]
> **Baseline Data Protection:** Having paying customers or beta users requires a verified backup routine. If your computer or cloud server disk fails, any data not copied off the machine is permanently lost.

---

## 1. Why Same-Server Backups Are Not Enough

Creating a backup file in a folder on your application server is only the first half of a backup. If the server's hard disk corrupts, if the cloud host terminates the instance, or if someone accidentally deletes the server, **both your live application and your backup folder are destroyed simultaneously**.

A true backup requires two steps:
1. **Local Consistent Snapshot:** Take a safe, uncorrupted copy of the SQLite database.
2. **Off-Server Copy:** Immediately transfer that file to a completely separate storage provider (such as Cloudflare R2, AWS S3, or Backblaze B2).

---

## 2. The Built-in Commands

Your project includes two management commands that use Python's native `sqlite3` backup API:

### `python manage.py backup_db`
- **What it does:** Safely locks and streams a consistent point-in-time copy of your SQLite database to the `./backups/` directory (or the path set in the `BACKUP_DIR` environment variable).
- **Integrity Guarantee:** Immediately runs `PRAGMA integrity_check` on the newly written snapshot. If the file is corrupted in any way, the command deletes the broken file and exits with an error.
- **Automatic Pruning:** Keeps only the newest 14 backups (configurable via `BACKUP_KEEP`) so your disk does not fill up.
- **What success looks like:**
  ```text
  Initiating live backup from .../db.sqlite3 to .../backups/backup_20261106_120000.sqlite3...
  PASS: Backup created successfully (64.0 KB). Integrity verified: OK.
  ```

### `python manage.py verify_backup <file>`
- **What it does:** Restores the specified snapshot into a temporary, isolated database, checks its internal consistency, and prints the exact row counts for every table.
- **Live Database Safety:** **Never touches or modifies your live database.**
- **Restore Drill Target:** Completes verification and confirms row counts in under 10 minutes.
- **What success looks like:**
  ```text
  Initiating verification of snapshot: backup_20261106_120000.sqlite3...
  Integrity check on restored database: OK.

  Restored Table Row Counts (12 tables found):
  ---------------------------------------------
    auth_user                        :        2 rows
    records_record                   :       15 rows
    ...
  ---------------------------------------------
  Total rows verified across all tables: 17
  PASS: Backup verification completed successfully. Elapsed time: 0.042 seconds.
  ```

---

## 3. How to Copy Backups Off the Server

We recommend **Rclone**, an open-source command-line tool that syncs files to dozens of cloud storage providers (S3, Cloudflare R2, Google Drive, Backblaze B2, SFTP).

### Setting up Rclone (5 Minutes)
1. Install rclone on your server:
   - Linux: `sudo apt install rclone` (or official package from rclone.org, verify before use)
2. Configure your storage remote:
   ```bash
   rclone config
   ```
   Follow the interactive prompt to set up your S3-compatible remote (named e.g. `offsite`).
3. Test copying your backups:
   ```bash
   rclone copy ./backups/ offsite:my-app-backups/
   ```

---

## 4. Automating with Cron

On Linux/VPS servers, schedule both the snapshot and off-server transfer to run automatically every night at 2:00 AM:

```bash
crontab -e
```

Add the following line (replace `/path/to/project` with your real directory):
```bash
0 2 * * * cd /path/to/project && .venv/bin/python manage.py backup_db >> /var/log/backup.log 2>&1 && rclone copy /path/to/project/backups/ offsite:my-app-backups/ >> /var/log/backup.log 2>&1
```

### Checking that the Schedule Ran
- Check the log file: `cat /var/log/backup.log`
- Check the local backup folder: `ls -la ./backups/`
- Check your remote cloud storage bucket to confirm the latest snapshot timestamp matches today's date.

---

## 5. Encrypting Backups Before Upload

Because database snapshots contain user emails, hashes, and records, encrypt them before uploading if your storage bucket is public or shared.

- **Option A (Rclone Crypt - Recommended):** Configure an encrypted overlay remote using Rclone's built-in `crypt` backend (`rclone config` &rarr; choose `crypt`). Files are encrypted on-the-fly before sending over the network.
- **Option B (GnuPG):** Encrypt snapshots using GPG before uploading:
  ```bash
  gpg --symmetric --cipher-algo AES256 ./backups/backup_*.sqlite3
  ```
  *(UNVERIFIED: verify GPG installation and key management policies on your host before use).*

---

## 6. How to Practice a Real Restore Drill

Every 30 to 90 days, practice restoring your backup to confirm your team can recover from a disaster in under 10 minutes:

1. Download the latest snapshot from your off-site bucket to a test computer:
   ```bash
   rclone copy offsite:my-app-backups/latest.sqlite3 ./test_restore/
   ```
2. Verify the downloaded snapshot:
   ```bash
   python manage.py verify_backup ./test_restore/latest.sqlite3
   ```
3. Inspect the row counts printed in the output. If the row counts match your expected customer record volumes and the elapsed time is under 10 minutes, your restore drill has **PASSED**.

---

## 7. Honest Baseline Limits

- **Backups do not prevent data leaks:** Backups protect against disk failures and human mistakes. They do not protect against hackers or security breaches.
- **Protect your backup copies:** A stolen backup file exposes all database records. Always restrict access to your off-site bucket and use encryption.
- **Point-in-time gap:** Daily backups mean that any data entered between the last snapshot (e.g. 2:00 AM) and an afternoon crash is lost. For mission-critical zero-data-loss requirements, upgrade to medium scope with managed PostgreSQL streaming replication per [`docs/05`](../05-rules-single-source.md).
