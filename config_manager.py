"""Configuration management for the Twitter bot."""
import json
import os
from typing import Dict, Any
from dotenv import load_dotenv


class ConfigManager:
    """Manages bot configuration from JSON and environment variables."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration JSON file
        """
        load_dotenv()
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_env_vars()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in configuration file: {self.config_path}")
    
    def _validate_env_vars(self):
        """Validate that required environment variables are set."""
        required_vars = [
            'TWITTER_API_KEY',
            'TWITTER_API_SECRET',
            'TWITTER_ACCESS_TOKEN',
            'TWITTER_ACCESS_TOKEN_SECRET',
            'OPENAI_API_KEY'
        ]
        
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    def get_character(self) -> Dict[str, Any]:
        """Get character configuration."""
        return self.config.get('character', {})
    
    def get_bot_settings(self) -> Dict[str, Any]:
        """Get bot settings."""
        return self.config.get('bot_settings', {})
    
    def get_behavior(self) -> Dict[str, Any]:
        """Get bot behavior settings."""
        return self.config.get('behavior', {})
    
    def get_twitter_credentials(self) -> Dict[str, str]:
        """Get Twitter API credentials from environment variables."""
        return {
            'api_key': os.getenv('TWITTER_API_KEY'),
            'api_secret': os.getenv('TWITTER_API_SECRET'),
            'access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
            'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            'bearer_token': os.getenv('TWITTER_BEARER_TOKEN')
        }
    
    def get_openai_config(self) -> Dict[str, str]:
        """Get OpenAI configuration from environment variables."""
        return {
            'api_key': os.getenv('OPENAI_API_KEY'),
            'model': os.getenv('OPENAI_MODEL', 'gpt-4'),
            'vision_model': os.getenv('OPENAI_VISION_MODEL', 'gpt-4-vision-preview')
        }
