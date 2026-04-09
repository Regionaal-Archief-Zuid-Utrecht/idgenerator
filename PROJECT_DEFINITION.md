# RAZU ID Generator

## Overview

**idgenerator** is a Python REST API service that generates unique RAZU identifiers for resources in the RAZU e-depot system. It ensures that each entity receives a single, permanent identifier that follows the RAZU identification principles.

**Target audience**: This is an internal service intended for developers working on ingest processes for the RAZU e-depot.

## RAZU Identifiers

### Purpose

RAZU identifiers uniquely identify entities stored in the RAZU e-depot system. They serve as the main discriminating component of other identifiers, such as linked data URIs.

**Key principle**: RAZU identifiers may never be reused.

### Structure

The RAZU identifier follows a strict five-part pattern based on the origin of the data:

```
nl-wbdrazu-{producer}-{dataset}-{unique-number}
```

**Example:**
```
nl-wbdrazu-k50907905-689-815224
```

### Structure Rules

- All characters are lowercase
- Five parts separated by dashes (`-`)
- Parts consist of lowercase letters and numbers only
- **Part 1**: Always `nl` (country code for the Netherlands)
- **Part 2**: Always `wbdrazu` (ISIL code for RAZU)
- **Part 3**: Producer identifier (e.g., `k50907905`, `g0352`)
- **Part 4**: Archive/dataset identifier (e.g., `689`)
- **Part 5**: Unique integer number (e.g., `815224`)

## REST API

### Endpoints

#### Generate Identifier

```
POST /generate
Content-Type: application/json
```

#### Health Check

```
GET /health
```

Returns service status and database connectivity.

### Request Parameters

| Parameter | Required | Type | Description | Valid Values |
|-----------|----------|------|-------------|--------------||
| `producer` | Yes | string | Producer identifier | e.g., `g0352`, `k50907905` |
| `dataset` | Yes | string | Archive/dataset identifier | Any non-empty string |
| `type` | Yes | string | Entity type | `Informatieobject` or `Bestand` |
| `aggregationlevel` | Yes | string | Aggregation level | `Archief`, `Serie`, `Dossier`, or `Archiefstuk` |
| `inventarisnummer` | Conditional* | string | Inventory number | Any string (trimmed) |
| `filepath` | Conditional* | string | File path | Any string |

**Conditional requirements based on `aggregationlevel`:**
- **`Archief` or `Serie`**: `inventarisnummer` and `filepath` must NOT be provided
- **`Dossier`**: `inventarisnummer` is REQUIRED, `filepath` must NOT be provided
- **`Archiefstuk`**: Both `inventarisnummer` and `filepath` are REQUIRED

### Request Example

```json
{
  "producer": "g0352",
  "dataset": "689",
  "type": "Informatieobject",
  "aggregationlevel": "Archiefstuk",
  "inventarisnummer": "INV-2024-001",
  "filepath": "data /documents/file.pdf"
}
```

### Response

#### Success Response (200 OK)

```json
{
  "identifier": "nl-wbdrazu-g0352-689-815224",
  "is_new": true
}
```

**Fields:**
- `identifier`: The generated or retrieved RAZU identifier
- `is_new`: 
  - `true` - New identifier created for this unique combination
  - `false` - Existing identifier retrieved from database

#### Error Response (400 Bad Request)

```json
{
  "error": "Validation error message"
}
```

## Business Logic

### Uniqueness Key

The system determines uniqueness based on the combination of all six parameters:
- `producer`
- `dataset`
- `type`
- `aggregationlevel`
- `inventarisnummer`
- `filepath`

### Identifier Generation Flow

1. **Validation**: Check if all required parameters are present and valid
2. **Lookup**: Search database for existing combination
3. **Decision**:
   - **If combination exists**: Return stored identifier with `is_new: false`
   - **If combination is new**:
     - Get the highest unique number for this `producer` + `dataset` combination
     - Increment by 1
     - Create identifier: `nl-wbdrazu-{producer}-{dataset}-{new-number}`
     - Store combination + unique number in database
     - Return identifier with `is_new: true`

### Example Scenarios

**Scenario 1: First request for a producer/dataset**
- Request: `producer=g0352`, `dataset=689`, other params...
- No previous identifiers exist
- Generates: `nl-wbdrazu-g0352-689-1`
- Returns: `is_new: true`

**Scenario 2: Second unique combination for same producer/dataset**
- Request: `producer=g0352`, `dataset=689`, different params...
- Previous highest number: `1`
- Generates: `nl-wbdrazu-g0352-689-2`
- Returns: `is_new: true`

**Scenario 3: Duplicate request**
- Request: Exact same parameters as Scenario 1
- Finds existing identifier: `nl-wbdrazu-g0352-689-1`
- Returns: `is_new: false`

## Validation Rules

All requests are validated before processing:

- ✓ All required parameters must be present
- ✓ No empty values allowed for any parameter
- ✓ `type` must be exactly `Informatieobject` or `Bestand`, case sensitive
- ✓ `aggregationlevel` must be one of: `Archief`, `Serie`, `Dossier`, `Archiefstuk`, case sensitive
- ✓ `inventarisnummer` is trimmed of leading/trailing whitespace
- ✓ All string values are validated as non-empty after trimming
- ✓ Conditional parameter requirements based on `aggregationlevel` (see Request Parameters section)

## Data Persistence

### Database

The system uses **SQLite** for persistence.

### Stored Data

For each generated identifier, the following is stored:
- Producer identifier
- Dataset identifier
- Entity type
- Aggregation level
- Inventory number (if provided)
- File path (if provided)
- Generated unique number

### Concurrency

The service implements database locking to handle concurrent requests safely. When multiple requests arrive simultaneously for the same `producer` + `dataset` combination, the database ensures:
- Only one transaction can increment the unique number at a time
- No duplicate unique numbers are generated
- Requests are processed sequentially when necessary

## Deployment

### Running the Service

The service can be started in two ways:

1. **Manual (Terminal)**:
   ```bash
   gunicorn app:app --bind 0.0.0.0:8000
   ```

2. **Systemd** (optional):
   - Create a systemd service unit file
   - Enable and start the service
   - Service runs automatically on system boot

### Requirements

- Python 3.x
- Dependencies as specified in `requirements.txt`
- SQLite database file (created automatically on first run)

## Testing

Comprehensive test scenarios are documented in [TEST_SCENARIOS.md](TEST_SCENARIOS.md). This includes:
- Validation tests (required parameters, enum values, aggregation level rules)
- Identifier generation tests (sequential numbering, uniqueness, duplicates)
- Concurrency tests (race conditions, database locking)
- API tests (endpoints, status codes, error handling)
- Edge cases and performance tests

##  Coding Principles

The principles in [CODING_GUIDELINES.md](CODING_GUIDELINES.md) apply.