# Guide: How to Run Your Project on Your Computer

This beginner-friendly guide walks you through setting up and running your generated Django small tool.

> [!IMPORTANT]
> **Runs Locally Only:** Everything in this guide runs strictly on your personal computer. Your application is not yet connected to the public internet, and no one else can see your data.

---

## Step-by-Step Instructions

### Step 1: Check Python Installation
Make sure Python 3.10 or newer is installed on your computer.

- **Windows:**
  ```powershell
  python --version
  ```
- **macOS / Linux:**
  ```bash
  python3 --version
  ```
- **What it does:** Checks whether Python is installed and prints the version number.
- **What success looks like:** Output showing `Python 3.10.x` (or 3.11, 3.12, 3.13).

---

### Step 2: Create an Isolated Virtual Environment
A virtual environment keeps your project's software packages organized in a dedicated folder without affecting the rest of your system.

- **Windows:**
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```
- **macOS / Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- **What it does:** Creates and activates a self-contained Python working environment inside the `.venv` folder.
- **What success looks like:** Your terminal prompt changes to show `(.venv)` at the beginning of the line.

---

### Step 3: Install Project Packages
Install Django using the pinned requirements file.

```bash
pip install -r requirements.txt
```
- **What it does:** Downloads and installs the exact version of Django required by your tool.
- **What success looks like:** Output ending with `Successfully installed Django-...`.

---

### Step 4: Configure Your Environment File
Create your project's configuration file from the provided example template.

- **Windows:**
  ```powershell
  copy .env.example .env
  ```
- **macOS / Linux:**
  ```bash
  cp .env.example .env
  ```
- **What it does:** Creates a local `.env` configuration file containing safe default settings for local development.
- **What success looks like:** A new file named `.env` appears in your project folder.

---

### Step 5: Initialize the Database
Set up the tables in your local SQLite database file.

```bash
python manage.py migrate
```
- **What it does:** Creates the internal database structure needed to store accounts and records.
- **What success looks like:** A list of operations ending with `Applying ... OK` and a new `db.sqlite3` file created in your folder.

---

### Step 6: Create Your Admin Account
Because public signups are disabled by default for privacy, create your own administrator account.

```bash
python manage.py createsuperuser
```
- **What it does:** Prompts you to choose a username, email address (optional), and password for your personal login.
- **What success looks like:** Terminal prints `Superuser created successfully.`

---

### Step 7: Start the Local Development Server
Launch your application so you can open it in your web browser.

```bash
python manage.py runserver
```
- **What it does:** Starts a lightweight local web server on your computer.
- **What success looks like:** Output showing:
  `Starting development server at http://127.0.0.1:8000/`
  `Quit the server with CTRL-BREAK / CTRL-C.`

---

### Step 8: Open Your Browser
Open your favorite web browser (Chrome, Safari, Edge, or Firefox) and visit:
```text
http://127.0.0.1:8000
```
- **What it does:** Loads your application's login screen.
- **What success looks like:** You see the **Log In** page. Enter the username and password you created in Step 6 to access your records dashboard!

---

### Step 9: Run Automated Tests
Verify that all data isolation and security checks pass on your machine.

```bash
python manage.py test
```
- **What it does:** Runs automated tests confirming that permissions, CSV sanitization, and data isolation work correctly.
- **What success looks like:** Output ending with `OK` (e.g. `Ran 9 tests ... OK`).

---

## If Something Went Wrong (Top 5 Solutions)

### 1. "Python is not recognized as an internal or external command"
- **Cause:** Python is not installed or not added to your system's PATH variable.
- **Fix:** Download the latest Python installer from python.org. On Windows, check the box that says **"Add Python to PATH"** during installation, then restart your terminal.

### 2. "Execution of scripts is disabled on this system" (Windows PowerShell)
- **Cause:** Windows prevents unsigned scripts from running by default.
- **Fix:** Run this command once in PowerShell: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`, then activate `.venv\Scripts\Activate.ps1` again.

### 3. "Port 8000 is already in use"
- **Cause:** Another program or previous Django server is already running on port 8000.
- **Fix:** Run on another port: `python manage.py runserver 8001`, and visit `http://127.0.0.1:8001` in your browser.

### 4. "No such table: records_record"
- **Cause:** Step 5 (database migration) was skipped or interrupted.
- **Fix:** Run `python manage.py migrate` in your activated environment.

### 5. "RuntimeError: CRITICAL: The SECRET_KEY environment variable is required"
- **Cause:** Your `.env` file is missing or `DEBUG` was turned off without setting a production secret key.
- **Fix:** Ensure `.env` exists in the project root with `DEBUG=True` for local development, or set a random `SECRET_KEY=...` string in `.env`.

