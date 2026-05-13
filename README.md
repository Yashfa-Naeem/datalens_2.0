# DataLens

## 1. Project purpose

**DataLens** is a web dashboard for exploring **2015 U.S. flight delay** data: millions of flight rows with carriers, airports, routes, and delay metrics. You can **upload** the official CSVs, **filter** and **chart** patterns, and use a **chat assistant** (powered by Groq) that answers questions using safe queries over your loaded data—so you get analytics without writing SQL yourself.

---

## 2. Prerequisites

Before you start, install these on your computer (Windows examples below; macOS/Linux steps are similar).

| Tool | Version | What it is |
|------|---------|--------------|
| **Python** | **3.11 or newer** | Runs the DataLens API server |
| **Node.js** | **18 or newer** (20+ recommended) | Runs the website build tools and dev server |
| **uv** | Latest | Installs and runs Python packages for the backend |
| **npm** | Comes with Node | Installs JavaScript libraries for the frontend |

You also need a **Groq API key** for chat (see [section 4](#4-how-to-get-a-groq-api-key)).

---

## 3. Step-by-step setup (for new users)

Follow these in order. If anything fails, see [Troubleshooting](#7-troubleshooting).

### Step A — Get the project on your computer

1. If you received a **ZIP** file, extract it so you have a folder named `datalens_2.0` (this README should sit inside that folder next to `backend` and `frontend`).
2. If you use **Git**, clone the repository and open the same `datalens_2.0` folder.

### Step B — Install Python

1. Go to [https://www.python.org/downloads/](https://www.python.org/downloads/).
2. Download **Python 3.11** or newer for Windows.
3. Run the installer. **Important:** check **“Add python.exe to PATH”**, then click **Install Now**.
4. Close and reopen **Command Prompt** or **PowerShell** after installing.

**Check it worked:** open PowerShell and run:

```powershell
python --version
```

You should see `Python 3.11.x` or higher.

### Step C — Install Node.js (includes npm)

1. Go to [https://nodejs.org/](https://nodejs.org/).
2. Download the **LTS** version and run the installer (defaults are fine).
3. Close and reopen your terminal.

**Check it worked:**

```powershell
node --version
npm --version
```

`node` should be **v18** or higher.

### Step D — Install uv (Python package runner)

1. Open PowerShell.
2. Run the official installer command from [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/) (on Windows, the docs provide a PowerShell one-liner—copy it from there so you always get the latest script).

**Check it worked:**

```powershell
uv --version
```

### Step E — Install backend (Python) dependencies

1. Open **PowerShell**.
2. Go to the project’s **backend** folder (change the path if your folder lives somewhere else):

```powershell
cd "C:\Users\Shahzad Malik\Desktop\datalens_2.0\backend"
```

3. Run:

```powershell
uv sync
```

Wait until it finishes without errors. This creates a virtual environment and downloads libraries like FastAPI and Pandas.

### Step F — Install frontend (website) dependencies

1. In PowerShell, go to the **frontend** folder:

```powershell
cd "C:\Users\Shahzad Malik\Desktop\datalens_2.0\frontend"
```

2. Run:

```powershell
npm install
```

Wait until it completes. This downloads React, Vite, Tailwind, Recharts, etc.

### Step G — Add your Groq API key

1. Open **Notepad**.
2. Create a new file with this line (paste your real key from Groq):

```text
GROQ_API_KEY=paste_your_key_here
```

3. Save the file as **`.env`** inside the **`backend`** folder, for example:

`C:\Users\Shahzad Malik\Desktop\datalens_2.0\backend\.env`

> **Note:** If Windows won’t let you save a file starting with `.`, save as `env.txt`, then rename it to `.env` in File Explorer, or in Notepad use quotes in the file name: `.env`

4. Never share this file or upload it to the internet—it is like a password.

### Step H — (Optional) Add your flight CSV files

Place `flights.csv`, `airlines.csv`, and `airports.csv` somewhere easy to find (for example a `data` folder on your PC). You will **upload** them through the DataLens website after the app is running.

---

## 4. How to get a Groq API key

1. Open [https://console.groq.com/](https://console.groq.com/) in your browser.
2. **Sign up** or **log in** (you can use a Google or GitHub account if offered).
3. Open the **API Keys** section in the Groq console.
4. Click **Create API Key**, give it a name (e.g. `datalens`), and **copy** the key immediately—it is shown only once.
5. Paste the key into your `backend\.env` file as:

```text
GROQ_API_KEY=your_copied_key_here
```

6. Save the file. Restart the backend server if it was already running.

If chat shows an error about the key, see [Troubleshooting](#7-troubleshooting).

---

## 5. Single command to start the application

DataLens needs **two** programs at once: the **API** (backend) and the **website** (frontend). The line below starts the API in a **new window**, then starts the site in your **current** window.

1. Open **PowerShell**.
2. **Go to the project folder** (the one that contains `backend` and `frontend`):

```powershell
cd "C:\Users\Shahzad Malik\Desktop\datalens_2.0"
```

3. Run this **one line** (copy all of it):

```powershell
Start-Process powershell -ArgumentList '-NoExit','-Command',"cd '$((Get-Location).Path)\backend'; uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"; Set-Location .\frontend; npm run dev
```

What you should see:

- A **second** PowerShell window running the API on **http://127.0.0.1:8000**
- Your **first** window running the site, usually at **http://localhost:5173**

Open **http://localhost:5173** in Chrome or Edge.

**To stop:** press `Ctrl+C` in the frontend window, then close the API window (or press `Ctrl+C` there too).

> If the one-liner fails (e.g. older PowerShell), use two terminals manually: in one, `cd backend` then `uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`; in the other, `cd frontend` then `npm run dev`.

---

## 6. How to run tests

### Backend — pytest

From the **`backend`** folder:

```powershell
cd "C:\Users\Shahzad Malik\Desktop\datalens_2.0\backend"
uv sync
uv run pytest
```

If you see “command not found” or missing `pytest`, add it to the project’s dev dependencies with `uv` and run `uv sync` again.

Useful variants:

```powershell
uv run pytest -q
uv run pytest tests\test_health.py -v
```

### Frontend — Vitest

Vitest must be listed in `frontend\package.json` (and installed with `npm install`). Then from **`frontend`**:

```powershell
cd "C:\Users\Shahzad Malik\Desktop\datalens_2.0\frontend"
npm install
npm run test
```

If `npm run test` does not exist yet, the team needs to add Vitest to the project (see `SPEC.md`). Until then, you can still run **lint**:

```powershell
npm run lint
```

---

## 7. Troubleshooting

### “`python` is not recognized”

Python is not on your PATH. Re-run the Python installer and enable **Add to PATH**, or reinstall Python from [python.org](https://www.python.org/downloads/).

### “`node` or `npm` is not recognized”

Install Node.js LTS from [nodejs.org](https://nodejs.org/) and **restart** your terminal.

### “`uv` is not recognized”

Install `uv` using the official instructions at [Astral uv installation](https://docs.astral.sh/uv/getting-started/installation/). Close and reopen PowerShell.

### “`uv sync` fails” or SSL / network errors

Check your internet connection, corporate firewall, or VPN. Try again on a stable network.

### Website loads but charts or data fail / “Network Error”

- Confirm the **API window** is still open and shows Uvicorn running.
- Open [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health) in the browser—you should see something like `{"status":"ok"}`.
- The frontend expects the API on **port 8000**. If you changed the port, update the frontend API URL to match.

### Chat returns **503** or “GROQ_API_KEY”

- Your `backend\.env` file is missing, in the wrong folder, or the key line is wrong.
- Fix the file, save it, and **restart** the backend server.
- Confirm the key is still valid in [Groq console](https://console.groq.com/).

### CORS errors in the browser console

The backend only allows certain origins (e.g. `http://localhost:5173`). Use that URL, not a different port, unless your team updates CORS in the FastAPI app.

### Upload is slow or fails on huge CSVs

Large files take time. The app may enforce **row or preview limits** to protect memory—try a smaller sample file or ask the team about limits in `upload` settings.

### Port already in use (`8000` or `5173`)

Something else is using that port. Either close the other program or change the port in the `uvicorn` command / Vite config (and update the frontend base URL to match).

### PowerShell “execution policy” blocks scripts

If you later run `.ps1` scripts and get blocked, your administrator may need to allow scripts, or run only the commands from this README in an interactive PowerShell window.

---

## 8. Team members

| Name | Area |
|------|------|
| **Yashfa Naeem** | Backend (FastAPI, data, SQLite, APIs) |
| **[Friend 1 name]** | Frontend (React, Vite, Tailwind, charts) |
| **[Friend 2 name]** | LLM / Chat (Groq integration, prompts, tool-calling) |

Replace **[Friend 1 name]** and **[Friend 2 name]** with your teammates’ names when you finalize the README.

---

## More documentation

See **`SPEC.md`** in the same folder for objectives, project layout, code style, testing strategy, and contributor boundaries.
