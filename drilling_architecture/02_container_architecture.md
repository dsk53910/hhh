# Level 2: Container Architecture (Deployment Schema)

This level zooms into the "HHH Bot" system from Level 1 to show the deployable units (containers, databases) and how they communicate.

```mermaid
C4Container
    title Container Architecture for HHH Bot

    System_Ext(telegram, "Telegram API", "Messaging platform")
    System_Ext(hhru, "HH.ru API", "Job board")

    Boundary(flyio, "Fly.io (Compute Cloud)") {
        Container(python_app, "Python Application Container", "Python 3.11+, Aiogram, SQLAlchemy", "Runs the Telegram Bot and background scheduling processes concurrently.")
    }

    Boundary(supabase, "Supabase (Database Cloud)") {
        ContainerDb(postgres, "PostgreSQL DB", "PostgreSQL 15+", "Stores users, search profiles, vacancies, and application state.")
        ContainerDb(pgvector, "pgvector Extension", "PostgreSQL Extension", "Stores vector embeddings of resumes and job descriptions for semantic matching (Future).")
    }

    Rel(telegram, python_app, "Sends Updates (Polling/Webhook)", "HTTPS")
    Rel(python_app, hhru, "Fetches vacancies (Scheduled)", "HTTPS")
    Rel(python_app, postgres, "Reads/Writes state", "SQL/TCP")
    Rel(postgres, pgvector, "Powers similarity search")
```

## Deployment Notes
*   **Single Container Strategy**: To keep costs at $0, the Telegram Bot (Aiogram) and the Job Scanner (APScheduler) run in the same Python process inside a single Docker container deployed to **Fly.io**.
*   **Database**: Hosted on **Supabase**. The application uses an async SQLAlchemy connection pool to talk to Postgres.
*   **AI Readiness**: Supabase provides `pgvector` out of the box, allowing us to easily transition from keyword-based matching to AI semantic matching later.