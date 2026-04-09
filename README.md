# RAZU ID Generator

Internal service for generating unique RAZU identifiers for the RAZU e-depot system.

## Documentation

- **[PROJECT_DEFINITION.md](PROJECT_DEFINITION.md)** - Complete functional specification, API documentation, and validation rules
- **[TEST_SCENARIOS.md](TEST_SCENARIOS.md)** - Comprehensive test scenarios
- **[CODING_GUIDELINES.md](CODING_GUIDELINES.md)** - Coding standards

## Quick Start

### Installation

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running

```bash
# Development
python app.py

# Production
gunicorn app:app --bind 0.0.0.0:8000
```

Service runs on `http://localhost:8000`

### Testing

```bash
pytest -v
pytest --cov=src --cov-report=html
```

### Database

The service creates `identifiers.db` automatically on first run. To reset identifier generation, simply delete this file.

## API Example

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "producer": "g0352",
    "dataset": "689",
    "type": "Informatieobject",
    "aggregationlevel": "Archiefstuk",
    "inventarisnummer": "INV-2024-001",
    "filepath": "data/documents/file.pdf"
  }'
```

Returns:
```json
{
  "identifier": "nl-wbdrazu-g0352-689-1",
  "is_new": true
}
```

See [PROJECT_DEFINITION.md](PROJECT_DEFINITION.md) for complete API documentation and validation rules.

## Development

This project was developed with AI assistance following a documentation-first approach. See [CONTRIBUTING.md](CONTRIBUTING.md) for the development workflow.
