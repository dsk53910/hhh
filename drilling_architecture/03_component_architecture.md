# Level 3: Component Architecture (Application Schema)

This level zooms into the "Python Application Container" from Level 2 to show the internal modules, services, and how data flows through the Python code.

```mermaid
C4Component
    title Component Architecture for Python Application

    ContainerDb(postgres, "PostgreSQL DB", "Supabase", "Persistent Storage")
    System_Ext(hhru, "HH.ru API", "External System")
    System_Ext(telegram, "Telegram API", "External System")

    Boundary(app, "HHH Bot Python Application") {
        
        Component(bot_entry, "Bot Entry Point", "aiogram", "Initializes the bot, dispatcher, and routers")
        Component(scheduler, "Task Scheduler", "APScheduler", "Triggers periodic background jobs")
        
        Component(handlers, "Telegram Handlers", "aiogram routers", "Processes commands (/start, /search) and button clicks")
        
        Component(hh_service, "HH.ru Service", "httpx", "Handles rate-limiting, auth, and HTTP requests to HH.ru")
        Component(match_service, "Matching Engine", "Python", "Scores jobs against user profiles")
        Component(db_service, "Database Service", "SQLAlchemy", "Async CRUD operations and transaction management")
        
        Component(models, "Data Models", "SQLAlchemy ORM", "Defines the schema (User, Vacancy, Profile)")
    }

    Rel(telegram, bot_entry, "Updates")
    Rel(bot_entry, handlers, "Routes to")
    
    Rel(scheduler, hh_service, "Triggers job scan every 5m")
    Rel(hh_service, hhru, "Fetches /vacancies")
    
    Rel(hh_service, match_service, "Passes new jobs")
    Rel(match_service, db_service, "Saves matched jobs")
    
    Rel(handlers, db_service, "CRUD user settings")
    Rel(db_service, postgres, "SQL queries")
    Rel(db_service, models, "Uses ORM")
    
    Rel(match_service, telegram, "Sends 'New Job' alerts via Bot API")
```

## Execution Flows

### 1. The Bot Flow (User Interaction)
1. User sends `/search` in Telegram.
2. `bot_entry` receives the update and routes it to `handlers`.
3. `handlers` queries `db_service` for the user's active search profiles.
4. `handlers` formats a message and sends it back to Telegram.

### 2. The Background Job Flow (Monitoring)
1. `scheduler` wakes up every 5 minutes.
2. It asks `db_service` for all active search profiles across all users.
3. For each profile, it calls `hh_service` to fetch new vacancies.
4. The results are passed to the `match_service` to deduplicate and score against the user's criteria.
5. If a match is found, `db_service` saves the `Vacancy` and creates a `MonitoredJob` link.
6. The `match_service` triggers a Telegram notification to the user.