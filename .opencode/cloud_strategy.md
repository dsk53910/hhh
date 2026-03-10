# Deployment Strategy

## Chosen Stack: PaaS + Managed AI-Ready Database (Option 2)
- **Compute:** Fly.io
- **Database:** Supabase (PostgreSQL)

### Rationale
This provides a zero-maintenance, $0/month environment while keeping the application architecture intact (Dockerized, long-running process) and future-proofing it for AI features.

### Why Supabase for the Database?
You mentioned needing PostgreSQL with support for "embeddings" for the future. 
Supabase is the perfect fit here. It is a managed PostgreSQL database that comes pre-installed with **`pgvector`**, which is the industry-standard extension for storing and performing similarity searches on AI vector embeddings. 

*(Note: If you specifically meant a mathematical "Graph Database" like Neo4j, Postgres can handle lightweight graph traversals using recursive CTEs, but `pgvector` is exactly what you need for AI embeddings and RAG architectures).*

### Why Fly.io for Compute?
Fly.io allows running standard Docker containers on their free tier. This means our Python bot can run as a standard long-lived process alongside our job scheduler (`APScheduler`) without needing to rewrite the app into serverless functions.

### Infrastructure Plan
1. **Database:** Create a free Supabase project. We will use their connection pooler URL to avoid exhausting database connections.
2. **Compute:** Create a `Dockerfile` and `fly.toml` in the project root.
3. **Deploy:** Use `fly deploy` to push the container to the cloud.
