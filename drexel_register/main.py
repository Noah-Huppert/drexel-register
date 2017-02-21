import sys, re, logging
import yaml
import urwid

from models.config import Config

# Get config
config_file_path = "config.yaml"

if len(sys.argv) >= 2:  # If custom path provided for courses file
    config_file_path = sys.argv[1]

config = Config.from_file(config_file_path)

print(config)
