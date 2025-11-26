"""
Centralized logging configuration for Duchess.

Provides detailed logging to both console and file for high visibility
into system operations.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    level: int = logging.DEBUG,
    log_file: Optional[str] = None,
    console_level: int = logging.INFO,
) -> logging.Logger:
    """
    Configure a logger with both file and console handlers.
    
    Args:
        name: Logger name (typically __name__ of the module)
        level: Minimum logging level for file output
        log_file: Path to log file (relative to logs/ directory)
        console_level: Minimum logging level for console output
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers if logger already configured
    if logger.handlers:
        return logger
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Formatter with detailed information
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)-30s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Console formatter (slightly simpler)
    console_formatter = logging.Formatter(
        fmt="%(levelname)-8s | %(name)-25s | %(message)s"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_path = logs_dir / log_file
        file_handler = logging.FileHandler(file_path, mode="a")
        file_handler.setLevel(level)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    Get or create a logger for a module.
    
    Args:
        name: Logger name (use __name__ from calling module)
        log_file: Optional log file name in logs/ directory
        
    Returns:
        Configured logger
    """
    # Default log file based on phase
    if log_file is None:
        # Extract module to determine log file
        if "engine" in name:
            log_file = "engine.log"
        elif "reasoning" in name:
            log_file = "reasoning.log"
        elif "agent" in name:
            log_file = "agents.log"
        elif "simulation" in name:
            log_file = "simulation.log"
        else:
            log_file = "duchess.log"
    
    return setup_logger(name, log_file=log_file)


# Main application logger
main_logger = get_logger("duchess", log_file="duchess.log")

# Convenience export
logger = main_logger
