# Operational Baseline Security Guide

## Purpose & Honest Baseline Disclaimer

> [!IMPORTANT]
> **Baseline is the floor, not the ceiling:** This guide and the built-in `baseline_check` command provide a foundational starting point for a small application. They do **not** make your application "secure" or "compliant." Security is an ongoing practice, not a badge or single checklist. Every software system carries risk.

This document guides founders and development teams through running pre-launch sanity checks and ongoing dependency audits for small Django web applications.

---

## 1. The Built-in Baseline Check Command

Before launching your project or inviting outside testers, run the automated verification command:

```bash
python manage.py baseline_check
```

This command inspects your active Django settings and environment to catch common, dangerous misconfigurations before exposure to the public internet.

### What It Checks and How to Respond

| Check | Why It Matters | What to Do If It Fails |
| :--- | :--- | :--- |
| **`DEBUG` Mode** | If `DEBUG=True` on a live server, any code error will display your database passwords, secret keys, and internal code to whoever triggered the crash. | Set `DEBUG=False` in your production `.env` file or hosting environment variables. Keep `DEBUG=True` only on your personal machine during local development. |
| **`SECRET_KEY`** | Django uses this secret token to sign session cookies, CSRF tokens, and password reset links. If it is predictable, short, or left as the default placeholder, an attacker can forge user sessions. | Generate a fresh random string of 50 or more characters and place it in `.env` as `SECRET_KEY=...`. Never commit this string to version control. |
| **`ALLOWED_HOSTS`** | Prevents HTTP Host header attacks where malicious requests trick the server into generating password reset emails that point to an attacker's website. | Add your exact registered domain name (e.g., `ALLOWED_HOSTS=myapp.example.com,example.com`). Never set `ALLOWED_HOSTS=*` in production. |
| **`.gitignore` Rules** | Ensures sensitive files like `.env` (holding API keys and database credentials) are never committed to GitHub or Git history. | Open `.gitignore` and ensure `.env` is listed on its own line. If you accidentally committed `.env`, rotate all secrets immediately. |
| **Django Deploy Checks** | Runs Django's official `check --deploy` suite to review security middleware, cookie security flags, and SSL redirection. | Review any warnings output by `python manage.py check --deploy`. When your site has HTTPS enabled, turn on `SECURE_SSL_REDIRECT=True`. |
| **File Exposure Isolation** | Ensures your live `db.sqlite3` database file and backup directory are never located inside static or media folders served directly by your web server. | Keep database and backup files in the root folder or on a dedicated persistent data volume outside any directory served to the web. |
| **Administrative Accounts** | Warns if staff or superuser accounts lack working passwords or contact emails for account recovery and audits. | Log into `/admin/` and ensure all staff accounts have active, monitored email addresses and strong passwords. |

---

## 2. Dependency Vulnerability Audits (`pip-audit`)

Software libraries periodically discover security bugs that are cataloged in public vulnerability databases. You should inspect your installed packages regularly to ensure you are not running known vulnerable versions.

### Recommended Tool: `pip-audit`
`pip-audit` is maintained by the Python Packaging Authority (PyPA) and queries the Open Source Vulnerabilities (OSV) database.

### How to Install and Run

1. Install `pip-audit` into your local development virtual environment:
   ```bash
   pip install pip-audit
   ```
2. Run an audit against your dependencies:
   ```bash
   pip-audit -r requirements.txt
   ```

### When to Run
- **Before every production deployment:** Never deploy new code with unreviewed dependency vulnerabilities.
- **On a recurring schedule (e.g., monthly):** New vulnerabilities are discovered in existing packages over time even if you have not changed your code.

### What to Do When a Vulnerability is Found
1. **Check for an upgraded release:** Run `pip install --upgrade <package_name>` and check whether a patched version is available.
2. **Review release notes:** Test your application's automated test suite (`python manage.py test`) against the updated package to verify backward compatibility.
3. **If no patch exists yet:** Read the advisory description. Assess whether your application actually invokes the vulnerable function. If the vulnerable code path is active in your project, consider temporarily disabling the affected feature or substituting an alternate library.

---

## 3. What This Baseline Does NOT Cover

A passing baseline check does **not** mean your application is immune to attack. Baseline checks do **not** protect against:

- **Application Logic Flaws:** Flaws in your business rules, such as forgetting an authorization check on a custom view or allowing a user to manipulate an ID parameter.
- **Penetration Testing:** Active probing by security researchers testing for sophisticated chained exploits.
- **DDoS (Distributed Denial of Service):** Large volumes of malicious network traffic designed to overwhelm single-node servers.
- **Zero-Day Vulnerabilities:** Newly discovered flaws in Django, Python, SQLite, or the underlying operating system that do not yet have published fixes.
- **Social Engineering & Phishing:** Attacks targeting your personal email, password reuse, or credential stuffing against your staff accounts.
- **Third-Party Services:** Vulnerabilities or data breaches originating at your payment gateway, email delivery vendor, or cloud hosting provider.

For projects handling sensitive health data, direct payment card numbers, or large user volumes, a full professional third-party penetration test and architectural audit is required.
