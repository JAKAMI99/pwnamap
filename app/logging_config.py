import os
import logging
import argparse
from flask import Flask
from logging.handlers import TimedRotatingFileHandler

parser = argparse.ArgumentParser(description="Flask Application with Logging")
parser.add_argument(
    "--debug",
    action="store_true",
    help="Run the app in debug mode with verbose logging",
)

# Parse the command-line arguments
args = parser.parse_args()

# Determine log level from command-line argument or environment variable
env_log_level = os.getenv("LOG_LEVEL", "INFO").upper()
log_level = logging.DEBUG if args.debug else getattr(logging, env_log_level, logging.INFO)

# Ensure the directory for log files exists
log_directory = "app/data/logs"  # Log directory
if not os.path.exists(log_directory):
    os.makedirs(log_directory, exist_ok=True)  # Create the directory if it doesn't exist

# Configure the logging with TimedRotatingFileHandler
log_file_path = f"{log_directory}/pwnamap.log"
file_handler = TimedRotatingFileHandler(
    log_file_path,
    when="midnight",
    interval=1,
    backupCount=14,
)
file_handler.setLevel(log_level)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[file_handler, logging.StreamHandler()],
)

# Create Flask application
app = Flask(__name__)
