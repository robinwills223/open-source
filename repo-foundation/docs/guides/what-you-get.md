# Guide: What You Get in Your Generated Project

This overview describes what is included in your generated small-tool starter project, how to replace the starter workflow with your own idea, and the baseline protections built into the code.

---

## 1. What Is in the Box

Your generated project is a clean, minimal Python web application built using Django:

- **Personal Records Tracker:** A ready-to-use CRUD (Create, Read, Update, Delete) workflow. You can create records with titles, notes, and statuses (`draft`, `active`, `archived`), filter them, and inspect details.
- **Strict Data Isolation:** Each user only has access to their own records. If User B tries to view or edit a record owned by User A, the application immediately returns a `404 Not Found` response.
- **Admin Management Panel:** A built-in Django administration area at `/admin/` where you can view raw database tables and manage user accounts.
- **Formula-Safe CSV Export:** Download your data into a spreadsheet anytime. All text entries starting with dangerous formula characters (`=`, `+`, `-`, `@`) are automatically escaped to prevent spreadsheet formula execution attacks.
- **Local SQLite Database:** Everything is saved to a single local file (`db.sqlite3`). No cloud database configuration or external credentials are required to start.

---

## 2. Replacing the Starter with Your Own Workflow

The "Records Tracker" is an example archetype meant to be modified. You can turn it into whatever your business or tool needs by opening your project in your LLM coding assistant and giving a simple prompt.

### Example Prompts to Ask Your LLM:

1. **For Customer Feedback Tracker:**
   > *"In this project, modify the Record model to track Customer Feedback instead. I need customer name, email, rating from 1 to 5, feedback text, and whether we resolved their issue. Update the forms, views, and templates accordingly."*

2. **For Freelancer Invoicing / Job Tracker:**
   > *"I want to replace the records workflow with an Invoice Tracker. Each invoice needs client name, project description, dollar amount, due date, and payment status (unpaid, paid, overdue). Walk me through the code updates."*

3. **For Inventory or Asset Management:**
   > *"Transform the Record model into an Equipment Tracker with serial number, purchase date, assigned person, and condition. Keep the existing ownership isolation so only I can see our equipment."*

---

## 3. Baseline Security Features & Their Limits

### What Is Protected (Baseline Features)
- **Login Protection:** Every record page requires logging in; unauthenticated users are redirected to the login screen.
- **Ownership Verification:** Every view query enforces `user=request.user` at the database query level.
- **CSRF Defense:** All forms include cross-site request forgery protection tokens.
- **CSV Sanitization:** Spreadsheets opened in Excel, Google Sheets, or LibreOffice cannot execute arbitrary macros from user inputs.
- **Production Headers Ready:** When `DEBUG` is set to `False`, standard defensive headers (`X-Frame-Options: DENY`, `SECURE_CONTENT_TYPE_NOSNIFF`, strict session cookies) activate automatically.

### What Is NOT Guaranteed (Honest Limits)
- **Not Multi-Tenant Enterprise Isolation:** This starter uses standard application-level filtering (`user=request.user`), not database schema separation or row-level security policies (RLS).
- **Not HIPAA or Direct Card Processing Compliant:** The application does not include audit logging streams, business associate agreements (BAAs), or PCI DSS physical safeguards. Never store raw credit card numbers or sensitive health records in this starter.
- **Single Computer Storage:** A local SQLite database is stored on your current machine. If your disk is damaged or erased, your data is lost unless you manually copy your `db.sqlite3` file to a secure backup location.

