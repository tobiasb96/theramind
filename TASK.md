PsychDocs Quick-Start – uv, Django 5 & shadcn-django

Ziel – In < 10 Minuten eine lauffähige App mit Tailwind + shadcn-UI, Postgres-Docker und Whisper-/GPT-Hooks auf die Beine stellen.

Voraussetzungen
• Python ≥ 3.12   • uv (🔗 https://github.com/astral-sh/uv)   • Docker für PostgreSQL

⚠️ Dockerfile wird nicht gebraucht → wir starten mit manage.py runserver im Host.

⸻

1 | Projektstruktur anlegen

mkdir psych-docs && cd psych-docs
uv venv .venv              # erstellt virtuelles Env
source .venv/bin/activate  # aktivieren


⸻

2 | Abhängigkeiten deklarieren & installieren

requirements.txt (anlegen oder ergänzen)

Django>=5,<6
psycopg[binary]           # Postgres-Treiber
shadcn-django             # UI-Komponenten-CLI
django-tailwind-cli       # Tailwind ohne Node
openai                    # Whisper / GPT (dev-phase)
python-docx               # (Bericht-Export)

Install – ein Befehl, blitzschnell dank uv:

uv pip install -r requirements.txt

uv-Vorteil:  Dependency-Resolver & Wheel-Builder in Rust → ~10× schneller als pip.

⸻

3 | Django-Projekt & Basis-Apps

django-admin startproject config .
python manage.py startapp core      # Patienten, Settings
python manage.py startapp therapy   # Sessions, Notes, Recordings
python manage.py startapp ai        # STT & LLM-Helpers

Tipp: Leg dir gleich ein core/utils.py für Shared Helper an (slugify, uuid usw.).

⸻

4 | Postgres – Docker Compose

Du hast bereits eine docker-compose.yml mit Postgres – stelle sicher, dass folgende ENV in .env liegen und settings.py darauf zugreift:

DATABASE_URL=postgres://psych:changeme@localhost:5432/psychdocs

config/settings.py (Ausschnitt)

import dj_database_url
DATABASES = {
    "default": dj_database_url.parse(os.environ["DATABASE_URL"], conn_max_age=600, ssl_require=False)
}
MEDIA_ROOT = BASE_DIR / "media"
STATIC_ROOT = BASE_DIR / "staticfiles"

Dann:

# Terminal 1: Postgres starten
docker compose up db
# Terminal 2: Migrationen
python manage.py migrate


⸻

5 | Tailwind + shadcn-django einrichten

5.1 Tailwind CLI (keine Node-Abhängigkeit)

python -m django_tailwind_cli init   # erzeugt tailwind.config.js & input.css

Watch-Build in zweitem Tab:

npx tailwindcss -i input.css -o static/css/output.css --watch

5.2 shadcn-CLI

uv pip install --break-system-packages shadcn-django    # falls nicht global
shadcn_django init                                     # legt templates/cotton & tokens an
shadcn_django add button card table form               # erste Komponenten

Die CLI kopiert HTML-Snippets in dein Projekt, Tailwind-Klassen ready-to-go.

⸻

6 | Basistemplate & Navbar

templates/base.html (Kurzversion)

{% load static %}
<!doctype html>
<html lang="de" class="h-full">
<head>
  <meta charset="utf-8">
  <link rel="stylesheet" href="{% static 'css/output.css' %}">
  <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
  <title>{% block title %}PsychDocs{% endblock %}</title>
</head>
<body class="h-full bg-muted/40">
  <div class="container mx-auto px-6 py-4">
    {% include 'partials/navbar.html' %}
    {% block content %}{% endblock %}
  </div>
</body>
</html>


⸻

7 | Erste Modelle

# core/models.py
class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)

class Session(models.Model):
    patient  = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date     = models.DateTimeField(default=timezone.now)
    duration = models.PositiveIntegerField()

class AudioRecording(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    audio   = models.FileField(upload_to="audio/")
    created = models.DateTimeField(auto_now_add=True)

class Transcription(models.Model):
    recording  = models.OneToOneField(AudioRecording, on_delete=models.CASCADE)
    text       = models.TextField()
    confidence = models.FloatField(null=True, blank=True)

Migrations ausführen – python manage.py makemigrations && python manage.py migrate.

⸻

8 | STT-/LLM-Hooks (synchrones MVP)

# ai/services.py
from openai import OpenAI
client = OpenAI()

def transcribe(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return client.audio.transcriptions.create(model="whisper-1", file=f).text

def summarize(text: str) -> str:
    msg = [{"role": "user", "content": f"Fasse folgenden Text in 150 Wörtern zusammen: {text}"}]
    return client.chat.completions.create(model="gpt-4o-mini", messages=msg).choices[0].message.content.strip()

⚡️ Für Pilotphase okay – später Celery-Tasks statt blockierendem Call.

⸻

9 | Server starten

python manage.py runserver 0.0.0.0:8000

Dashboard sollte erreichbar sein ➜ http://localhost:8000

⸻

10 | Nächste Schritte
	1.	CRUD-Views mit Django Generic Views + HTMX.
	2.	Session-Detail: Audio-Recorder (MediaRecorder API) ➜ Upload Endpoint.
	3.	Settings-Singleton: Transkript-TTL (Stunden)
	4.	Celery & Redis nachrüsten, sobald Audio > 30 Sek.

⸻

✨ Happy Building!  Alles Weitere – Tests, Auth, DSGVO – könnt ihr sukzessive ergänzen.