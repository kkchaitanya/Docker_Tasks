# Student Management System

A Docker Compose mini-project with a browser UI, FastAPI REST API, PostgreSQL, health checks, a bridge network, environment configuration, and a persistent database volume.

## Requirements
- Docker Desktop (Windows/macOS) or Docker Engine + Docker Compose plugin (Linux)
- Ports 8080 and 8000 available

## Start everything
From this directory:

```bash
docker compose up --build
```

Open:
- UI: http://localhost:8080
- API documentation: http://localhost:8000/docs
- API health: http://localhost:8000/health

The frontend sends API requests through its Nginx reverse proxy. PostgreSQL is not published to the host; the backend connects to it using the Compose service name `db`.

## CRUD API
- `GET /api/students` — list students
- `GET /api/students/{id}` — get one student
- `POST /api/students` — create a student
- `PUT /api/students/{id}` — update a student
- `DELETE /api/students/{id}` — delete a student

Example JSON for POST/PUT:

```json
{
  "name": "Ananya Rao",
  "email": "ananya@example.com",
  "course": "Computer Science",
  "age": 21
}
```

## Verify health and containers
```bash
docker compose ps
curl http://localhost:8000/health
```

On PowerShell, use `Invoke-RestMethod http://localhost:8000/health` if `curl` behaves as an alias.

## Verify persistence across restarts
1. Add a student in the UI.
2. Run `docker compose restart`.
3. Refresh the UI; the student should remain.

The named volume `postgres_data` stores PostgreSQL data outside the container's writable layer. Rebuilding or restarting containers does not delete it.

## Stop the application
```bash
docker compose down
```

This keeps the named database volume. To intentionally delete the database and all stored records too:
```bash
docker compose down -v
```

## Configuration
Edit `.env` before starting. `.env` is ignored by Git; `.env.example` is a template. Change the sample password before using this beyond local development.

## Troubleshooting
```bash
docker compose logs -f
docker compose logs backend
docker compose ps
```
If you change the backend code or Dockerfile, run `docker compose up --build`.
