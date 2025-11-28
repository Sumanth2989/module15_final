# Module 11 – SQLAlchemy Model, Pydantic Schemas, Factory Pattern & CI/CD

This module implements the Calculation feature using SQLAlchemy, Pydantic, a Factory design pattern, and a full CI/CD pipeline with GitHub Actions and Docker Hub. It includes unit tests, integration tests with PostgreSQL, Alembic migrations, and automated Docker image builds and pushes.

## Features Implemented

### SQLAlchemy Calculation Model
- Fields: id, a, b, type, result
- Enum-based operation types: add, sub, multiply, divide
- Alembic migrations fully functional

### Pydantic Schemas
- CalculationCreate for validating inputs
- CalculationRead for returning responses
- Validation prevents division by zero and invalid types

### Factory Pattern
Implements strategies:
- AddStrategy
- SubStrategy
- MultiplyStrategy
- DivideStrategy

This ensures extensibility for future operations.

### Testing
- Unit tests: Factory logic + Pydantic rules
- Integration tests: Database persistence using SQLAlchemy + Alembic
- All tests pass locally and in CI

## Run Tests Locally

pip install -r requirements.txt  
pytest -q

## Database Migrations

alembic upgrade head

## Build & Run Docker Image Locally

docker build -t module11-sql .  
docker run -p 8000:8000 module11-sql

## CI/CD Pipeline (GitHub Actions)

Every push to main:
1. Installs dependencies
2. Runs tests
3. Builds Docker image
4. Pushes image to Docker Hub

Workflow file: .github/workflows/ci.yml

## Docker Hub Repository Link

https://hub.docker.com/r/sumanthchand23/module11-sql

## Project Structure

app/
 ├── models/
 │    └── calculation.py
 ├── schemas/
 │    └── calculation.py
 ├── services/
 │    ├── calculation_factory.py
 │    └── calculation_service.py
alembic/
 ├── versions/
tests/
 ├── unit/
 ├── integration/
.github/
 └── workflows/
     └── ci.yml

