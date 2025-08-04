"""Comprehensive logging system for Battle of Wits."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class BattleOfWitsLogger:
    """Custom logger for the Battle of Wits application."""
    
    def __init__(self, name: str = "battle_of_wits"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            self._setup_logger()
    
    def _setup_logger(self):
        """Set up the logger with console and file handlers."""
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Create formatters
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
        )
        
        # Console handler (for development)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        
        # File handler (for debugging)
        log_file = logs_dir / f"battle_of_wits_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(self._format_message(message, **kwargs))
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error message with optional exception details."""
        full_message = self._format_message(message, **kwargs)
        if error:
            full_message += f" | Error: {str(error)} | Type: {type(error).__name__}"
        self.logger.error(full_message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(self._format_message(message, **kwargs))
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(self._format_message(message, **kwargs))
    
    def _format_message(self, message: str, **kwargs) -> str:
        """Format message with additional context."""
        if kwargs:
            context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            return f"{message} | {context}"
        return message


# Global logger instance
_logger = None

def get_logger() -> BattleOfWitsLogger:
    """Get the global logger instance."""
    global _logger
    if _logger is None:
        _logger = BattleOfWitsLogger()
    return _logger