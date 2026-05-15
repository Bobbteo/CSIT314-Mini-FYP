# CSIT314-Mini-FYP

Flask web app for managing fundraising activities, donations, accounts, and reports.

## Prerequisites

- [Python 3](https://www.python.org/downloads/) 3.10 or newer
- Windows PowerShell (commands below) or any shell with equivalent paths

## Run the website

From the repository root (`CSIT314-Mini-FYP`):

### 1) Create a virtual environment (first time only)

```powershell
python -m venv .venv
```

### 2) Install dependencies

```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
```

### 3) Start the app

```powershell
.\.venv\Scripts\python fundraising_system\run.py
```

On startup the app initializes SQLite at `fundraising_system/fundraising.db` and loads demo data (categories, accounts, campaigns, donations). An internet connection is optional; seeding uses the RandomUser API when available and falls back to Faker locally.

### 4) Open in browser

Go to [http://127.0.0.1:5000](http://127.0.0.1:5000).

### Stop the server

Press `Ctrl+C` in the terminal running Flask.

## Demo logins

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin` |
| Fundraiser, doner, manager | `fundraiser_*`, `doner_*`, `manager_*` (see Accounts in the admin UI) | `password123` |

**Note:** Each time you start the app, the database is reset and reseeded. Any changes made during a previous session are not kept.

## Troubleshooting

- **`ModuleNotFoundError` (e.g. `faker`, `requests`)** — Run step 2 again from the repo root.
- **Port already in use** — Stop the other Flask process or change the port in `fundraising_system/run.py`.
- **Fresh database without restarting** — Delete `fundraising_system/fundraising.db` and run step 3 again.

## Project layout

```
fundraising_system/
  app.py          # Flask routes
  run.py          # Entry point
  init_db.py      # Schema + demo seed data
  control/        # Controllers
  entity/         # Domain models
  templates/      # HTML
  static/         # CSS and images
```
