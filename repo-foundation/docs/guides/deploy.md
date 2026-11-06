# Production Deployment Guide (Ubuntu + systemd + Caddy)

## Overview & Architecture

This guide walks you through deploying your small Django tool onto a single virtual private server (VPS).

### Why This Architecture?
- **Persistent Disk:** Unlike ephemeral container platforms that wipe local files on reboot, a VPS disk preserves your SQLite database (`db.sqlite3`) across restarts and deploys.
- **No Docker Required:** Runs directly in a standard Python virtual environment, keeping maintenance simple for a solo founder or small team.
- **Automatic HTTPS:** Caddy web server handles TLS certificates automatically without complicated certbot cron jobs.
- **Reliable Process Management:** Ubuntu's standard `systemd` supervisor automatically restarts your application if it crashes or the server reboots.

---

## 1. Prerequisites

Before starting, make sure you have:
1. **A Domain Name:** Registered with any registrar (e.g. Cloudflare, Namecheap). You will need access to create DNS `A` records pointing to your server's IP address.
2. **A VPS Account:** An account with a reputable cloud hosting provider (e.g. DigitalOcean, Hetzner, Linode, AWS Lightsail).
   > [!NOTE]
   > *UNVERIFIED: check the provider's current docs before use* regarding current pricing and billing terms. Select a standard 1 GB or 2 GB RAM server running **Ubuntu 24.04 LTS**.
3. **An SSH Key:** To log into your server securely without typing passwords.

---

## 2. Server Provisioning & Initial Setup

Log into your server as root via your computer's terminal:

```bash
ssh root@<YOUR_SERVER_IP>
```

### Step 2.1: Update System Packages and Install Dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git caddy
```
*Why:* Updates operating system security patches and installs Python 3, Git, and the Caddy web server.

### Step 2.2: Create a Dedicated Application User
Running web services as `root` is dangerous. Create a dedicated unprivileged system user named `web`:

```bash
sudo adduser --disabled-password --gecos "" web
```

---

## 3. Deploying Code & Installing Dependencies

### Step 3.1: Clone the Application
Switch to the `web` user and clone your repository:

```bash
sudo -u web -i
git clone <YOUR_GIT_REPO_URL> /home/web/app
cd /home/web/app
```

### Step 3.2: Create Virtual Environment and Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-deploy.txt
```
*Why:* `requirements.txt` installs Django. `requirements-deploy.txt` installs Gunicorn (WSGI application server) and WhiteNoise (static file handler).

---

## 4. Configuring Production Environment Variables

Create the production `.env` configuration file on the server:

```bash
nano /home/web/app/.env
```

Enter your production values:

```bash
# Production Environment Settings
DEBUG=False
DJANGO_ENV=production

# Generate with: python3 -c "import secrets; print(secrets.token_urlsafe(50))"
SECRET_KEY=replace-with-your-generated-50-character-secret-key

# Your exact live domain names (comma-separated, no spaces)
ALLOWED_HOSTS=myapp.example.com,www.myapp.example.com

# Database path (stored in web user home directory, persistent across deploys)
DJANGO_DB_PATH=/home/web/app/db.sqlite3

# Redirect all HTTP requests to HTTPS
SECURE_SSL_REDIRECT=True
```

Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`). Secure permissions so only the `web` user can read secrets:

```bash
chmod 600 /home/web/app/.env
```

---

## 5. Running Database Migrations & Creating Admin Account

Inside the virtual environment (`source .venv/bin/activate`):

```bash
# Apply database schemas
python manage.py migrate

# Collect static assets into staticfiles/ for WhiteNoise
python manage.py collectstatic --noinput

# Create your initial administrative superuser
python manage.py createsuperuser
```

---

## 6. Verifying Baseline Security Configuration

Before directing traffic to your server, run the automated security verification command:

```bash
python manage.py baseline_check
```

*Expected Result:* `AUDIT RESULT: ALL PASS` or `PASS WITH WARNINGS`. Resolve any `[FAIL]` flags before moving to the next step.

---

## 7. Configuring systemd Service (Process Supervision)

Exit back to the `root` shell (type `exit` to return from the `web` user).

Create a systemd unit configuration file:

```bash
sudo nano /etc/systemd/system/django-app.service
```

Paste the following configuration:

```ini
[Unit]
Description=Gunicorn daemon for Django Small Tool
After=network.target

[Service]
User=web
Group=web
WorkingDirectory=/home/web/app
EnvironmentFile=/home/web/app/.env
ExecStart=/home/web/app/.venv/bin/gunicorn \
    --workers 2 \
    --bind 127.0.0.1:8000 \
    --access-logfile /home/web/app/gunicorn-access.log \
    --error-logfile /home/web/app/gunicorn-error.log \
    config.wsgi:application
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable django-app
sudo systemctl start django-app
sudo systemctl status django-app
```

*Why:* Systemd ensures Gunicorn starts whenever the server boots and restarts automatically if it ever crashes.

---

## 8. Configuring Caddy Reverse Proxy & Automatic HTTPS

Edit `/etc/caddy/Caddyfile`:

```bash
sudo nano /etc/caddy/Caddyfile
```

Replace the contents with:

```caddyfile
myapp.example.com {
    reverse_proxy 127.0.0.1:8000
}
```

Reload Caddy:

```bash
sudo systemctl reload caddy
```

*Why:* Caddy automatically contacts Let's Encrypt to issue and renew free SSL certificates, redirects HTTP to HTTPS, and forwards web requests to Gunicorn on port 8000.

---

## 9. Automated Minimum Viable Backup Routine

Protect customer data by scheduling daily database snapshots and copying them off-server.

As user `web` (`sudo -u web crontab -e`), add a daily cron job at 03:00 UTC:

```bash
0 3 * * * /home/web/app/.venv/bin/python /home/web/app/manage.py backup_db >> /home/web/app/backup.log 2>&1
```

### Off-Server Transfer
Install `rclone` and schedule a second cron job to sync `/home/web/app/backups` to an external S3-compatible cloud bucket (e.g., Backblaze B2, Cloudflare R2, or AWS S3):

```bash
15 3 * * * rclone copy /home/web/app/backups remote-s3:my-backup-bucket/daily-snapshots >> /home/web/app/rclone.log 2>&1
```

See [backup-and-restore.md](file:///repo-foundation/docs/guides/backup-and-restore.md) for full off-server setup instructions and restore drills.

---

## 10. Rollback Procedure

If a new deployment breaks the live application:

1. **Check error logs:**
   ```bash
   tail -n 50 /home/web/app/gunicorn-error.log
   sudo journalctl -u django-app -n 50
   ```
2. **Revert Git commit:**
   ```bash
   cd /home/web/app
   git log -n 5 --oneline
   git checkout <PREVIOUS_WORKING_COMMIT_HASH>
   ```
3. **Re-run migrations if needed:**
   ```bash
   source .venv/bin/activate
   python manage.py migrate
   ```
4. **Restart application:**
   ```bash
   sudo systemctl restart django-app
   ```
5. **Verify restoration:** Run `python manage.py baseline_check` and check the live URL.

---

## 11. Honest Limits of This Setup

This deployment architecture provides a clean, zero-configuration baseline for small projects. However, be aware of its operational limits:

- **Single Server Point of Failure:** If the hosting provider's physical server hardware fails or reboots, your app will experience brief downtime.
- **SQLite Write Throughput:** SQLite handles hundreds of concurrent readers with ease, but only one writer process at a time. If user actions perform heavy simultaneous database writes, you will experience lock contention.
- **When to Upgrade (Escalation Triggers):**
  - If database lock timeouts occur (`sqlite_lock_contention` signal), upgrade database to managed PostgreSQL (see `docs/02-scope-levels.md`).
  - If slow background tasks delay web requests (`slow_sync_calls` signal), turn on asynchronous background queues and Redis.
  - If user concurrency exceeds 500 active users, scale to multi-node hosting with a managed load balancer.
