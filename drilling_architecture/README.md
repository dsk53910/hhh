# Architecture Drill-Down (C4 Model)

This folder contains the architectural blueprints for the **HHH Bot**. 

We are using the **C4 Model** (Context, Containers, Components, Code) combined with **Mermaid.js** diagrams. This is the absolute best way to document architecture because:
1. **It's visual:** GitHub and most modern editors render Mermaid code blocks as actual diagrams.
2. **It's text-based:** It lives in version control alongside your code.
3. **It drills down logically:** You start at the highest abstraction (Level 1) and zoom into the specific Python classes (Level 3/4).

## Navigation

*   [Level 1: System Context](01_system_context.md) - The Global Schema (Users, Telegram, Bot, External APIs).
*   [Level 2: Container Architecture](02_container_architecture.md) - The Deployment Schema (Fly.io, Supabase, Python App).
*   [Level 3: Component Architecture](03_component_architecture.md) - The internal Python Application Schema (Handlers, Services, Schedulers).
*   *Level 4: Code/Data Models (To be created as we drill into specific services)*