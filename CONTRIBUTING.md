# Contributing to RAZU ID Generator

## Development Approach

This project follows a **documentation-first, AI-assisted development workflow**. Code is generated and maintained based on comprehensive documentation specifications.

## Documentation Structure

The project is defined by three core documentation files:

1. **[PROJECT_DEFINITION.md](PROJECT_DEFINITION.md)** - Functional specification
   - API endpoints and parameters
   - Business logic and validation rules
   - Data persistence and deployment

2. **[TEST_SCENARIOS.md](TEST_SCENARIOS.md)** - Test scenarios
   - Validation test cases
   - Identifier generation tests
   - Concurrency and edge cases

3. **[CODING_GUIDELINES.md](CODING_GUIDELINES.md)** - Code standards
   - Naming conventions
   - Design patterns
   - Preferred libraries

## Making Changes

### Workflow

1. **Update documentation first**
   - Modify PROJECT_DEFINITION.md for functional changes
   - Update TEST_SCENARIOS.md for new test cases
   - Adjust CODING_GUIDELINES.md only for general standards (not project-specific)

2. **Generate/update code**
   - Use AI assistance (e.g., Claude/Cascade) to implement changes based on updated documentation
   - Ensure all changes follow CODING_GUIDELINES.md

3. **Verify implementation**
   - Run tests: `pytest -v`
   - Check coverage: `pytest --cov=src`
   - Manually test API endpoints if needed

4. **Update README.md if needed**
   - Only for quick start or practical usage changes
   - Keep it concise - detailed info belongs in PROJECT_DEFINITION.md

### Example: Adding a New Validation Rule

1. Document the rule in PROJECT_DEFINITION.md (Validation Rules section)
2. Add test scenarios in TEST_SCENARIOS.md
3. Instruct AI to implement the validation in `src/validator.py`
4. Run tests to verify
5. Commit documentation and code together

## Code Generation

This codebase was initially generated with AI assistance and is maintained the same way. The AI acts as an implementation tool that translates documentation into code following established patterns.

## Testing

All changes must maintain or improve test coverage:

```bash
# Run all tests
pytest -v

# Check coverage (should be >95%)
pytest --cov=src --cov-report=term-missing
```

Current coverage: **98%** (47 tests)

## Code Review Checklist

Before committing changes:

- [ ] Documentation updated first
- [ ] Code follows CODING_GUIDELINES.md
- [ ] All tests pass
- [ ] Test coverage maintained or improved
- [ ] README.md updated if needed (quick start only)
- [ ] No hardcoded values or temporary hacks

## Questions?

For questions about:
- **Functionality**: See PROJECT_DEFINITION.md
- **Testing**: See TEST_SCENARIOS.md
- **Code style**: See CODING_GUIDELINES.md
