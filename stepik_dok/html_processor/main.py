import argparse
import os
import sys

from html_processor.config.loader import load_config
from html_processor.pipeline.runner import run_pipeline
from html_processor.utils.logger import log_info, log_error

def main():
    parser = argparse.ArgumentParser(description='HTML to PDF processor')
    parser.add_argument('config', help='Path to config JSON file')
    args = parser.parse_args()

    # Handle paths relative to the package when running as a module
    if args.config == 'config.json':
        package_dir = os.path.dirname(__file__)
        config_path = os.path.join(package_dir, args.config)
    else:
        config_path = args.config

    try:
        config = load_config(config_path)
        run_pipeline(config)
        log_info("Application finished successfully.")
    except Exception as e:
        log_error(f"Application failed: {e}")

if __name__ == "__main__":
    main()