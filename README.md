# Recruiting Loop Agent v3.0

An autonomous recruiting agent that continuously searches for candidates until the position is closed.

## Overview

The Recruiting Loop Agent is designed to run indefinitely, searching for candidates, deduplicating, updating databases, automatically scoring, contacting candidates, and continuing the search until a position is closed.

## Tech Stack

- Backend: FastAPI
- Agent: LangGraph
- ORM: SQLAlchemy 2.x (Async)
- Database: SQLite
- Scheduler: APScheduler + asyncio
- Frontend: React + Ant Design
- HTTP Client: httpx
- Email: smtplib
- Container: Docker Compose

## Architecture

The system follows a four-layer architecture:
- HTTP Request
- FastAPI Router
- Service Layer
- Repository Layer
- SQLite Database

## Getting Started

```bash
docker-compose up
```

## Development

See individual module documentation in the docs/ folder.