## FastAPI Hello World

Minimal FastAPI project with a root endpoint and a health check.

### Setup

1. Create and activate a virtual environment (optional but recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Run

```bash
uvicorn app.main:app --reload
```

The app will be available at `http://127.0.0.1:8000/`.

- `GET /` → `{ "message": "Hello, World!" }`
- `GET /health` → `{ "status": "ok" }`

### Project layout

```
fast/
├─ app/
│  └─ main.py
├─ requirements.txt
└─ README.md
```


