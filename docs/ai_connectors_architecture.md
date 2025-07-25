# AI Connectors Architecture

## Overview

The AI connectors system provides a clean, extensible architecture for integrating various AI services (transcription and LLM) into the application. The system follows SOLID principles and uses the Abstract Factory pattern to enable easy addition of new AI providers.

## Architecture

### Directory Structure

```
core/ai_connectors/
├── __init__.py                    # Public API exports
├── base/                          # Abstract base classes
│   ├── __init__.py
│   ├── exceptions.py              # Custom exceptions
│   ├── transcription.py           # GenericTranscriptionConnector
│   └── llm.py                     # GenericLLMConnector
├── openai/                        # OpenAI implementations
│   ├── __init__.py
│   ├── transcription.py           # OpenAIWhisperConnector
│   └── llm.py                     # OpenAILLMConnector
└── factory.py                     # Connector factory with singletons
```

### Key Components

#### 1. Abstract Base Classes

**GenericTranscriptionConnector**
- Defines interface for audio transcription services
- Methods: `transcribe()`, `is_available()`, `get_supported_formats()`, `reinitialize()`
- Returns `TranscriptionResult` with text, processing time, and metadata

**GenericLLMConnector**
- Defines interface for text generation services
- Methods: `generate_text()`, `is_available()`, `get_available_models()`, `reinitialize()`
- Uses `LLMGenerationParams` for configuration
- Returns `LLMResult` with text, token usage, and model info

#### 2. OpenAI Implementations

**OpenAIWhisperConnector**
- Implements transcription using OpenAI Whisper API
- Supports: mp3, wav, m4a, webm, flac formats
- Handles timing and error reporting

**OpenAILLMConnector**
- Implements text generation using OpenAI GPT models
- Supports: gpt-4.1-nano, gpt-4, gpt-3.5-turbo
- Tracks token usage and model information

#### 3. Factory Pattern

**ConnectorFactory**
- Creates connector instances based on configuration
- Supports provider selection via settings
- Extensible for future providers (Azure, Anthropic, etc.)

**Singleton Management**
- `get_transcription_connector()` - Global transcription connector
- `get_llm_connector()` - Global LLM connector
- `reinitialize_connectors()` - Refresh after settings changes

### Service Layer Integration

#### SessionService (formerly TranscriptionService)
- Handles session-specific AI operations
- Uses both transcription and LLM connectors
- Provides gender context building helper
- Methods: `create_session_notes_with_template()`, `summarize_session_notes()`

#### ReportService
- Generates therapy reports using LLM connector
- Integrates with UnifiedInputService for context
- Provides gender context building helper
- Methods: `generate_with_template()`, `generate()`

#### UnifiedInputService
- Processes audio inputs using transcription connector
- Handles document text extraction
- Combines multiple input sources

## Benefits

### SOLID Principles Compliance

1. **Single Responsibility**: Each connector handles one specific task
2. **Open/Closed**: Easy to add new providers without modifying existing code
3. **Liskov Substitution**: All implementations are interchangeable
4. **Interface Segregation**: Separate interfaces for transcription and LLM
5. **Dependency Inversion**: Services depend on abstractions, not concrete implementations

### Extensibility

Adding a new provider (e.g., Azure OpenAI) requires:

1. Create implementation classes in `core/ai_connectors/azure/`
2. Register in `ConnectorFactory._transcription_connectors` and `_llm_connectors`
3. Add configuration settings for provider selection

### Error Handling

- Custom exception hierarchy: `AIConnectorError`, `TranscriptionError`, `LLMError`, `ConfigurationError`
- Proper error propagation and logging
- Graceful degradation when services unavailable

### Configuration

Providers can be selected via Django settings:
```python
DEFAULT_TRANSCRIPTION_PROVIDER = 'openai'  # or 'azure', 'google'
DEFAULT_LLM_PROVIDER = 'openai'           # or 'azure', 'anthropic'
```

## Usage Examples

### Basic Usage

```python
from core.ai_connectors import get_transcription_connector, get_llm_connector
from core.ai_connectors.base.llm import LLMGenerationParams

# Transcription
transcription_connector = get_transcription_connector()
if transcription_connector.is_available():
    result = transcription_connector.transcribe("/path/to/audio.mp3")
    print(result.text)

# Text Generation
llm_connector = get_llm_connector()
if llm_connector.is_available():
    params = LLMGenerationParams(max_tokens=500, temperature=0.3)
    result = llm_connector.generate_text(
        "You are a helpful assistant",
        "Write a summary",
        params
    )
    print(result.text)
```

### Service Integration

```python
from therapy_sessions.services import get_session_service
from reports.services import ReportService

# Session notes generation
session_service = get_session_service()
notes = session_service.create_session_notes_with_template(
    transcript_text, template, existing_notes, patient_gender
)

# Report generation
report_service = ReportService()
report_content = report_service.generate_with_template(report, template)
```

## Migration Notes

### Changes Made

1. **Renamed Services**: `TranscriptionService` → `SessionService`
2. **New Imports**: `from core.ai_connectors import get_transcription_connector, get_llm_connector`
3. **Removed**: Old `core/connector.py` file
4. **Updated**: All service classes to use new connectors

### Backward Compatibility

- `get_transcription_service()` still works as an alias to `get_session_service()`
- All existing method signatures remain the same
- No changes required in templates or views

## Testing

Run the test script to verify the system:

```bash
python test_connectors.py
```

This will test:
- Connector instantiation
- Availability checks  
- Service integration
- Basic functionality (if API keys configured) 