"""
Configuration management using Pydantic with YAML support
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml


class BotConfig(BaseModel):
    """Telegram bot configuration"""

    token: str
    admin_id: int
    webhook_url: Optional[str] = None
    drop_pending_updates: bool = True


class DatabaseConfig(BaseModel):
    """Database configuration"""

    url: str
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False


class HHConfig(BaseModel):
    """HH.ru API configuration"""

    api_key: Optional[str] = None
    search_interval: int = 300  # seconds
    max_requests_per_hour: int = 100
    default_filters: Dict[str, Any] = {}
    user_agent: str = "HHH-Bot/1.0 (+https://github.com/example/hhh-bot)"


class AutoApplyConfig(BaseModel):
    """Auto-apply configuration"""

    enabled: bool = False
    require_approval: bool = True
    max_applications_per_day: int = 5
    auto_responses: bool = False
    approval_timeout: int = 3600  # seconds


class NotificationConfig(BaseModel):
    """Notification configuration"""

    enabled: bool = True
    digest_time: str = "09:00"
    new_job_alert: bool = True
    application_update: bool = True
    error_alerts: bool = True
    daily_summary: bool = False


class LoggingConfig(BaseModel):
    """Logging configuration"""

    level: str = "INFO"
    file: Optional[str] = None
    json_format: bool = False
    max_file_size: str = "10MB"
    backup_count: int = 5


class Settings(BaseSettings):
    """Main application settings"""

    # Environment
    environment: str = "development"
    debug: bool = False
    secret_key: str

    # Sub-configurations
    bot: BotConfig
    database: DatabaseConfig
    hh: HHConfig = HHConfig()
    auto_apply: AutoApplyConfig = AutoApplyConfig()
    notifications: NotificationConfig = NotificationConfig()
    logging: LoggingConfig = LoggingConfig()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
    )

    @classmethod
    def load_from_yaml(cls, config_path: str = "config/config.yaml") -> "Settings":
        """
        Load configuration from YAML file

        Args:
            config_path: Path to YAML configuration file

        Returns:
            Settings instance
        """
        # Manually load .env file using python-dotenv so pydantic gets it
        from dotenv import load_dotenv

        load_dotenv()

        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        import os
        import re

        with open(config_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Basic environment variable substitution for ${VAR_NAME} in YAML
        # Fallback to empty string or numeric 0 if not found to avoid pydantic errors
        def replacer(match):
            val = os.environ.get(match.group(1))
            if val is not None:
                return val
            # For known integers, return "0"
            if match.group(1) == "ADMIN_ID":
                return "0"
            return ""

        content = re.sub(r"\$\{([^}^{]+)\}", replacer, content)

        config_data = yaml.safe_load(content)

        config_data = yaml.safe_load(content)

        # Override with actual environment variables manually
        db_url = os.environ.get("DATABASE_URL")
        if db_url:
            if "database" not in config_data:
                config_data["database"] = {}
            config_data["database"]["url"] = db_url.strip("\"'")

        bot_token = os.environ.get("BOT_TOKEN")
        if bot_token:
            if "bot" not in config_data:
                config_data["bot"] = {}
            config_data["bot"]["token"] = bot_token.strip("\"'")

        admin_id = os.environ.get("ADMIN_ID")
        if admin_id:
            if "bot" not in config_data:
                config_data["bot"] = {}
            config_data["bot"]["admin_id"] = int(admin_id.strip("\"'"))

        hh_api_key = os.environ.get("HH_API_KEY")
        if hh_api_key:
            if "hh" not in config_data:
                config_data["hh"] = {}
            config_data["hh"]["api_key"] = hh_api_key.strip("\"'")

        hh_resume_id = os.environ.get("HH_RESUME_ID")
        if hh_resume_id:
            if "hh" not in config_data:
                config_data["hh"] = {}
            config_data["hh"]["resume_id"] = hh_resume_id.strip("\"'")

        return cls(**config_data)

    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment is one of allowed values"""
        allowed = ["development", "testing", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of: {', '.join(allowed)}")
        return v

    @validator("logging")
    def validate_logging_level(cls, v):
        """Validate logging level"""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.level.upper() not in allowed:
            raise ValueError(f"Logging level must be one of: {', '.join(allowed)}")
        v.level = v.level.upper()
        return v

    @validator("notifications")
    def validate_digest_time(cls, v):
        """Validate digest time format (HH:MM)"""
        import re

        pattern = r"^[0-2][0-9]:[0-5][0-9]$"
        if not re.match(pattern, v.digest_time):
            raise ValueError("Digest time must be in format HH:MM")
        return v

    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"

    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"

    def get_database_url(self) -> str:
        """Get database URL with async driver"""
        return self.database.url

    def get_log_config(self) -> Dict[str, Any]:
        """Get logging configuration dictionary"""
        return {
            "log_level": self.logging.level,
            "log_file": self.logging.file,
            "json_format": self.logging.json_format,
        }


# Global settings instance
settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get global settings instance, loading if necessary

    Returns:
        Settings instance
    """
    global settings
    if settings is None:
        settings = Settings.load_from_yaml()
    return settings


def reload_settings(config_path: str = "config/config.yaml") -> Settings:
    """
    Reload settings from file

    Args:
        config_path: Path to configuration file

    Returns:
        Reloaded settings instance
    """
    global settings
    settings = Settings.load_from_yaml(config_path)
    return settings


# Configuration file validation
def validate_config_file(config_path: str) -> bool:
    """
    Validate configuration file syntax

    Args:
        config_path: Path to configuration file

    Returns:
        True if valid, False otherwise
    """
    try:
        Settings.load_from_yaml(config_path)
        return True
    except Exception:
        return False


# Environment-specific configuration templates
def create_config_template() -> Dict[str, Any]:
    """
    Create a configuration file template

    Returns:
        Dictionary with default configuration values
    """
    return {
        "environment": "development",
        "debug": True,
        "secret_key": "your-secret-key-here",
        "bot": {
            "token": "your-bot-token",
            "admin_id": 123456789,
            "webhook_url": None,
            "drop_pending_updates": True,
        },
        "database": {
            "url": "postgresql+asyncpg://user:password@localhost:5432/hhh_bot",
            "pool_size": 10,
            "max_overflow": 20,
            "echo": False,
        },
        "hh": {
            "api_key": None,
            "search_interval": 300,
            "max_requests_per_hour": 100,
            "default_filters": {
                "text": "Python developer",
                "area": 1,
                "schedule": "remote",
            },
            "user_agent": "HHH-Bot/1.0 (+https://github.com/example/hhh-bot)",
        },
        "auto_apply": {
            "enabled": False,
            "require_approval": True,
            "max_applications_per_day": 5,
            "auto_responses": False,
            "approval_timeout": 3600,
        },
        "notifications": {
            "enabled": True,
            "digest_time": "09:00",
            "new_job_alert": True,
            "application_update": True,
            "error_alerts": True,
            "daily_summary": False,
        },
        "logging": {
            "level": "INFO",
            "file": None,
            "json_format": False,
            "max_file_size": "10MB",
            "backup_count": 5,
        },
    }
