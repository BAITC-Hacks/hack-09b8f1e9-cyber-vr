#!/bin/zsh
cd "$(dirname "$0")" || exit 1
if [[ ! -d .venv ]]; then
  python3 -m venv .venv || { echo 'Python 3.11+ қажет'; read '?Enter...'; exit 1; }
fi
source .venv/bin/activate
python -m pip install -r requirements.txt || { echo 'Install failed; check internet connection'; read '?Enter...'; exit 1; }
if [[ ! -f .env ]]; then
  cp .env.example .env
  echo 'Edit .env and put a NEW API key in OPENAI_API_KEY. Then run start_mac.command again.'
  read '?Press Enter...'
  exit 0
fi
if grep -q 'replace_with_your_NEW_key' .env; then
  echo 'Edit .env first and replace the placeholder with your NEW API key.'
  read '?Press Enter...'
  exit 0
fi
open http://127.0.0.1:5000
python app.py
