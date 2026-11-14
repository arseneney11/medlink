# Medlink

Integrated healthcare management system for Rwanda, developed by DIRECA Company Ltd.

**Stack:** Django 5.2 LTS, PostgreSQL 17 (Docker), HTMX + Alpine.js + Tailwind CSS (added in the next PRs).

## Local setup (Windows PowerShell)

```powershell
git clone https://github.com/<your-username>/medlink.git
cd medlink

python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements\dev.txt

Copy-Item .env.example .env      # then edit DJANGO_SECRET_KEY
docker compose up -d             # starts PostgreSQL
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/ and http://127.0.0.1:8000/health/.

Run the tests with `pytest`.

## Workflow

- `main` is always working; changes arrive through pull requests.
- Branch names: `feat/...`, `fix/...`, `chore/...`
- Commit style: `feat(patients): add duplicate detection`
- Every PR fills in the "Guidebook reference" section.
