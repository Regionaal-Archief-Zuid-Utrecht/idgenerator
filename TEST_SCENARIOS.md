# Test Scenarios - RAZU ID Generator

This document describes the test scenarios for the idgenerator service. These scenarios should be implemented as automated tests following the guidelines in [CODING_GUIDELINES.md](CODING_GUIDELINES.md).

## Validation Tests

### Test invalid/missing required parameters

- Missing `producer` → 400 error
- Missing `dataset` → 400 error
- Missing `type` → 400 error
- Missing `aggregationlevel` → 400 error
- Empty string for required parameter → 400 error
- Whitespace-only string for required parameter → 400 error

### Test invalid enum values

- `type` = "InvalidType" → 400 error
- `type` = "informatieobject" (lowercase) → 400 error
- `aggregationlevel` = "InvalidLevel" → 400 error
- Valid values: `type` in ["Informatieobject", "Bestand"] (case sensitive), otherwise 400 error
- Valid values: `aggregationlevel` in ["Archief", "Serie", "Dossier", "Archiefstuk"] (case sensitive), otherwise 400 error

### Test whitespace handling

- `inventarisnummer` = "  INV-001  " → Trimmed to "INV-001"
- `inventarisnummer` = "   " → Treated as empty, stored as empty/null

### Test aggregation level business rules

**Archief level:**
- `aggregationlevel=Archief`, with `inventarisnummer` → 400 error
- `aggregationlevel=Archief`, with `filepath` → 400 error
- `aggregationlevel=Archief`, with both `inventarisnummer` and `filepath` → 400 error
- `aggregationlevel=Archief`, without `inventarisnummer` and `filepath` → Success

**Serie level:**
- `aggregationlevel=Serie`, with `inventarisnummer` → 400 error
- `aggregationlevel=Serie`, with `filepath` → 400 error
- `aggregationlevel=Serie`, without `inventarisnummer` and `filepath` → Success

**Dossier level:**
- `aggregationlevel=Dossier`, without `inventarisnummer` → 400 error
- `aggregationlevel=Dossier`, with `filepath` → 400 error
- `aggregationlevel=Dossier`, with `inventarisnummer`, without `filepath` → Success
- `aggregationlevel=Dossier`, with both `inventarisnummer` and `filepath` → 400 error

**Archiefstuk level:**
- `aggregationlevel=Archiefstuk`, without `inventarisnummer` → 400 error
- `aggregationlevel=Archiefstuk`, without `filepath` → 400 error
- `aggregationlevel=Archiefstuk`, with only `inventarisnummer` → 400 error
- `aggregationlevel=Archiefstuk`, with only `filepath` → 400 error
- `aggregationlevel=Archiefstuk`, with both `inventarisnummer` and `filepath` → Success

## Identifier Generation Tests

### Test first identifier for producer/dataset

- New combination → Generates `nl-wbdrazu-{producer}-{dataset}-1`
- Returns `is_new: true`
- Identifier stored in database

### Test sequential numbering

- First request: `producer=g0352`, `dataset=689` → `nl-wbdrazu-g0352-689-1`
- Second request (different params): `producer=g0352`, `dataset=689` → `nl-wbdrazu-g0352-689-2`
- Third request (different params): `producer=g0352`, `dataset=689` → `nl-wbdrazu-g0352-689-3`

### Test different producers/datasets are independent

- Request: `producer=g0352`, `dataset=689` → `nl-wbdrazu-g0352-689-1`
- Request: `producer=g0352`, `dataset=690` → `nl-wbdrazu-g0352-690-1` (different dataset)
- Request: `producer=k5090`, `dataset=689` → `nl-wbdrazu-k5090-689-1` (different producer)

### Test duplicate detection

- First request with params A → `nl-wbdrazu-g0352-689-1`, `is_new: true`
- Second request with identical params A → `nl-wbdrazu-g0352-689-1`, `is_new: false`
- Verify no new database entry created

### Test uniqueness key (all 6 parameters)

- Request 1: `producer=g0352, dataset=689, type=Informatieobject, aggregationlevel=Archief, inventarisnummer=INV-001, filepath=/path/a`
- Request 2: Same as Request 1 → Returns same identifier, `is_new: false`
- Request 3: Same but different `inventarisnummer=INV-002` → New identifier, `is_new: true`
- Request 4: Same as Request 1 but different `filepath=/path/b` → New identifier, `is_new: true`
- Request 5: Same as Request 1 but different `type=Bestand` → New identifier, `is_new: true`

### Test optional parameters in uniqueness

- Request 1: With `inventarisnummer=INV-001`, without `filepath`
- Request 2: With `inventarisnummer=INV-001`, with `filepath=/path/a` → Different identifier (filepath differs)
- Request 3: Without `inventarisnummer`, without `filepath`
- Request 4: Without `inventarisnummer`, without `filepath` → Same as Request 3

## Concurrency Tests

### Test concurrent requests for same producer/dataset

- Send 10 simultaneous requests with different parameters
- All for `producer=g0352`, `dataset=689`
- Verify: All get unique sequential numbers (1-10)
- Verify: No duplicate numbers generated
- Verify: All requests succeed

### Test concurrent duplicate requests

- Send 5 simultaneous identical requests
- Verify: All return the same identifier
- Verify: Only one database entry created
- Verify: All return `is_new: false` (or first returns `true`, rest `false`)

## API Tests

### Test POST /generate endpoint

- Valid request → 200 OK with correct JSON structure
- Invalid request → 400 Bad Request with error message
- Malformed JSON → 400 Bad Request
- Wrong HTTP method (GET) → 405 Method Not Allowed

### Test GET /health endpoint

- Returns 200 OK
- Returns status information
- Verifies database connectivity

## Edge Cases

### Test special characters in parameters

- Producer with mixed case: `G0352` → Stored as-is, identifier uses lowercase
- Dataset with special chars: `689-A` → Allowed
- Filepath with unicode: `archief/café/file.pdf` → Stored correctly

### Test very long values

- Very long `filepath` (1000+ chars) → Accepted and stored
- Very long `inventarisnummer` → Accepted and stored

### Test database persistence

- Generate identifier → Restart service → Request same params → Returns same identifier
- Verify `is_new: false` after restart

## Performance Tests (optional)

### Test response time

- Single request < 100ms
- 100 sequential requests complete in reasonable time

### Test database growth

- Generate 1000 unique identifiers
- Verify database size is reasonable
- Verify query performance remains acceptable
