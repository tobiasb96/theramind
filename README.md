# TheraMind

A Django-based therapy session management system with AI-powered transcription and intelligent report generation.

## 🎯 Goal

TheraMind streamlines therapy session documentation by automatically transcribing audio recordings and generating structured session notes using AI. It helps therapists focus on their clients while maintaining comprehensive documentation.

## ✨ Features

- **Audio Recording & Transcription**: Record therapy sessions and automatically transcribe them using OpenAI Whisper
- **AI-Powered Session Notes**: Generate structured session notes from transcripts using customizable templates
- **Document Templates**: Create and manage custom report templates for different therapy contexts
- **Session Management**: Organize therapy sessions with notes, summaries, and related documents
- **Report Generation**: Generate comprehensive reports linking multiple sessions
- **PDF Export**: Export session notes and reports to PDF format
- **Dashboard**: Quick access to recent sessions and documents with fast creation tools

## 🏗️ Project Structure

```
theramind/
├── config/              # Django settings and configuration
├── core/               # Core services (PDF export, utilities)
├── dashboard/          # Main dashboard interface
├── therapy_sessions/   # Session management, audio processing, AI transcription
├── reports/            # Report generation and management
├── document_templates/ # Template system for AI-generated content
├── templates/          # HTML templates
├── static/            # Static files (CSS, JS)
└── media/             # User uploads (audio files)
```

### Key Apps

- **therapy_sessions**: Handles session creation, audio uploads, transcription, and AI-generated notes
- **reports**: Manages report creation and generation with AI assistance
- **document_templates**: Provides customizable templates for AI content generation
- **dashboard**: Central hub for quick access to all features

## 🚀 Developer Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Docker & Docker Compose
- OpenAI API key

### 1. Install Dependencies

```bash
# Install Python dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate
# or use: uv run <command> for individual commands
```

### 2. Database Setup

```bash
# Start PostgreSQL with Docker
docker compose up -d postgres

# The database will be available at:
# - Host: localhost
# - Port: 5432
# - Database: postgres
# - Username: postgres
# - Password: postgres
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```bash
# Copy from example (create if it doesn't exist)
cp .env.example .env
```

**Required environment variables:**

```env
# OpenAI API Configuration (REQUIRED)
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration (Optional - defaults to local PostgreSQL)
DATABASE_URL=postgres://postgres:postgres@localhost:5432/theramind

# Django Configuration (Optional - has defaults)
SECRET_KEY=your_secret_key_here
DEBUG=True
```

### 4. Database Migration

```bash
# Run migrations to set up the database
python manage.py migrate

# Create a superuser (optional)
python manage.py createsuperuser

# Load default document templates (optional)
python manage.py seed_templates
```

### 5. Frontend Assets

```bash
# Install Node.js dependencies for Tailwind CSS
npm install

# Build CSS assets
npm run build
```

### 6. Run the Development Server

```bash
# Start the Django development server
python manage.py runserver

# Application will be available at: http://localhost:8000
```

## 🔧 Additional Setup

### Optional Services

```bash
# Start Redis (for future caching/background tasks)
docker compose up -d redis
```

### Development Commands

```bash
# Watch and rebuild CSS during development
npm run watch

# Run tests
python manage.py test

# Create new migrations after model changes
python manage.py makemigrations
```

## 🔑 Required Secrets

### OpenAI API Key

1. Sign up at [OpenAI](https://platform.openai.com/)
2. Create an API key in your dashboard
3. Add it to your `.env` file as `OPENAI_API_KEY`

**Note**: The OpenAI API key is required for:
- Audio transcription (Whisper API)
- AI-generated session notes and reports (GPT API)

### Database URL

The default configuration uses the local PostgreSQL instance from Docker Compose. Only modify `DATABASE_URL` if you're using a different database setup.

## 🎮 Usage

1. **Start a Session**: Create a new therapy session from the dashboard
2. **Upload Audio**: Record or upload audio files to the session
3. **Transcription**: Audio is automatically transcribed using OpenAI Whisper
4. **Generate Notes**: AI creates structured session notes based on your selected template
5. **Create Reports**: Generate comprehensive reports linking multiple sessions
6. **Export**: Download session notes and reports as PDF files

## 📝 Notes

- Audio files are stored in `media/audio/` and automatically processed
- Transcriptions can be configured to auto-delete after a specified time
- Document templates can be customized for different therapy approaches
- The system supports German language by default but can be configured for other languages