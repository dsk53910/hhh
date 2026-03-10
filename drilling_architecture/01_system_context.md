# Level 1: System Context (Global Schema)

This is the "bird's-eye view" of the entire system. It shows the users and the external systems the HHH Bot interacts with.

```mermaid
C4Context
    title System Context for HHH Bot

    Person(user, "Job Seeker", "A user searching for jobs on Telegram")
    
    System(bot, "HHH Bot", "Monitors job postings, sends notifications, and auto-applies on behalf of the user")
    
    System_Ext(telegram, "Telegram API", "Messaging platform for user interaction")
    System_Ext(hhru, "HH.ru API", "The HeadHunter Russia job board API")
    System_Ext(llm, "LLM Provider (Optional)", "OpenAI/Anthropic for generating personalized cover letters")

    Rel(user, telegram, "Sends commands, receives job alerts", "HTTPS")
    Rel(telegram, bot, "Forwards messages/webhooks", "HTTPS")
    Rel(bot, hhru, "Polls for new vacancies, submits applications", "HTTPS/REST")
    Rel(bot, llm, "Requests cover letter generation", "HTTPS")
```

## Description
*   **Job Seeker**: Interacts exclusively through the Telegram UI.
*   **Telegram API**: Acts as the frontend presentation layer.
*   **HHH Bot**: The core system we are building. It orchestrates the entire flow.
*   **HH.ru API**: The source of truth for job vacancies.
*   **LLM Provider**: (Future) Used to generate smart, contextual responses based on the vacancy description.