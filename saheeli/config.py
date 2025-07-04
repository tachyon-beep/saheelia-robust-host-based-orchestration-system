"""Configuration utilities and models."""

from pathlib import Path
import os

from pydantic import BaseModel
import yaml


class Config(BaseModel):
    """Application configuration settings."""

    model_name: str
    api_base: str
    api_key_env_var: str
    servo_image: str
    cpu_limit: float
    memory_limit: str
    timeout: int


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


def load_config(path: Path | None = None) -> Config:
    """Load configuration from YAML file."""
    path = path or CONFIG_PATH
    data = yaml.safe_load(path.read_text())
    return Config(**data)


def get_api_key(cfg: Config) -> str:
    """Return the API key from the environment."""
    return os.getenv(cfg.api_key_env_var, "")
