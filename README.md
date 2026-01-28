# Travel Planner API

API for managing travel projects and places from Art Institute of Chicago.

## Description

Travel Planner API allows you to create travel projects and add places (artworks) from the Art Institute of Chicago API to them. You can track visited places, add notes, and manage your travel projects.

## Features

### Travel Projects
- ✅ Create a travel project (with or without places)
- ✅ List projects with pagination and filtering
- ✅ Get a single project by ID
- ✅ Update project information
- ✅ Delete a project (cannot delete if it has visited places)

### Places / Project Places
- ✅ Add a place to an existing project
- ✅ List all places for a project with pagination
- ✅ Get a single place by ID
- ✅ Update place notes
- ✅ Mark a place as visited/not visited

### Additional Features
- ✅ Caching responses from third-party API
- ✅ Automatic project completion status updates
- ✅ Validation of place existence in Art Institute API

## Technologies

- **FastAPI** - Modern web framework for Python
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Database
- **Pydantic** - Data validation
- **httpx** - Async HTTP requests
- **Uvicorn** - ASGI server

## Requirements

- Docker and Docker Compose

## Installation and Running

### Docker Compose (Recommended)

1. **Clone the repository:**
```bash
git clone <repository-url>
cd Travel-Planner
```

2. **Start the application:**
```bash
docker-compose up -d
```

3. **View logs:**
```bash
docker-compose logs -f
```

4. **Stop the application:**
```bash
docker-compose down
```

### Docker

1. **Build the image:**
```bash
docker build -t travel-planner-api .
```

2. **Run the container:**
```bash
docker run -d \
  --name travel-planner-api \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  travel-planner-api
```

## Environment Variables

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `DATABASE_URL` | Database URL | `sqlite:///./data/travel_planner.db` |
| `ART_INSTITUTE_API_BASE_URL` | Art Institute API base URL | `https://api.artic.edu/api/v1` |
| `API_CACHE_TTL_SECONDS` | Cache TTL in seconds | `3600` (1 hour) |

## API Documentation

After starting the application, documentation is available at:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Schema (JSON):** http://localhost:8000/openapi.json

### Importing to Postman

You can import the API into Postman using the OpenAPI schema:

1. Open Postman
2. Click **Import** button
3. Select **Link** tab
4. Enter: `http://localhost:8000/openapi.json`
5. Click **Continue** and **Import**

Alternatively, you can download the OpenAPI schema and import it as a file:

```bash
curl http://localhost:8000/openapi.json -o openapi.json
```

Then import the `openapi.json` file into Postman.

