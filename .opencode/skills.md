# Reusable AI Skills and Workflows

## Core Development Skills

### 1. Python Async Project Setup
**Trigger**: "Set up async Python project" or "Initialize Python project"

**Standard Workflow**:
```bash
# Create project structure
mkdir -p src/{models,services,utils,bot,core}
touch requirements.txt pyproject.toml .env.example README.md

# Initialize git
git init
echo "venv/" > .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

**Dependencies to install**:
- `aiogram>=3.0.0` - Telegram bot framework
- `sqlalchemy[asyncio]>=2.0.0` - Database ORM
- `alembic>=1.12.0` - Database migrations
- `pydantic>=2.0.0` - Data validation
- `httpx>=0.24.0` - Async HTTP client
- `apscheduler>=3.10.0` - Task scheduling
- `pyyaml>=6.0` - YAML parsing
- `python-dotenv>=1.0.0` - Environment variables
- `pytest>=7.0.0` - Testing framework
- `pytest-asyncio>=0.21.0` - Async testing

### 2. SQLAlchemy Model Creation
**Trigger**: "Create SQLAlchemy model for [entity]"

**Pattern**:
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class ModelName(Base):
    __tablename__ = "table_name"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Add specific fields here
    
    def __repr__(self):
        return f"<ModelName(id={self.id})>"
```

### 3. Aiogram Handler Pattern
**Trigger**: "Create aiogram handler for [command/action]"

**Standard Handler**:
```python
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

class HandlerStates(StatesGroup):
    # Define states here
    pass

@router.message(F.text == "/command")
async def command_handler(message: Message, state: FSMContext):
    # Handle command
    pass

@router.callback_query(F.data.startswith("action_"))
async def callback_handler(callback: CallbackQuery, state: FSMContext):
    # Handle callback
    pass
```

### 4. Configuration Management
**Trigger**: "Set up configuration management" or "Create config"

**Pydantic Config Pattern**:
```python
from pydantic import BaseSettings, Field
from typing import Optional
import os

class Settings(BaseSettings):
    # Bot settings
    bot_token: str = Field(..., env="BOT_TOKEN")
    admin_id: int = Field(..., env="ADMIN_ID")
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    
    # HH.ru
    hh_api_key: Optional[str] = Field(None, env="HH_API_KEY")
    search_interval: int = Field(300, env="SEARCH_INTERVAL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### 5. Async Database Operations
**Trigger**: "Create database service" or "Async database operations"

**Service Pattern**:
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

class DatabaseService:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def create(self, model_obj):
        async with self.async_session() as session:
            session.add(model_obj)
            await session.commit()
            await session.refresh(model_obj)
            return model_obj
    
    async def get_by_id(self, model_class, obj_id: int):
        async with self.async_session() as session:
            result = await session.get(model_class, obj_id)
            return result
```

### 6. Error Handling and Logging
**Trigger**: "Add error handling" or "Set up logging"

**Pattern**:
```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

async def safe_operation(*args, **kwargs):
    try:
        result = await operation(*args, **kwargs)
        logger.info(f"Operation completed successfully: {result}")
        return result
    except Exception as e:
        logger.error(f"Operation failed: {e}", exc_info=True)
        # Handle error appropriately
        return None
```

### 7. Testing Patterns
**Trigger**: "Write tests for [feature]" or "Create test suite"

**Test Pattern**:
```python
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_feature():
    # Arrange
    mock_service = AsyncMock()
    mock_service.method.return_value = "expected_result"
    
    # Act
    result = await function_under_test(mock_service)
    
    # Assert
    assert result == "expected_result"
    mock_service.method.assert_called_once()
```

## Project-Specific Skills

### 8. HH.ru Integration
**Trigger**: "Implement HH.ru integration" or "HH.ru API"

**HH.ru Service Pattern**:
```python
import httpx
from typing import List, Dict, Optional
import asyncio

class HHService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.hh.ru/vacancies"
        self.headers = {"User-Agent": "JobBot/1.0"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    async def search_vacancies(self, **params) -> List[Dict]:
        """Search vacancies with given parameters"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.base_url, 
                params=params, 
                headers=self.headers
            )
            response.raise_for_status()
            return response.json().get("items", [])
```

### 9. Job Application Tracking
**Trigger**: "Track job applications" or "Application status"

**Application Model**:
```python
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.sql import func
import enum

class ApplicationStatus(enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    VIEWED = "viewed"
    REJECTED = "rejected"
    ACCEPTED = "accepted"

class JobApplication(Base):
    __tablename__ = "job_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    vacancy_id = Column(String, index=True)
    company_name = Column(String)
    position = Column(String)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.PENDING)
    applied_at = Column(DateTime, default=func.now())
    response_text = Column(Text)
    notes = Column(Text)
```

### 10. Telegram Bot Menu System
**Trigger**: "Create bot menu" or "Bot navigation"

**Menu Pattern**:
```python
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_keyboard():
    buttons = [
        [KeyboardButton(text="📊 Statistics")],
        [KeyboardButton(text="🔍 Search Jobs")],
        [KeyboardButton(text="⚙️ Settings")],
        [KeyboardButton(text="📜 History")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_settings_inline():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🎯 Search Criteria", callback_data="settings_search"),
        InlineKeyboardButton(text="🔔 Notifications", callback_data="settings_notify"),
        InlineKeyboardButton(text="🤖 Auto-apply", callback_data="settings_autoapply"),
    )
    builder.adjust(1)
    return builder.as_markup()
```

## Workflow Templates

### 11. New Feature Development
**Steps**:
1. Create/update SQLAlchemy models
2. Generate Alembic migration
3. Implement service layer
4. Create bot handlers
5. Add tests
6. Update documentation
7. Create configuration options

### 12. Database Schema Changes
**Steps**:
1. Modify model definitions
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Review generated migration
4. Apply migration: `alembic upgrade head`
5. Update related services
6. Add tests for new fields

### 13. External API Integration
**Steps**:
1. Research API documentation
2. Create service class with authentication
3. Implement rate limiting
4. Add error handling and retries
5. Create data models for API responses
6. Write integration tests
7. Add monitoring and logging

## Code Review Checklists

### 14. Async Code Review
- [ ] All async functions use `await` properly
- [ ] No blocking calls in async functions
- [ ] Proper error handling with try/except
- [ ] Resource cleanup (sessions, connections)
- [ ] Timeout handling for external calls
- [ ] Concurrency safety considerations

### 15. Security Review
- [ ] No hardcoded secrets or credentials
- [ ] Input validation and sanitization
- [ ] SQL injection prevention
- [ ] Rate limiting implementation
- [ ] Authentication and authorization checks
- [ ] Audit logging for sensitive operations

## Performance Optimization

### 16. Database Optimization
- Use connection pooling
- Add appropriate indexes
- Optimize queries with `explain analyze`
- Implement query result caching
- Batch operations where possible
- Use read replicas for read-heavy workloads

### 17. Bot Performance
- Implement caching for frequent requests
- Use background tasks for long operations
- Optimize message sending (batch where possible)
- Monitor response times
- Implement graceful degradation

## Debugging Skills

### 18. Common Issues
**Database connection issues**:
- Check connection string format
- Verify database is running
- Check firewall rules
- Validate credentials

**Bot not responding**:
- Verify bot token is correct
- Check webhook vs polling configuration
- Review bot permissions
- Check rate limiting

**HH.ru API issues**:
- Verify API key validity
- Check rate limits
- Review request parameters
- Monitor User-Agent requirements