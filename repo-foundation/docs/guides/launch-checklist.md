# Founder Pre-Launch & Operations Checklist

A practical, printable checklist for launching and operating your small application.

---

## 1. Before Launch (Preparation & Hardening)

- [ ] **Run `python manage.py baseline_check`**
  *Rationale: Verifies that DEBUG is OFF, SECRET_KEY is long and random, and security headers are active before public visitors arrive.*
- [ ] **Run dependency vulnerability audit (`pip-audit -r requirements.txt`)**
  *Rationale: Confirms installed software packages contain no known public security vulnerabilities.*
- [ ] **Verify `ALLOWED_HOSTS` matches registered domains**
  *Rationale: Prevents HTTP Host header spoofing attacks while ensuring legitimate traffic reaches the application.*
- [ ] **Verify database file is not in public web directories**
  *Rationale: Ensures the SQLite database cannot be downloaded directly over the web.*
- [ ] **Perform a test backup and restore drill (`python manage.py verify_backup`)**
  *Rationale: Guarantees your backup routine actually works before you have live customer data to lose.*
- [ ] **Verify SSL / HTTPS encryption**
  *Rationale: Ensures all user passwords, sessions, and data are encrypted in transit across the internet.*
- [ ] **Create your administrative superuser account**
  *Rationale: Gives you secure administrative access to Django admin for day-one operational support.*

---

## 2. Launch Day (Go-Live)

- [ ] **Point DNS A record to your server IP**
  *Rationale: Directs your public domain name to your live production host.*
- [ ] **Test user signup, login, and record creation in a clean incognito window**
  *Rationale: Verifies the full user flow functions properly in production with cookies and CSRF tokens enabled.*
- [ ] **Test CSV export download**
  *Rationale: Confirms background file generation and download headers work under live server reverse proxy settings.*
- [ ] **Inspect application logs for errors**
  *Rationale: Catches any silent server warnings or misconfigured static assets right after go-live.*

---

## 3. Day After Launch (Immediate Verification)

- [ ] **Verify the first automated daily backup ran**
  *Rationale: Confirms that scheduled cron jobs executed as expected without manual triggering.*
- [ ] **Verify off-server copy reached cloud storage**
  *Rationale: Ensures you have an off-host disaster recovery snapshot if the primary server fails.*
- [ ] **Check server disk space (`df -h`)**
  *Rationale: Ensures logs or temporary files are not consuming excessive storage.*
- [ ] **Review user feedback or login error reports**
  *Rationale: Identifies early friction points or unexpected user confusion while usage is small.*

---

## 4. Ongoing Maintenance (Weekly / Monthly)

- [ ] **Monthly dependency audit (`pip-audit`)**
  *Rationale: Identifies newly reported security advisories in upstream libraries.*
- [ ] **Monthly restore test drill**
  *Rationale: Periodically downloads an off-server snapshot and runs `verify_backup` to ensure snapshots remain healthy.*
- [ ] **Operating system security updates (`sudo apt update && sudo apt upgrade -y`)**
  *Rationale: Applies critical Linux kernel and system package security patches.*
- [ ] **Review escalation signals**
  *Rationale: Checks if application response times or database locking indicate it is time to upgrade scope (e.g. to PostgreSQL).*
