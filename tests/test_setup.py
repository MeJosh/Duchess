"""
Test that the project structure is set up correctly.
"""

import pytest
from duchess.utils import get_logger


def test_logging_setup():
    """Test that logging is configured correctly."""
    logger = get_logger(__name__)
    assert logger is not None
    
    logger.info("Test log message - INFO level")
    logger.debug("Test log message - DEBUG level")
    logger.warning("Test log message - WARNING level")
    
    # Verify logger has handlers
    assert len(logger.handlers) > 0


def test_project_version():
    """Test that the package is importable."""
    import duchess
    assert duchess.__version__ == "0.1.0"
