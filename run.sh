#!/bin/bash
cd "$(dirname "$0")"

unset PYTHONPATH
unset PYTHONHOME

if [ ! -f .venv/bin/python ] || ! .venv/bin/python -c "import django" 2>/dev/null; then
  echo "Sozdaem venv ili pereustanavlivaem zavisimosti..."
  rm -rf .venv
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
fi

if [ ! -f .env ]; then
  cp .env.example .env
fi

.venv/bin/python manage.py migrate 2>/dev/null || true
echo "--- Server: http://127.0.0.1:8001 (esli 8000 zanyat) ---"
exec .venv/bin/python manage.py runserver 8001
