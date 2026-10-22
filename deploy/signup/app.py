"""Liste d'attente ARKA : recoit une adresse e-mail et l'ajoute a un fichier CSV.

Une seule route, POST /api/inscription, corps JSON {"email": ..., "lang": ...}.
Bibliotheque standard uniquement. Le fichier vit hors du depot (/data, monte depuis le VPS).
"""
import csv
import json
import os
import re
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DATA = os.environ.get('DATA_FILE', '/data/inscriptions.csv')
ORIGINS = {o for o in os.environ.get('ALLOWED_ORIGINS', '').split(',') if o}
MAX_BODY = 1024
MAX_FILE = 5 * 1024 * 1024
PER_IP, PER_IP_WINDOW = 5, 3600
PER_DAY = 1000
LANGS = {'fr', 'de', 'en'}
# Pas de virgule, guillemet ni chevron ; pas de premier caractere qu'un tableur lirait comme une formule.
EMAIL = re.compile(r'^(?![=+\-@])[^\s@,;"<>\\]{1,64}@[^\s@,;"<>\\]{1,190}\.[A-Za-z]{2,24}$')

lock = threading.Lock()
hits: dict[str, list[float]] = {}
day = {'key': '', 'n': 0}


def known(email: str) -> bool:
    if not os.path.exists(DATA):
        return False
    with open(DATA, newline='', encoding='utf-8') as f:
        return any(len(r) > 1 and r[1] == email for r in csv.reader(f))


def allow(ip: str) -> bool:
    now = time.time()
    recent = [t for t in hits.get(ip, []) if now - t < PER_IP_WINDOW]
    if len(hits) > 10000:
        hits.clear()
    if len(recent) >= PER_IP:
        hits[ip] = recent
        return False
    hits[ip] = recent + [now]
    today = time.strftime('%Y-%m-%d')
    if day['key'] != today:
        day.update(key=today, n=0)
    day['n'] += 1
    return day['n'] <= PER_DAY


class Handler(BaseHTTPRequestHandler):
    server_version = 'arka'
    sys_version = ''

    def reply(self, code: int) -> None:
        body = json.dumps({'ok': code == 200}).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path != '/api/inscription':
            return self.reply(404)
        origin = self.headers.get('Origin')
        if ORIGINS and origin and origin not in ORIGINS:
            return self.reply(403)
        try:
            size = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            return self.reply(400)
        if size <= 0 or size > MAX_BODY:
            return self.reply(413)
        try:
            data = json.loads(self.rfile.read(size))
        except (ValueError, UnicodeDecodeError):
            return self.reply(400)
        if not isinstance(data, dict):
            return self.reply(400)
        if data.get('site'):  # champ invisible : seuls les robots le remplissent
            return self.reply(200)
        email = str(data.get('email', '')).strip().lower()
        lang = str(data.get('lang', ''))[:2]
        if not EMAIL.match(email):
            return self.reply(400)
        # Traefik ajoute l'adresse reelle du client en dernier.
        ip = self.headers.get('X-Forwarded-For', self.client_address[0]).split(',')[-1].strip()
        with lock:
            if not allow(ip):
                return self.reply(429)
            if os.path.exists(DATA) and os.path.getsize(DATA) > MAX_FILE:
                return self.reply(507)
            if not known(email):
                new = not os.path.exists(DATA)
                with open(DATA, 'a', newline='', encoding='utf-8') as f:
                    w = csv.writer(f)
                    if new:
                        w.writerow(['date', 'email', 'langue'])
                    w.writerow([datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M'), email, lang if lang in LANGS else ''])
        self.reply(200)

    def do_GET(self) -> None:
        self.reply(404)

    def log_message(self, fmt: str, *args) -> None:  # pas d'adresses e-mail ni d'IP dans les journaux
        pass


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
