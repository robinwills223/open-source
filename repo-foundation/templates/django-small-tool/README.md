# My Small Tool Starter

Welcome to your generated project! This is a clean, local web application starter built with Python and Django.

---

## What Is Included

- **Personal Records Tracker:** A ready-to-use workflow where logged-in users can create, view, update, delete, and filter their own records.
- **Ownership Isolation:** Each user only sees their own records. Other users cannot view or modify your data.
- **Formula-Safe CSV Export:** Download your data anytime with built-in protection against spreadsheet formula injection.
- **Local SQLite Database:** Your data is stored safely in a single `db.sqlite3` file on your computer.

---

## Quick Start (Run on Your Computer)

### 1. Set Up Your Environment File
Copy the example environment settings file:
```bash
cp .env.example .env
```

### 2. Set Up the Database
Run migrations to create the database tables:
```bash
python manage.py migrate
```

### 3. Create Your First Account
Because public signups are disabled by default for privacy and security, create your administrator account:
```bash
python manage.py createsuperuser
```
Follow the prompts to enter a username and password.

### 4. Start the Application
Start your local server:
```bash
python manage.py runserver
```
Open your browser and visit: **http://127.0.0.1:8000**

---

## Running the Automated Tests

Verify that all baseline security and data isolation tests pass:
```bash
python manage.py test
```

---

## Customizing Your Tool

To change this starter into your specific workflow, open this project folder in your LLM tool and ask:
> *"Help me customize the Record model to track [my specific data, e.g. customer feedback, job applications, invoices] instead."*

