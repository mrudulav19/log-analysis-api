# LogLens — Application Log Analyzer

LogLens is a full-stack application log analysis tool built with **Python, Flask, PostgreSQL, React, and TypeScript**. It allows users to upload application log files, parse and store log entries, explore records by severity, and view useful statistics through a dashboard.

## Features

- **Log File Upload:** Upload `.log` and `.txt` files for analysis.
- **Log Parsing:** Extract timestamps, severity levels, sources, and messages from structured log lines.
- **PostgreSQL Storage:** Persist uploaded file metadata and successfully parsed log entries in a relational database.
- **Log Explorer:** Browse parsed entries, search messages, and filter logs by severity.
- **Analytics Dashboard:** View file statistics, severity distributions, and top log sources.
- **File Management:** View uploaded files and delete files with their associated database records.
- **Input Validation:** Handle unsupported file types, malformed log lines, and oversized uploads.
- **REST API:** Access file metadata and parsed log entries through Flask API endpoints.
- **Automated Tests:** Test log parsing and API behavior using pytest.

## Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | React, TypeScript, Vite |
| Backend | Python, Flask |
| Database | PostgreSQL |
| ORM and Migrations | SQLAlchemy, Flask-Migrate |
| API Testing | Postman |
| Automated Testing | pytest |
| Version Control | Git, GitHub |

## Architecture

```text
┌──────────────────────────┐
│ React + TypeScript       │
│ Dashboard                │
└────────────┬─────────────┘
             │ HTTP / REST API
             ▼
┌──────────────────────────┐
│ Flask Backend            │
│                          │
│ File Upload & Validation │
│ Log Parser               │
│ File and Entry APIs      │
└────────────┬─────────────┘
             │ SQLAlchemy
             ▼
┌──────────────────────────┐
│ PostgreSQL               │
│                          │
│ LogFile                  │
│ LogEntry                 │
└──────────────────────────┘
```

## Log Format

LogLens supports structured log lines in the following format:

```text
YYYY-MM-DD HH:MM:SS LEVEL SOURCE MESSAGE
```

Example:

```text
2026-10-28 09:15:30 INFO auth-service User login successful
2026-10-28 09:16:02 WARNING payment-service Payment retry initiated
2026-10-28 09:17:45 ERROR database Connection timeout
```

Supported severity levels include `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`.

Lines that do not match the expected format are counted as failed lines rather than stored as parsed entries.

## Prerequisites

Install the following before running the project:

- Python 3.11 or a compatible version supported by your dependencies
- PostgreSQL
- Node.js and npm
- Git

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/mrudulav19/log-analysis-api.git
cd log-analysis-api
```

### 2. Set up the Python backend

Create and activate a virtual environment.

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the backend dependencies:

```powershell
pip install -r requirements.txt
```

> Ensure `requirements.txt` is present in the repository and contains the backend dependencies before publishing.

### 3. Configure PostgreSQL

Create a PostgreSQL database named `loglens_db`, or use another database name of your choice.

Create a `.env` file in the project root and configure the database connection using the environment variable expected by the application.

Example:

```env
DATABASE_URL=postgresql://YOUR_USERNAME:YOUR_PASSWORD@localhost:5432/loglens_db
```

Replace the placeholders with your local PostgreSQL credentials. Never commit your actual `.env` file or database password.

### 4. Initialize the database

If the project uses Flask-Migrate, apply the migrations:

```powershell
flask db upgrade
```

If your Flask CLI configuration requires it, set the application entry point first:

```powershell
$env:FLASK_APP = "run.py"
flask db upgrade
```

### 5. Start the backend

From the project root, run:

```powershell
python run.py
```

The API should be available at:

```text
http://127.0.0.1:5000
```

### 6. Start the frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite development URL, typically:

```text
http://localhost:5173
```

## API Endpoints

The API base URL is `http://127.0.0.1:5000/api/v1`.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/files` | List uploaded log files |
| POST | `/files` | Upload a `.log` or `.txt` file |
| GET | `/files/<id>` | Retrieve file details |
| GET | `/files/<id>/entries` | Retrieve parsed entries for a file |
| DELETE | `/files/<id>` | Delete a file and its associated entries |

### Upload a log file

Send a `POST` request to `/api/v1/files` using `multipart/form-data` with a file field named `file`.

### Retrieve parsed entries

Send a `GET` request to `/api/v1/files/<id>/entries` to retrieve parsed log entries for the specified file.

### Delete a file

Send a `DELETE` request to `/api/v1/files/<id>` to remove the selected file and its associated records.

## Running Tests

Run the automated test suite from the project root:

```powershell
python -m pytest -v
```

The project currently has **12 passing tests** covering log parsing, file API behavior, file deletion, invalid file types, and upload-size validation.

## Project Structure

```text
log-analysis-api/
├── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── __init__.py
│   ├── config.py
│   └── extensions.py
├── frontend/
│   └── src/
├── migrations/
├── tests/
│   ├── conftest.py
│   ├── test_files_api.py
│   └── test_log_parser.py
├── .gitignore
├── run.py
└── README.md
```

## Future Improvements

- Add pagination for large log files.
- Support configurable date and time filters.
- Add log trend visualizations and advanced analytics.
- Introduce authentication and role-based access control.
- Containerize the application with Docker Compose.
- Add deployment and continuous integration workflows.

## Author

**Mrudula V.**

GitHub: [@mrudulav19](https://github.com/mrudulav19)

---

*LogLens was developed as a hands-on project to strengthen Python backend development, REST API design, SQL database integration, and full-stack application development skills.*
