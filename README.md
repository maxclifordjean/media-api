# media-api

API service for managing media content, primarily focused on video assets. Provides endpoints for uploading, retrieving, and enriching media metadata.

## Stack

| Component         | Description                                         |
|-------------------|-----------------------------------------------------|
| **FastAPI**       | High-performance web framework for building APIs    |
| **PostgreSQL**    | Reliable relational database for persistent storage |
| **SQLModel**      | ORM combining SQLAlchemy and Pydantic for models    |
| **Pydantic**      | Data validation and serialization                   |
| **Alembic**       | Database schema migrations                          |
| **ASYNCPG**       | Asynchronous PostgreSQL driver                      |
| **APScheduler**   | Advanced scheduling for background tasks            |
| **S3**            | Cloud object storage for media files                |

---

## Features

- **Video Upload Workflow**
    - Upload videos to server, store temporarily, then transfer to S3 cloud storage.
    - Extract video metadata using `common_utils.media` and persist to PostgreSQL.
- **Media Metadata Management**
    - Store and manage media records in PostgreSQL.
    - Retrieve detailed media information via API endpoints.
- **S3 Util**
    - List, upload, delete, and move files in S3 buckets.
- **API Endpoints**
    - Submit media with `form data`: video file, title, and description.
    - Update media records by uploading a `ZIP archive` containing additionnal files:
        - **Scenario File:** PDF document
        - **Casting Profile Info:** CSV with metadata columns
        - **Scene Locations:** CSV with scene details and address information
        - **Subtitles:** TXT file with timestamps
    - ZIP files are stored temporarily, then uploaded to S3 and linked to the corresponding media record.
- **Testing**
    - Unit tests for media processing, S3 utilities, and API endpoints.

