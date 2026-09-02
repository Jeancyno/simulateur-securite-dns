# Simulateur Sécurité DNS

Un simulateur pour tester et analyser la sécurité des configurations DNS.

## Structure du projet

- `frontend/` - Application React.js
- `backend/` - API Django
- `docs/` - Documentation
- `tests/` - Tests

## Installation

```bash
# Backend
cd backend
python -m venv venv
#pour linux
source .venv/bin/activate
pip install -r requirements.txt
python manage.py runserver

#pour windows
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver

# Frontend
cd frontend
npm install
```

## Configuration

Copiez `.env.example` vers `.env` et configurez les variables d'environnement nécessaires.
