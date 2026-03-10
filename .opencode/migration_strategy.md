# Infrastructure Migration Strategy

## Overview: Moving Between Option 1 (VPS) and Option 2 (PaaS)

Migrating between a raw Virtual Private Server (Oracle Cloud/Option 1) and a Platform-as-a-Service (Fly.io + Neon / Option 2) is **very easy** because the underlying application architecture remains exactly the same. 

In both scenarios, the application runs as a continuous, long-running Docker container.

### Why It's Easy

1.  **No Code Changes Required:**
    *   Both options support standard `aiogram` long-polling (`bot.polling()`).
    *   Both options support background thread schedulers (e.g., `APScheduler`) running alongside the bot.
    *   Both options handle standard PostgreSQL connection pooling (`pool_size: 10`) without exhausting limits rapidly like AWS Lambda would.

2.  **Docker is the Common Denominator:**
    *   **Option 1 (VPS):** You run `docker-compose up -d` on your Linux server.
    *   **Option 2 (Fly.io):** You run `fly deploy`, which builds your Dockerfile and runs the container on their infrastructure.

3.  **Environment Variables:**
    *   The only thing that changes is where the `DATABASE_URL` points.
    *   On a VPS, it might point to `localhost:5432` (a local Postgres container).
    *   On Fly.io, it points to the external Neon DB URL (`postgresql://user:pass@ep-cool-snow-1234.eu-central-1.aws.neon.tech/dbname`).

### The Migration Process

#### Migrating from Option 1 (VPS) -> Option 2 (Fly.io + Neon)
1.  **Export Database:** Dump the PostgreSQL database from the VPS (`pg_dump`).
2.  **Import Database:** Restore the dump into the new Neon database.
3.  **Deploy Compute:** Run `fly launch` and `fly deploy` to push the Docker container to Fly.io.
4.  **Update Config:** Change the `DATABASE_URL` secret in Fly.io to point to Neon.
5.  **Shutdown VPS:** Stop the containers on the Oracle VPS.

#### Migrating from Option 2 (Fly.io + Neon) -> Option 1 (VPS)
1.  **Export Database:** Dump the database from Neon.
2.  **Setup VPS:** Provision an Oracle Linux server, install Docker and Docker Compose.
3.  **Import Database:** Start a local PostgreSQL container on the VPS and restore the dump.
4.  **Deploy Compute:** Pull your code to the VPS, build the Docker image, and run it via `docker-compose`.
5.  **Update Config:** Change `.env` on the VPS to point to the local database.

### Conclusion
Because the app is containerized (Docker) and relies on standard environment variables, you avoid "vendor lock-in." You can start with Fly.io + Neon for the easiest $0 setup, and if you ever need more resources (e.g., 24GB of RAM), you can easily move the Docker containers to an Oracle VPS in under an hour.
