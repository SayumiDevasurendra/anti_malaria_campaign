"""
Configurable logging with console and file output
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_stain_time_logger(
    name: str = "AMC",
    log_dir: str = "logs/logs_04",
    level: str = "INFO",
    console_output: bool = True,
    file_output: bool = True
) -> logging.Logger:
    """Set up project logger with console and file output"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if file_output:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        # Create one log file per day (append mode)
        date_stamp = datetime.now().strftime("%Y%m%d")
        log_file = log_path / f"{name}_{date_stamp}.log"

        file_handler = logging.FileHandler(log_file, mode='a')  # Append mode
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Log separator for each run
        logger.info("=" * 80)
        logger.info(f"NEW RUN STARTED AT {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)

    return logger
