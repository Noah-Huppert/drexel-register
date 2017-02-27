import os, sys, re, logging
import yaml
import urwid

from models.config import Config
from models.progress import Progress
from models.db.database import engine, session

# Get config
config_file_path = "config.yaml"

if len(sys.argv) > 1:  # If custom path provided for courses file
    config_file_path = sys.argv[1]

config = Config.from_file(config_file_path)

# Make Progress file
progress_file_path = os.path.join(os.getcwd(), "../progress.yaml")
progress = Progress.from_path_or_defaults(config.hash(), progress_file_path)
print(progress)